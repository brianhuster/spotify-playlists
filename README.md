# Spotify Playlists Auto-Update

Tự động cập nhật các danh sách phát Spotify vào file CSV sử dụng GitHub Actions.

## Tính năng

- Tự động export liked songs (bài hát đã thích) sang file CSV
- Tự động export các playlist cụ thể sang file CSV
- Chạy tự động hàng ngày lúc 00:00 UTC
- Có thể chạy thủ công qua GitHub Actions
- Tự động commit và push các thay đổi

## Cấu hình

### 1. Tạo Spotify App

1. Truy cập [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Đăng nhập và tạo một app mới
3. Lưu lại `Client ID` và `Client Secret`
4. Trong phần Settings, thêm Redirect URI: `http://localhost:8888/callback`

### 2. Lấy Refresh Token

Chạy script sau để lấy refresh token:

```bash
pip install spotipy
python -c "
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    redirect_uri='http://localhost:8888/callback',
    scope='user-library-read playlist-read-private playlist-read-collaborative'
))

# Lệnh này sẽ mở browser để authorize
user = sp.current_user()
print('User:', user['display_name'])

# Lấy refresh token
auth_manager = sp.auth_manager
token_info = auth_manager.get_cached_token()
print('Refresh Token:', token_info['refresh_token'])
"
```

Thay `YOUR_CLIENT_ID` và `YOUR_CLIENT_SECRET` bằng thông tin của bạn.

### 3. Cấu hình GitHub Secrets

Vào repository Settings > Secrets and variables > Actions, thêm các secrets sau:

- `SPOTIFY_CLIENT_ID`: Client ID từ Spotify App
- `SPOTIFY_CLIENT_SECRET`: Client Secret từ Spotify App
- `SPOTIFY_REFRESH_TOKEN`: Refresh token lấy được từ bước 2
- `SPOTIFY_PLAYLIST_IDS`: (Optional) Danh sách playlist IDs cách nhau bởi dấu phẩy
  - Ví dụ: `37i9dQZF1DXcBWIGoYBM5M,3cEYpjA9oz9GiPac4AsH4n`
  - Để lấy playlist ID, copy link playlist và lấy phần sau `/playlist/`

### 4. Bật GitHub Actions

Workflow sẽ tự động chạy:
- Hàng ngày lúc 00:00 UTC
- Khi có thay đổi trong `update_playlists.py` hoặc workflow file
- Hoặc chạy thủ công qua tab Actions > Update Spotify Playlists > Run workflow

## Cấu trúc file

```
.
├── .github/
│   └── workflows/
│       └── update-playlists.yml    # GitHub Actions workflow
├── update_playlists.py              # Script Python để fetch data
├── requirements.txt                 # Python dependencies
├── liked.csv                        # Bài hát đã thích
└── [tên-playlist].csv              # Các playlist khác
```

## Format CSV

File CSV được export theo format của Spotify với các trường:
- Track URI, Track Name
- Artist URI(s), Artist Name(s)
- Album URI, Album Name
- Album Artist URI(s), Album Artist Name(s)
- Album Release Date, Album Image URL
- Disc Number, Track Number
- Track Duration (ms), Track Preview URL
- Explicit, Popularity, ISRC
- Added By, Added At

## Chạy local

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Export environment variables
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
export SPOTIFY_REFRESH_TOKEN="your_refresh_token"
export SPOTIFY_PLAYLIST_IDS="playlist_id_1,playlist_id_2"

# Chạy script
python update_playlists.py
```

## Troubleshooting

### Token hết hạn
Nếu refresh token hết hạn, bạn cần lấy lại token mới bằng cách chạy lại bước 2.

### Playlist không được export
Kiểm tra:
- Playlist ID có đúng không
- Playlist có public hoặc bạn có quyền truy cập không
- Token có scope đủ quyền không

### Workflow không chạy
Kiểm tra:
- Tất cả secrets đã được cấu hình chưa
- Repository có bật Actions không
- Workflow file có syntax đúng không (check tab Actions)

## License

MIT
