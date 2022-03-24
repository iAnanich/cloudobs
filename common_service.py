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

app = Flask(__name__)
obs_server: server.Server = None
instance_service_addrs = util.ServiceAddrStorage()  # dict of `"lang": {"addr": "address", "init": True/False}


@app.route(API_INIT_ROUTE, methods=['POST'])
def init():
    """
    Query parameters:
    server_langs: json, dict of "lang": {"host_url": "base_url", "websocket_port": 1234, "password": "qwerty123", "original_media_url": "srt://localhost"}}
    e.g.: {"rus": {"host": "http://255.255.255.255:5000", "websocket_port": 1234, "password": "qwerty123", "original_media_url": "srt://localhost"}, "eng": ...}
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
            "init": False
        }
        lang_info.pop("host_url")
        # POST initialization for every instance service
        # for now every obs instance should be run locally with the instance service
        lang_info["obs_host"] = "localhost"
        lang_info = {lang: lang_info}

        query_params = urlencode({"server_langs": json.dumps(lang_info)})

        request_ = f"{instance_service_addrs[lang]}{API_INIT_ROUTE}/?{query_params}"
        response = requests.post(request_)

        if response.status_code != 200:
            msg_ = f"E PYSERVER::init(): couldn't initialize server for {lang}, details: {response.text}"
            print(msg_)
            status.append_error(msg_)

            instance_service_addrs[lang]["init"] = False
        else:
            instance_service_addrs[lang]["init"] = True

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
        if not instance_service_addrs[lang]['init']:
            continue

        query_params = urlencode({"name": name, "use_file_num": use_file_num})
        request_ = f"{instance_service_addrs[lang]['addr']}{API_MEDIA_PLAY_ROUTE}/?{query_params}"
        response = requests.post(request_)

        if response.status_code != 200:
            msg_ = f"E PYSERVER::media_play(): couldn't play media for {lang}, details: {response.text}"
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
