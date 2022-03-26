import time
import json
import os
import obswebsocket as obsws
import obswebsocket.requests as obsrequests
import requests as requests
import server
from flask import Flask
from flask import request
from dotenv import load_dotenv
from urllib.parse import urlencode
import util
from util import ExecutionStatus

load_dotenv()

MEDIA_DIR = os.getenv('MEDIA_DIR')
API_INIT_ROUTE = os.getenv('API_INIT_ROUTE')
API_MEDIA_PLAY_ROUTE = os.getenv('API_MEDIA_PLAY_ROUTE')
API_SET_STREAM_SETTINGS_ROUTE = os.getenv('API_SET_STREAM_SETTINGS_ROUTE')
API_STREAM_START_ROUTE = os.getenv('API_STREAM_START_ROUTE')
API_STREAM_STOP_ROUTE = os.getenv('API_STREAM_STOP_ROUTE')
API_CLEANUP_ROUTE = os.getenv('API_CLEANUP_ROUTE')

app = Flask(__name__)
obs_server: server.Server = None
instance_service_addrs = util.ServiceAddrStorage()  # dict of `"lang": {"addr": "address"}


@app.route(API_INIT_ROUTE, methods=['POST'])
def init():
    """
    Query parameters:
    server_langs: json, dict of "lang": {"host_url": "base_url", "websocket_port": 1234, "password": "qwerty123", "original_media_url": "srt://localhost"}}
    e.g.: {"rus": {"host_url": "http://255.255.255.255:5000", "websocket_port": 1234, "password": "qwerty123", "original_media_url": "srt://localhost"}, "eng": ...}
    :return:
    """
    server_langs = request.args.get('server_langs', '')
    server_langs = json.loads(server_langs)

    # validate input parameters before broadcasting them to servers
    status: ExecutionStatus = util.validate_init_params(server_langs)
    if not status:
        return status.to_http_status()

    status = ExecutionStatus(status=True)

    # in the following loop we build `server_lang` parameters for each lang and
    # broadcast request for all servers
    global instance_service_addrs  # dict of `"lang": {"addr": "address", "init": True/False}
    for lang, lang_info in server_langs.items():
        # fill `instance_service_addrs`
        instance_service_addrs[lang] = {
            "addr": lang_info["host_url"].strip('/'),
        }
        lang_info.pop("host_url")
        # POST initialization for every instance service
        # for now every obs instance should be run locally with the instance service
        lang_info["obs_host"] = "localhost"
        lang_info = {lang: lang_info}

        query_params = urlencode({"server_langs": json.dumps(lang_info)})

        request_ = f"{instance_service_addrs[lang]['addr']}{API_INIT_ROUTE}?{query_params}"
        response = requests.post(request_)

        if response.status_code != 200:
            msg_ = f"E PYSERVER::init(): couldn't initialize server for {lang}, details: {response.text}"
            print(msg_)
            status.append_error(msg_)

    return status.to_http_status()


