import time
import re

import obswebsocket
import obswebsocket.requests
from obswebsocket import events

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from flask import Flask
from flask import request

app = Flask(__name__)

def on_event(message):
    print(u"Got message: {}".format(message))

@app.route('/init', methods=['POST'])
def init():
    """
    Query parameters:
    server_langs: list of lang|obs_host|websocket_port|original_media_url,
                  separated by ";". For example "rus|localhost|4440|rtmp://X.X.X.X/rtmp/stream;eng|localhost|4441|srt://X.X.X.X:..."
    :return:
    """
    server_langs = request.args.get('server_langs', '')
    # TODO: separate method to parse `server_langs`
    server_langs = server_langs.split(';')
    server_langs = [re.search(r'(?P<lang>[a-zA-Z]+)\|'
                              r'(?P<obs_host>.+)\|'
                              r'(?P<websocket_port>\d+)\|'
                              r'(?P<original_media_url>[^\;\|]+)\|', x) for x in server_langs]


    server_langs = [(
        x['lang'],
        x['obs_host'],
        x['websocket_port'],
        x['original_media_url'],
    ) for x in server_langs]  # list of (lang, obs_host, websocket_port, original_media_url)

# ==================================== FOR TESTING
client = obswebsocket.obsws("localhost", 4444)
# client.register(on_event)
client.connect()

# client.call(obswebsocket.requests.GetVersion()).getObsWebsocketVersion()
client.call(obswebsocket.requests.GetSourcesList()).getSources()
client.call(obswebsocket.requests.GetSourceSettings('original_media')).getSourceSettings()
obswebsocket.requests.CreateSource(sourceName='name', sourceKing='', sceneName='', sourceSettings='')
client.call(obswebsocket.requests.GetSceneList()).getScenes()

'''
{'input': 'rtmp://nsk-2.facecast.io/re/861424dbf89b93e52333',
 'is_local_file': False}
 '''
items = client.call(obswebsocket.requests.GetSceneItemList(sceneName='main_1')).getSceneItems()
for item in items:
    print(item)
    client.call(obswebsocket.requests.DeleteSceneItem(item=item))


try:
    time.sleep(100)

except KeyboardInterrupt:
    pass

client.disconnect()
obswebsocket.requests.GetSourceSettings