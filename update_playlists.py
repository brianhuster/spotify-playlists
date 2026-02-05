#!/usr/bin/env python3
"""
Script to export Spotify playlists and liked songs to CSV files.
"""

import os
import sys
import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify API credentials from environment variables
CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.environ.get(
    'SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
REFRESH_TOKEN = os.environ.get('SPOTIFY_REFRESH_TOKEN')

# Configuration
PLAYLIST_IDS = os.environ.get('SPOTIFY_PLAYLIST_IDS', '').split(',')
PLAYLIST_IDS = [pid.strip() for pid in PLAYLIST_IDS if pid.strip()]


def get_spotify_client():
    """Initialize and return Spotify client with authentication."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError(
            "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set")

    # Use refresh token if available, otherwise use standard OAuth
    if REFRESH_TOKEN:
        auth_manager = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope='user-library-read playlist-read-private playlist-read-collaborative'
        )
        # Create token info from refresh token
        token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)
        sp = spotipy.Spotify(auth=token_info['access_token'])
    else:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope='user-library-read playlist-read-private playlist-read-collaborative'
        ))

    return sp


def export_tracks_to_csv(tracks, filename):
    """Export tracks to CSV file with Spotify's format."""
    fieldnames = [
        'Track URI', 'Track Name', 'Artist URI(s)', 'Artist Name(s)',
        'Album URI', 'Album Name', 'Album Artist URI(s)', 'Album Artist Name(s)',
        'Album Release Date', 'Album Image URL', 'Disc Number', 'Track Number',
        'Track Duration (ms)', 'Track Preview URL', 'Explicit', 'Popularity',
        'ISRC', 'Added By', 'Added At'
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in tracks:
            track = item.get('track')
            if not track:
                continue

            # Extract artist information
            artist_uris = ', '.join(
                [f"spotify:artist:{a['id']}" for a in track['artists']])
            artist_names = ', '.join([a['name'] for a in track['artists']])

            # Extract album artist information
            album_artist_uris = ', '.join(
                [f"spotify:artist:{a['id']}" for a in track['album']['artists']])
            album_artist_names = ', '.join(
                [a['name'] for a in track['album']['artists']])

            # Get album image URL
            album_image = track['album']['images'][0]['url'] if track['album']['images'] else ''

            row = {
                'Track URI': f"spotify:track:{track['id']}",
                'Track Name': track['name'],
                'Artist URI(s)': artist_uris,
                'Artist Name(s)': artist_names,
                'Album URI': f"spotify:album:{track['album']['id']}",
                'Album Name': track['album']['name'],
                'Album Artist URI(s)': album_artist_uris,
                'Album Artist Name(s)': album_artist_names,
                'Album Release Date': track['album']['release_date'],
                'Album Image URL': album_image,
                'Disc Number': track['disc_number'],
                'Track Number': track['track_number'],
                'Track Duration (ms)': track['duration_ms'],
                'Track Preview URL': track.get('preview_url', ''),
                'Explicit': str(track['explicit']).lower(),
                'Popularity': track['popularity'],
                'ISRC': track.get('external_ids', {}).get('isrc', ''),
                'Added By': item.get('added_by', {}).get('id', '') if 'added_by' in item else '',
                'Added At': item.get('added_at', '')
            }
            writer.writerow(row)

    print(f"✓ Exported {len(tracks)} tracks to {filename}")


def get_liked_songs(sp):
    """Fetch all liked songs from Spotify."""
    print("Fetching liked songs...")
    tracks = []
    results = sp.current_user_saved_tracks(limit=50)

    while results:
        tracks.extend(results['items'])
        if results['next']:
            results = sp.next(results)
        else:
            break

    print(f"✓ Found {len(tracks)} liked songs")
    return tracks


def get_playlist_tracks(sp, playlist_id):
    """Fetch all tracks from a specific playlist."""
    try:
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist['name']
        print(f"Fetching playlist: {playlist_name} ({playlist_id})...")

        tracks = []
        results = sp.playlist_tracks(playlist_id, limit=100)

        while results:
            tracks.extend(results['items'])
            if results['next']:
                results = sp.next(results)
            else:
                break

        print(f"✓ Found {len(tracks)} tracks in {playlist_name}")
        return tracks, playlist_name
    except Exception as e:
        print(f"✗ Error fetching playlist {playlist_id}: {e}")
        return None, None


def sanitize_filename(name):
    """Sanitize playlist name for use as filename."""
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    return name.strip()


def main():
    """Main function to export playlists."""
    try:
        # Initialize Spotify client
        sp = get_spotify_client()

        # Export liked songs
        print("\n" + "="*50)
        print("EXPORTING LIKED SONGS")
        print("="*50)
        liked_tracks = get_liked_songs(sp)
        export_tracks_to_csv(liked_tracks, 'liked.csv')

        # Export specific playlists
        if PLAYLIST_IDS:
            print("\n" + "="*50)
            print("EXPORTING PLAYLISTS")
            print("="*50)
            for playlist_id in PLAYLIST_IDS:
                tracks, playlist_name = get_playlist_tracks(sp, playlist_id)
                if tracks is not None:
                    filename = f"{sanitize_filename(playlist_name)}.csv"
                    export_tracks_to_csv(tracks, filename)

        print("\n" + "="*50)
        print("✓ ALL EXPORTS COMPLETED SUCCESSFULLY")
        print("="*50)

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