@app.route(API_CLEANUP_ROUTE, methods=['POST'])
def cleanup():
    """
    :return:
    """
    status = ExecutionStatus(status=True)

    # broadcast request for all lang servers
    for lang in instance_service_addrs:
        request_ = f"{instance_service_addrs[lang]['addr']}{API_CLEANUP_ROUTE}"
        response = requests.post(request_)

        if response.status_code != 200:
            msg_ = f"E PYSERVER::cleanup(): couldn't cleanup server for {lang}, details: {response.text}"
            print(msg_)
            status.append_error(msg_)

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

    status = ExecutionStatus(status=True)

    # broadcast request for all lang servers
    for lang in instance_service_addrs:
        query_params = urlencode({"name": name, "use_file_num": use_file_num})
        request_ = f"{instance_service_addrs[lang]['addr']}{API_MEDIA_PLAY_ROUTE}?{query_params}"
        response = requests.post(request_)

        if response.status_code != 200:
            msg_ = f"E PYSERVER::media_play(): couldn't play media for {lang}, details: {response.text}"
            print(msg_)
            status.append_error(msg_)

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

    status = ExecutionStatus(status=True)
    for lang in stream_settings:
        stream_settings_ = stream_settings[lang]
        if 'key' not in stream_settings_ or 'server' not in stream_settings_:
            return status.append_error("Please specify both `server` and `key` attributes")
    if not status:
        return status.to_http_status()

    status = ExecutionStatus(status=True)

    # broadcast request for all lang servers
    for lang in stream_settings:
        params_ = {lang: stream_settings[lang]}
        query_params = urlencode({'stream_settings': json.dumps(params_)})
        request_ = f"{instance_service_addrs[lang]['addr']}{API_SET_STREAM_SETTINGS_ROUTE}?{query_params}"
        response = requests.post(request_)

        if response.status_code != 200:
            msg_ = f"E PYSERVER::set_stream_settings(): couldn't set stream settings for {lang}, details: {response.text}"
            print(msg_)
            status.append_error(msg_)

    return status.to_http_status()


@app.route(API_STREAM_START_ROUTE, methods=['POST'])
def stream_start():
    """
    Starts streaming on all machines
    :return:
    """
    status = ExecutionStatus(status=True)

    # broadcast request for all lang servers
    for lang in instance_service_addrs:
        request_ = f"{instance_service_addrs[lang]['addr']}{API_STREAM_START_ROUTE}"
        response = requests.post(request_)

        if response.status_code != 200:
            msg_ = f"E PYSERVER::stream_start(): couldn't start streaming for {lang}, details: {response.text}"
            print(msg_)
            status.append_error(msg_)

    return status.to_http_status()


@app.route(API_STREAM_STOP_ROUTE, methods=['POST'])
def stream_stop():
    """
    Stops streaming on all machines
    :return:
    """
    status = ExecutionStatus(status=True)

    # broadcast request for all lang servers
    for lang in instance_service_addrs:
        request_ = f"{instance_service_addrs[lang]['addr']}{API_STREAM_STOP_ROUTE}"
        response = requests.post(request_)

        if response.status_code != 200:
            msg_ = f"E PYSERVER::stream_stop(): couldn't stop streaming for {lang}, details: {response.text}"
            print(msg_)
            status.append_error(msg_)

    return status.to_http_status()


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)

# ==================================== FOR TESTING
# client = obswebsocket.obsws("localhost", 4441)
# # client.register(on_event)
# client.connect()
#
# # client.call(obswebsocket.requests.GetVersion()).getObsWebsocketVersion()
# client.call(obswebsocket.requests.GetSourcesList()).getSources()
# client.call(obswebsocket.requests.GetSourceSettings('original_media')).getSourceSettings()
# obswebsocket.requests.CreateSource(sourceName='name', sourceKind='', sceneName='', sourceSettings='')
# client.call(obswebsocket.requests.GetSceneList()).getScenes()
#
# client.call(obswebsocket.requests.GetMute('original_stream')).getMuted()
# client.call(obswebsocket.requests.GetAudioMonitorType('original_stream')).getMonitorType()  # none, monitorOnly, monitorAndOutput
# client.call(obswebsocket.requests.SetAudioMonitorType(sourceName='original_stream', monitorType='none'))
#
# '''
# {'input': 'rtmp://nsk-2.facecast.io/re/861424dbf89b93e52333',
#  'is_local_file': False}
#  '''
# items = client.call(obswebsocket.requests.GetSceneItemList(sceneName='main_1')).getSceneItems()
# for item in items:
#     print(item)
#     client.call(obswebsocket.requests.DeleteSceneItem(item=item))
#
#
# try:
#     time.sleep(100)
#
# except KeyboardInterrupt:
#     pass
#
# client.disconnect()
# obswebsocket.requests.GetSourceSettings
