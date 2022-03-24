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
### `POST /media/play`
 - Plays the video specified in parameters
 - Accepts the following parameters:
   - `name` - name of the video
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`
### `POST /stream/settings`
 - Sets streaming destination settings
 - Accepts the following parameters:
   - `stream_settings` - json dictionary, e.g.:
    ```
    {"lang": {"server": "rtmp://...", "key": "..."}, ...}
    ```
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`
### `POST /stream/start`
 - Starts streaming
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`
### `POST /stream/stop`
 - Stops streaming
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`