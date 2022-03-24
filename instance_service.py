import time
import json
import os
import obswebsocket as obsws
import obswebsocket.requests as obsrequests
import server
from flask import Flask
from flask import request
from dotenv import load_dotenv
import util
from util import ExecutionStatus

load_dotenv()

MEDIA_DIR = os.getenv('MEDIA_DIR')
API_INIT_ROUTE = os.getenv('API_INIT_ROUTE')
API_MEDIA_PLAY_ROUTE = os.getenv('API_MEDIA_PLAY_ROUTE')
API_SET_STREAM_SETTINGS_ROUTE = os.getenv('API_SET_STREAM_SETTINGS_ROUTE')
API_STREAM_START_ROUTE = os.getenv('API_STREAM_START_ROUTE')
API_STREAM_STOP_ROUTE = os.getenv('API_STREAM_START_ROUTE')

app = Flask(__name__)
obs_server: server.Server = None


@app.route(API_INIT_ROUTE, methods=['POST'])
def init():
    """
    Query parameters:
    server_langs: json, dict {"obs_host": "localhost", "websocket_port": 1234, "password": "qwerty123", "original_media_url": "srt://localhost"}
    :return:
    """
    server_langs = request.args.get('server_langs', '')
    server_langs = json.loads(server_langs)

    status: ExecutionStatus = util.validate_init_params(server_langs)
    if not status:
        return status.to_http_status()

    global obs_server
    obs_server = server.Server(server_langs=server_langs, base_media_path=MEDIA_DIR)
    status: ExecutionStatus = obs_server.initialize()

    return status.to_http_status()


@app.route(API_MEDIA_PLAY_ROUTE, methods=['POST'])
def media_play():
    """
    Query parameters:
    name: name of the video
    search_by_num: "1"/"0" (default "0"), points if need to search a file by first `n` numbers in name
    e.g.: 001_video_desc.mp4
    :return:
    """
    name = request.args.get('name', None)
    use_file_num = request.args.get('use_file_num', '0')

    status: ExecutionStatus = util.validate_media_play_params(name, use_file_num)
    if not status:
        return status.to_http_status()

    use_file_num = bool(int(use_file_num))
    status: ExecutionStatus = obs_server.run_media(name, use_file_num)

    return status.to_http_status()


@app.route(API_SET_STREAM_SETTINGS_ROUTE, methods=['POST'])
def set_stream_settings():
    """
    Query parameters:
    stream_settings: json dictionary,
    e.g. {"lang": {"server": "rtmp://...", "key": "..."}, ...}
    :return:
    """
    stream_settings = request.args.get('stream_settings', None)
    stream_settings = json.loads(stream_settings)

    status: ExecutionStatus = obs_server.set_stream_settings(stream_settings=stream_settings)

    return status.to_http_status()


@app.route(API_STREAM_START_ROUTE, methods=['POST'])
def stream_start():
    """
    Starts streaming on all machines
    :return:
    """
    status: ExecutionStatus = obs_server.start_streaming()

    return status.to_http_status()


@app.route(API_STREAM_STOP_ROUTE, methods=['POST'])
def stream_stop():
    """
    Stops streaming on all machines
    :return:
    """
    status: ExecutionStatus = obs_server.stop_streaming()

    return status.to_http_status()


if __name__ == '__main__':
    app.run('0.0.0.0', 6000)
