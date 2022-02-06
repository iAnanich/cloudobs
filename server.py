import numpy as np
import obswebsocket as obs
import obswebsocket.requests as obs_requests
from obswebsocket import events

class Server:
    def __init__(self, restreams):
        """
        :param restreams: list of (lang, obs_host, websocket_port, original_media_url)
        :return:
        """

        # assertions to make sure all parameters are passed properly
        values, counts = np.unique([x[0] for x in restreams], return_counts=True)
        for lang, cnt in zip(values, counts):
            assert cnt == 1, f'E PYSERVER::Server::init(): each lang should be unique in `restreams` list. ' \
                             f'Lang {lang} contains {cnt} entries'
        for i, x in enumerate(restreams):
            assert len(x) == 4, f'E PYSERVER:Server::init(): each restream info in `restreams` list should contain four elements. ' \
                                f'Element {i} contains {len(x)} elements: {x}'

        self.restreams = restreams  # [... [lang, obs_host, websocket_port, original_media_url], ...]
        self.obs_clients = {
            lang: None
            for lang, _, _, _ in restreams
        }  # lang: info

    def _establish_connections(self):
        """
        establish connections
        :return:
        """
        for lang, obs_host, websocket_port, _ in self.restreams:
            client = obs.obsws(obs_host, int(websocket_port))
            try:
                client.connect()
            except obs.core.exceptions.ConnectionFailure as exception:
                print(f"E PYSERVER::Server::initialize(): couldn't connect to {obs_host}:{websocket_port}")
                raise exception
            self.obs_clients[lang] = client
        print(f"I PYSERVER::Server::initialize(): connections are successfully established")

    def initialize(self):
        """
        establish connections, ...
        :return:
        """
        self._establish_connections()
