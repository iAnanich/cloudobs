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
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`
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
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`
### `POST /stream/settings`
 - Sets streaming destination settings
 - Accepts the following parameters:
   - `stream_settings` - json dictionary, by-lang parameters, e.g.:
    ```
    {"lang": {"server": "rtmp://...", "key": "..."}, ...}
    ```
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`
### `POST /stream/start`
 - Starts streaming for all machines
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`
### `POST /stream/stop`
 - Stops streaming for all machines
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`
### `POST /ts/offset`
 - Sets teamspeak sound offset (in milliseconds)
 - Accepts the following parameters:
   - `offset_settings` - json dictionary, by-lang parameters, e.g.:
    ```
    {"lang": 4000, ...}
    ```
 - Note: in this route you may specify one offset for every language
   just passing `__all__` as a lang code, e.g.: `{"__all__": 4000}`
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`