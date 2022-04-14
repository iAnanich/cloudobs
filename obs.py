import os
import obswebsocket as obs
import obswebsocket.requests as obs_requests

ORIGINAL_STREAM_SOURCE_NAME = 'original_stream'
MAIN_SCENE_NAME = 'main'
MEDIA_SCENE_NAME = 'media'
TS_INPUT_NAME = 'ts_input'
COMPRESSOR_FILTER_NAME = 'sidechain'


def create_event_handler(obs_instance):
    def foo(message):
        obs_instance.on_event(message)

    return foo


class OBS:
    def __init__(self, lang, client):
        self.lang = lang
        self.client = client
        self.original_media_source = None
        self.media_queue = []
        self.callback_queue = []

        self.client.register(create_event_handler(self))

    def set_original_media_source(self, scene_name, original_media_source):
        """
        Adds an original media source
        :param scene_name: scene to add an input
        :param original_media_source: url like 'protocol://address[:port][/path][...]', may be rtmp, srt
        """
        self.original_media_source = original_media_source

        source_settings = {
            'input': original_media_source,
            'is_local_file': False,
        }
        request = obs.requests.CreateSource(
            sourceName=ORIGINAL_STREAM_SOURCE_NAME,
            sourceKind='ffmpeg_source',
            sceneName=scene_name,
            sourceSettings=source_settings
        )
        response = self.client.call(request)

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::add_original_media_source(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

        request = obs.requests.SetAudioMonitorType(
            sourceName=ORIGINAL_STREAM_SOURCE_NAME, monitorType='none'
        )
        response = self.client.call(request)

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::add_original_media_source(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

    def setup_scene(self, scene_name='main', switch_scene=True):
        """
        Creates (if not been created) a scene called `scene_name` and sets it as a current scene.
        If it has been created, removes all the sources inside the scene and sets it as a current one.
        """
        scenes = self.client.call(
            obs.requests.GetSceneList()).getScenes()  # [... {'name': '...', 'sources': [...]}, ...]

        # if such scene has already been created
        if any([x['name'] == scene_name for x in scenes]):
            self.clear_scene(scene_name)
        else:
            self.create_scene(scene_name)

        if switch_scene:
            self.set_current_scene(scene_name)

    def clear_all_scenes(self):
        """
        Lists all the scenes and removes all the scene items.
        """
        scenes = self.obsws_get_scene_list()
        for scene_info in scenes:
            scene_name = scene_info['name']
            self.clear_scene(scene_name)

    def clear_scene(self, scene_name):
        """
        Removes all the items from a specified scene
        """
        items = self.obsws_get_scene_item_list(scene_name=scene_name)
        items = [{'id': item['itemId'], 'name': item['sourceName']} for item in items]
        for item in items:
            response = self.client.call(obs.requests.DeleteSceneItem(scene=scene_name, item=item))
            if not response.status:  # if not deleted
                raise Exception(
                    f"E PYSERVER::OBS::clear_scene(): "
                    f"datain: {response.datain}, dataout: {response.dataout}")

    def set_current_scene(self, scene_name):
        """
        Switches current scene to `scene_name`
        """
        self.client.call(obs.requests.SetCurrentScene(scene_name=scene_name))

    def create_scene(self, scene_name):
        """
        Creates a scene with name `scene_name`
        """
        self.client.call(obs.requests.CreateScene(sceneName=scene_name))

    def run_media(self, path):
        """
        Mutes original media, adds and runs the media located at `path`, and appends a listener which removes
        the media when it has finished. Fires Exception when couldn't add or mute a source.
        """
        filename = os.path.basename(path)
        self.setup_scene(scene_name=MEDIA_SCENE_NAME, switch_scene=False)
        # scene_name = self.obsws_get_current_scene_name()

        response = self.client.call(obs.requests.CreateSource(
            sourceName=filename,
            sourceKind='ffmpeg_source',
            sceneName=MEDIA_SCENE_NAME,
            sourceSettings={'local_file': path}
        ))

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::run_media(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

        self.media_queue.append(filename)

        response = self.client.call(obs.requests.SetCurrentScene(scene_name=MEDIA_SCENE_NAME))
        # response = self.client.call(obs.requests.SetMute(source=ORIGINAL_STREAM_SOURCE_NAME, mute=True))
        if not response.status:
            raise Exception(f"E PYSERVER::OBS::run_media(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

    def setup_ts_sound(self):
        """
        Adds/Resets teamspeak audio input (default device).
        """

        current_scene = self.obsws_get_current_scene_name()
        items = [{'id': item['itemId'], 'name': item['sourceName']}
                 for item in self.obsws_get_scene_item_list(scene_name=current_scene)
                 if item['sourceName'] == TS_INPUT_NAME]

        for item in items:
            response = self.client.call(obs.requests.DeleteSceneItem(scene=current_scene, item=item))
            if not response.status:  # if not deleted
                raise Exception(
                    f"E PYSERVER::OBS::setup_ts_sound(): "
                    f"datain: {response.datain}, dataout: {response.dataout}")

        response = self.client.call(obs.requests.CreateSource(
            sourceName=TS_INPUT_NAME,
            sourceKind='pulse_output_capture',
            sceneName=current_scene,
        ))

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::setup_ts_sound(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

    def setup_transition(self, transition_name="Cut", transition_settings=None):
        """
        :param transition_name: transition name, e.g. "Cut" or "Stinger"
        :param transition_settings:
        e.g.:
        {'audio_fade_style': 1,
         'audio_monitoring': 1,
         'hw_decode': True,
         'invert_matte': False,
         'path': '/home/user/common/_Sting_RT.mp4',
         'tp_type': 0,
         'track_matte_enabled': False,
         'transition_point': 3000}
        :return:
        """
        if transition_name == "Stinger":
            if "audio_fade_style" not in transition_settings:
                transition_settings["audio_fade_style"] = 1
            if "audio_monitoring" not in transition_settings:
                transition_settings["audio_monitoring"] = 1
            if "invert_matte" not in transition_settings:
                transition_settings["invert_matte"] = False
            if "tp_type" not in transition_settings:
                transition_settings["tp_type"] = 0
            if "track_matte_enabled" not in transition_settings:
                transition_settings["track_matte_enabled"] = False
            if "transition_point" not in transition_settings:
                transition_settings["transition_point"] = 3000

        response = self.client.call(obs.requests.SetTransitionSettings(
            transitionName=transition_name,
            transitionSettings=transition_settings,
        ))

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::setup_transition(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

        response = self.client.call(obs.requests.SetCurrentTransition(
            transition_name=transition_name
        ))

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::setup_transition(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

    def get_ts_sync_offset(self):
        """
        Retrieves teamspeak sound sync offset
        :return:
        """
        response = self.client.call(obs.requests.GetSyncOffset(source=TS_INPUT_NAME))

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::get_ts_sync_offset(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

        return response.getOffset() // 1_000_000

    def set_ts_sync_offset(self, offset):
        """
        Sets teamspeak sound ('ts_input' source) sync offset
        :return:
        """
        response = self.client.call(obs.requests.SetSyncOffset(
            source=TS_INPUT_NAME,
            offset=offset * 1_000_000,  # convert to nanoseconds (refer to documentation)
        ))

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::set_ts_sync_offset(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

    def get_ts_volume_db(self):
        """
        Retrieves teamspeak sound volume (in decibels)
        :return:
        """
        response = self.client.call(obs.requests.GetVolume(source=TS_INPUT_NAME, useDecibel=True))

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::get_ts_volume_db(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

        return response.getVolume()

    def set_ts_volume_db(self, volume_db):
        """
        Sets teamspeak sound volume (in decibels)
        :param volume_db:
        :return:
        """
        response = self.client.call(obs.requests.SetVolume(source=TS_INPUT_NAME, volume=volume_db, useDecibel=True))

        if not response.status:
            raise RuntimeError(f"E PYSERVER::OBS::set_ts_volume_db(): "
                               f"datain: {response.datain}, dataout: {response.dataout}")

    def get_source_volume_db(self):
        """
        Retrieves original source sound volume (in decibels)
        :return:
        """
        response = self.client.call(obs.requests.GetVolume(source=ORIGINAL_STREAM_SOURCE_NAME, useDecibel=True))

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::get_source_volume_db(): "
                            f"datain: {response.datain}, dataout: {response.dataout}")

        return response.getVolume()

    def set_source_volume_db(self, volume_db):
        """
        Sets original source sound volume (in decibels)
        :param volume_db:
        :return:
        """
        response = self.client.call(
            obs.requests.SetVolume(source=ORIGINAL_STREAM_SOURCE_NAME, volume=volume_db, useDecibel=True))

        if not response.status:
            raise RuntimeError(f"E PYSERVER::OBS::set_source_volume_db(): "
                               f"datain: {response.datain}, dataout: {response.dataout}")

    def setup_sidechain(self, ratio=None, release_time=None, threshold=None):
        """
        [{'enabled': True,
          'name': 'sidechain',
          'settings': {'ratio': 15.0,
           'release_time': 1000,
           'sidechain_source': 'Mic/Aux',
           'threshold': -29.2},
          'type': 'compressor_filter'}]
        """
        response = self.client.call(obs.requests.GetSourceFilters(sourceName=ORIGINAL_STREAM_SOURCE_NAME))

        if not response.status:
            raise RuntimeError(f"E PYSERVER::OBS::setup_sidechain(): "
                               f"datain: {response.datain}, dataout: {response.dataout}")

        filters = response.getFilters()  # [... {'enabled': ..., 'name': ..., 'settings': ..., 'type': ...} ...]

        sourceName = ORIGINAL_STREAM_SOURCE_NAME
        filterName = COMPRESSOR_FILTER_NAME
        filterType = 'compressor_filter'
        filterSettings = {
            'sidechain_source': TS_INPUT_NAME,
        }
        if ratio is not None:
            filterSettings['ratio'] = ratio
        if release_time is not None:
            filterSettings['release_time'] = release_time
        if threshold is not None:
            filterSettings['threshold'] = threshold

        if all([f['name'] != COMPRESSOR_FILTER_NAME for f in filters]):  # if no compressor input added before
            response = self.client.call(obs.requests.AddFilterToSource(
                sourceName=sourceName, filterName=filterName, filterType=filterType, filterSettings=filterSettings,
            ))
            if not response.status:
                raise RuntimeError(f"E PYSERVER::OBS::setup_sidechain(): "
                                   f"datain: {response.datain}, dataout: {response.dataout}")
        else:  # if compressor was already added before
            response = self.client.call(obs.requests.SetSourceFilterSettings(
                sourceName=sourceName, filterName=filterName, filterSettings=filterSettings,
            ))
            if not response.status:
                raise RuntimeError(f"E PYSERVER::OBS::setup_sidechain(): "
                                   f"datain: {response.datain}, dataout: {response.dataout}")

    def set_stream_settings(self, server, key, type="rtmp_custom"):
        """
        Sets the streaming settings of the server
        """
        # TODO: validate server and key
        settings_ = {
            'server': server,
            'key': key
        }

        response = self.client.call(obs.requests.SetStreamSettings(type=type, settings=settings_, save=True))
        if not response.status:
            raise Exception(f"E PYSERVER::OBS::set_stream_settings(): "
                            f"lang: {self.lang}, datain: {response.datain}, dataout: {response.dataout}")

    def start_streaming(self):
        """
        Starts the streaming
        """
        response = self.client.call(obs.requests.StartStreaming())
        if not response.status:
            raise Exception(f"E PYSERVER::OBS::start_streaming(): "
                            f"lang: {self.lang}, datain: {response.datain}, dataout: {response.dataout}")

    def stop_streaming(self):
        """
        Starts the streaming
        """
        response = self.client.call(obs.requests.StopStreaming())
        if not response.status:
            raise Exception(f"E PYSERVER::OBS::stop_streaming(): "
                            f"lang: {self.lang}, datain: {response.datain}, dataout: {response.dataout}")

    def on_event(self, message):
        # we handle the error here for the reason of this function is called from another thread
        # from obs-websocket-py library, and I am not sure of the exception will be handled properly there
        try:
            if message.name == 'MediaEnded':
                self.on_media_ended(message)
        except BaseException as ex:
            print(f"E PYSERVER::OBS::on_event(): {ex}")

    def on_media_ended(self, message):
        """
        Fired on event MediaEnded. Fires Exception if could't delete a scene item or unmute a source
        """
        source_name = message.getSourceName()

        if source_name in self.media_queue and \
                self.obsws_get_current_scene_name() == MEDIA_SCENE_NAME:
            response = self.client.call(obs.requests.SetCurrentScene(scene_name=MAIN_SCENE_NAME))
            if not response.status:
                raise Exception(f"E PYSERVER::OBS::on_media_ended(): "
                                f"datain: {response.datain}, dataout: {response.dataout}")

    def obsws_get_current_scene_name(self):
        return self.client.call(obs.requests.GetCurrentScene()).getName()

    def obsws_get_sources_list(self):
        """
        :return: list of [... {'name': '...', 'type': '...', 'typeId': '...'}, ...]
        """
        return self.client.call(obs.requests.GetSourcesList()).getSources()

    def obsws_get_scene_list(self):
        """
        :return: list of [... {'name': '...', 'sources': [{..., 'id': n, ..., 'name': '...', ...}, ...]}, ...]
        """
        return self.client.call(obs.requests.GetSceneList()).getScenes()

    def obsws_get_scene_item_list(self, scene_name):
        """
        :param scene_name: name of the scene
        :return: list of [... {'itemId': n, 'sourceKind': '...', 'sourceName': '...', 'sourceType': '...'}, ...]
        """
        return self.client.call(obs.requests.GetSceneItemList(sceneName=scene_name)).getSceneItems()
