import numpy as np
import obswebsocket as obsws
import obs
import obswebsocket.requests as obs_requests
from obswebsocket import events


class Server:
    def __init__(self, server_langs):
        """
        :param server_langs: dict of "lang": {"obs_host": "localhost", "websocket_port": 1234, "password": "qwerty123", "original_media_url": "srt://localhost"}}
        :return:
        """
        self.server_langs = server_langs
        self.obs_instances = None  # {..., "lang": obs.OBS(), ...}
        self.is_initialized = False

    def put_video(self, name):
        if not self.is_initialized:
            raise
        for lang, obs_ in self.obs_instances.items():
            pass

    def drop_connections(self):
        for lang, client in self.obs_instances.items():
            try:
                client.disconnect()
            except:
                pass

    def _establish_connections(self):
        """
        establish connections
        :return: True/False
        """
        # create obs ws clients
        self.obs_instances = {
            lang: obsws.obsws(host=lang_info['obs_host'], port=int(lang_info['websocket_port']))
            for lang, lang_info in self.server_langs.items()
        }
        # establish connections
        for lang, client in self.obs_instances.items():
            # if couldn't establish a connection
            try:
                client.connect()
            except BaseException as ex:
                return False, f"E PYSERVER::Server::_establish_connections(): Couldn't connect to obs server. " \
                              f"Lang '{lang}', " \
                              f"host '{self.server_langs[lang]['obs_host']}', " \
                              f"port {self.server_langs[lang]['websocket_port']}. Details: {ex}"

        return True, ''

    def _initialize_obs_controllers(self):
        # create obs controller instances
        self.obs_instances = {
            lang: obs.OBS(lang, client)
            for lang, client in self.obs_instances.items()
        }
        # reset scenes, create original media sources
        for lang, obs_ in self.obs_instances.items():
            try:
                obs_.clear_all_scenes()
                obs_.setup_scene(scene_name=obs.MAIN_SCENE_NAME)
                obs_.set_original_media_source(scene_name=obs.MAIN_SCENE_NAME,
                                               original_media_source=self.server_langs[lang]['original_media_url'])
            except BaseException as ex:
                return False, f"E PYSERVER::Server::_initialize_obs_controllers(): Couldn't initialize obs controller. " \
                              f"Lang: '{lang}', " \
                              f"host '{self.server_langs[lang]['obs_host']}', " \
                              f"port {self.server_langs[lang]['websocket_port']}. Details: {ex}"

        return True, ''

    def initialize(self):
        """
        establish connections, initialize obs controllers, setup scenes, create original media sources
        :return: True/False, error message
        """
        status, err_msg = self._establish_connections()
        if not status:
            self.drop_connections()
            return status, err_msg
        status, err_msg = self._initialize_obs_controllers()
        if not status:
            self.drop_connections()
            return status, err_msg
        return status, ''
