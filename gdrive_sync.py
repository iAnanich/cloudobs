from __future__ import print_function

import os.path
import io
import time

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from dotenv import load_dotenv

load_dotenv()
DRIVE_ID = os.getenv('GDRIVE_DRIVE_ID')
MEDIA_DIR = os.getenv('MEDIA_DIR')
LANG = os.getenv('LANG')
API_KEY = os.getenv('GDRIVE_API_KEY')
SYNC_SECONDS = os.getenv('GDRIVE_SYNC_SECONDS')


def run_drive_sync(drive_id, sync_period_seconds, local_dir, api_key):
    """
    Every `sync_period_seconds` lists child files within
    a specified `drive_id`, compares with a list of files
    in `local_dir` directory, and downloads the new ones.
    Does not raise exceptions.
    """
    while True:
        try:
            time.sleep(int(sync_period_seconds))
            # every time rebuild service, since I am not sure of there is no timeout
            with build('drive', 'v3', developerKey=api_key) as service:
                # list the drive files, the response is like the following structure:
                """
                {'kind': 'drive#fileList',
                 'incompleteSearch': False,
                 'files': [{'kind': 'drive#file',
                   'id': '1HCFWjOE-XTAh_Mau7DrSYsR3_uu0Ei3r',
                   'name': 'electron_edited.wav',
                   'mimeType': 'audio/wav'}]}
                """
                files = service.files().list(q=f"'{drive_id}' in parents").execute()
                # if something went wrong
                if 'files' not in files:
                    raise Exception(f"Couldn't list files in specified driveId. Error: {files}")

                for fileinfo in files['files']:
                    fid, fname = fileinfo['id'], fileinfo['name']
                    # if such file is not found locally, download it
                    flocal = os.path.join(local_dir, fname)
                    if not os.path.isfile(flocal):
                        request = service.files().get_media(fileId=fid)

                        with io.FileIO(flocal, mode='w') as fh:
                            downloader = MediaIoBaseDownload(fh, request)
                            done = False
                            while not done:
                                status, done = downloader.next_chunk()
                                # print("Download %d%%." % int(status.progress() * 100))
                            print(f"I PYSERVER::run_drive_sync(): Downloaded {fname} => {flocal}, status: {status}")
        except Exception as ex:
            print(f"E PYSERVER::run_drive_sync(): {ex}")


if __name__ == '__main__':
    media_dir = os.path.join(MEDIA_DIR, LANG)
    os.system(f"mkdir -p {media_dir}")
    run_drive_sync(drive_id=DRIVE_ID,
                   sync_period_seconds=SYNC_SECONDS,
                   local_dir=media_dir,
                   api_key=API_KEY)
