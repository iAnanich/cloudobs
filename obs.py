import obswebsocket as obs
import obswebsocket.requests as obs_requests
from obswebsocket import events


class OBS:
    def __init__(self, lang, client):
        self.lang = lang
        self.client = client
        self.original_media_source = None

    def add_original_media_source(self, scene_name, original_media_source):
        """
        Adds an original media source
        :param original_media_source: url like 'protocol://address[:port][/path][...]', may be rtmp, srt
        """
        source_settings = {
            'input': original_media_source,
            'is_local_file': False,
        }
        request = obs.requests.CreateSource(
            sourceName='original_stream',
            sourceKind='ffmpeg_source',
            sceneName=scene_name,
            sourceSettings=source_settings
        )
        response = self.client.call(request)

        if not response.status:
            raise Exception(f"E PYSERVER::OBS::add_original_media_source(): "
                            f"coudn't create a source, datain: {response.datain}, dataout: {response.dataout}")

    def reset_scene(self, scene_name='main'):
        """
        Creates (if not been created) a scene called `scene_name` and sets it as a current scene.
        If it has been created, removes all the sources from it and sets it as a current one.
        """
        scenes = self.client.call(
            obs.requests.GetSceneList()).getScenes()  # [... {'name': '...', 'sources': [...]}, ...]

        # if such scene has already been created
        if any([x['name'] == scene_name for x in scenes]):
            self.clear_scene(scene_name)
        else:
            self.create_scene(scene_name)

        self.set_current_scene(scene_name)

    def clear_scene(self, scene_name):
        """
        Removes all the items from a specified scene
        """
        items = self.client.call(obs.requests.GetSceneItemList(sceneName=scene_name)).getSceneItems()
        items = [{'id': item['itemId'], 'name': item['sourceName']} for item in items]
        for item in items:
            response = self.client.call(obs.requests.DeleteSceneItem(scene=scene_name, item=item))
            if not response.status:  # if not deleted
                raise Exception(
                    f"E PYSERVER::OBS::clear_scene(): coudn't delete scene item, datain: {response.datain}, dataout: {response.dataout}")

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
