### `POST /init`
 - Initializes the server
 - Accepts the following parameters:
   - `server_langs` -
    json, dict of 
     ```
     "lang": {
        "host_url": "localhost", 
        "websocket_port": 1234, 
        "password": "qwerty123", 
        "original_media_url": "srt://localhost"} 
     }
     ```
 - Returns `("Ok", 200)` on success, otherwise `("error details", 500)`
### `POST /cleanup`
 - Cleans up the server: stop streaming -> reset scenes -> close connections
### `POST /media/play`
 - Plays the video specified in parameters
 - Accepts the following parameters:
   - `name` - name of the video
   - `search_by_num` - `1`/`0` (defaults to `0`), if `1`
     points the server needs to search a file by first `n` numbers in name,
     for example if `name="001_test.mp4"`, the server will search for a file
     which full name even does not match with `001_test.mp4`, but it's name starts with
     `001`, it may be `001_test2.mp4`, `001.mp4`, etc.
 - Returns `("Ok", 200)` on success, otherwise `("error details", 500)`
### `POST /stream/settings`
 - Sets streaming destination settings
 - Accepts the following parameters:
   - `stream_settings` - json dictionary, by-lang parameters, e.g.:
    ```
    {"lang": {"server": "rtmp://...", "key": "..."}, ...}
    ```
 - Returns `("Ok", 200)` on success, otherwise `("error details", 500)`
### `POST /stream/start`
 - Starts streaming for all machines
 - Returns `("Ok", 200)` on success, otherwise `("error details", 500)`
### `POST /stream/stop`
 - Stops streaming for all machines
 - Returns `("Ok", 200)` on success, otherwise `("error details", 500)`
### `POST /ts/offset`
 - Sets teamspeak sound offset (in milliseconds)
 - Accepts the following parameters:
   - `offset_settings` - json dictionary, by-lang parameters, e.g.:
    ```
    {"lang": offset, ...}
    ```
 - Note: you may specify one offset for all languages,
   passing `__all__` as a lang code, e.g.: `{"__all__": offset}`
 - Returns `("Ok", 200)` on success, otherwise `("error details", 500)`
### `GET /ts/offset`
 - Returns current teamspeak sound offset (in milliseconds)
 - Has the following structure:
   ```
   {"lang": offset, ...}
   ```
 - Returns ("data", 200)
### `POST /ts/volume`
 - Sets teamspeak sound volume (in decibels)
 - Accepts the following parameters:
   - `volume_settings` - json dictionary, by-lang parameters, e.g.:
    ```
    {"lang": volume, ...}
    ```
 - Note: you may specify one volume for all languages,
   passing `__all__` as a lang code, e.g.: `{"__all__": volume}`
 - Returns `("Ok", 200)` on success, otherwise `("error details", 500)`
### `GET /ts/volume`
 - Returns current teamspeak volume (in decibels)
 - Has the following structure:
   ```
   {"lang": volume, ...}
   ```
 - Returns ("data", 200)
### `POST /source/volume`
 - Sets original source sound volume (in decibels)
 - Accepts the following parameters:
   - `volume_settings` - json dictionary, by-lang parameters, e.g.:
    ```
    {"lang": volume, ...}
    ```
 - Note: you may specify one volume for all languages,
   passing `__all__` as a lang code, e.g.: `{"__all__": volume}`
 - Returns `("Ok", 200)` on success, otherwise `("error details", 500)`
### `GET /source/volume`
 - Returns current original source volume (in decibels)
 - Has the following structure:
   ```
   {"lang": volume, ...}
   ```
 - Returns ("data", 200)
### `POST /filters/sidechain`
 - Sets up sidechain
 - Accepts the following parameters:
   - `sidechain_settings` - json dictionary, by-lang parameters, e.g.:
    ```
    {"lang": {'ratio': ..., 'release_time': ..., 'threshold': ...}, ...}
    ```
 - Note: you are not required to provide all sidechain params (ratio, release_time, ...).
   If some are not provided, default values will be used.
 - Note: you may specify sidechain settings for all languages,
   passing `__all__` as a lang code, e.g.: `{"__all__": volume}`
 - Returns `("Ok", 200)` on success, otherwise `("error details", 500)`
