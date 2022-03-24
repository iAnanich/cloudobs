### `/init`
 - Initializes the server
 - Accepts the following parameters:
   - `server_langs` -
    json, dict of 
     ```
     "lang": {
        "obs_host": "localhost", 
        "websocket_port": 1234, 
        "password": "qwerty123", 
        "original_media_url": "srt://localhost"} 
     }
     ```
 - Returns `(200, "Ok")` on success, otherwise `(500, "error details")`
### `/media/play`
 - Plays the video specified in parameters
 - Accepts the following parameters:
   - `name` - name of the video