# Reference: https://github.com/ytdl-org/youtube-dl/blob/master/README.md#embedding-youtube-dl
from __future__ import unicode_literals
import youtube_dl
import os, shutil, re, json
import logging
from tempfile import TemporaryDirectory
from helpers import sanitize_title, get_and_track_true_progress, read_job_progress_file, get_true_progress

class MyLogger(object):
    def debug(self, msg):
        print(msg)
        logging.debug(msg)
        #pass

    def warning(self, msg):
        print(msg)
        logging.warning(msg)
        #pass

    def error(self, msg):
        #TODO: do some testing and verify that I can rely fully on logging instead of print for catching these errors
        print(msg)
        logging.error(msg)

def my_hook(d):
    get_and_track_true_progress(d)
    true_progress = get_true_progress()
    logging.debug(f'true_progress at this point: {true_progress}')
    if d['status'] == 'finished':
        logging.info('Done downloading, now converting ...')

#Nice idea: #'outtmpl': 'trash/myprefix-%(title)s-%(id)s-mysuffix.%(ext)s',
#'outtmpl': '%(title)s-%(id)s/%(title)s-%(id)s.%(ext)s',

def ensure_filesystem_structure(dir_list):
    for i in dir_list:
        os.makedirs(i, mode=0o750, exist_ok=True)

def generate_ydl_opts_music(tmpdirname):
    return {
        #BAD#'outtmpl': str(tmpdirname) + '/' + '%(title)s-%(id)s.%(ext)s', #This works, but is unpredictable
        #  Bad special characters in the title such as '/' can result in very strange file names.
        'outtmpl': str(tmpdirname) + '/' + '%(id)s.%(ext)s',
        'writethumbnail': True, #Disabling this for now
        #'writethumbnail': False, #Setting this to false breaks the conversion process
        #'embedthumbnail': True, #This doesn't seem to do anything when placed here.  https://github.com/ytdl-org/youtube-dl/blob/5208ae92fc3e2916cdccae45c6b9a516be3d5796/youtube_dl/postprocessor/__init__.py suggests this is a postprocessor
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
        {
            'key': 'EmbedThumbnail',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
#Note: Post processor config is a bit odd:
#  To start, you need to provide the name of the post processor (anything from https://github.com/ytdl-org/youtube-dl/blob/5208ae92fc3e2916cdccae45c6b9a516be3d5796/youtube_dl/postprocessor/__init__.py works after you remove the trailing 'PP')
#  Some post processers don't really need any other options.  It's enough to just call them.  Others can take additional arguments like:
#  preferredcodec=None, preferredquality=None (Reference: https://github.com/ytdl-org/youtube-dl/blob/5208ae92fc3e2916cdccae45c6b9a516be3d5796/youtube_dl/postprocessor/ffmpeg.py#L250)
#  These additional options can follow after the key argument.

def download_mp3(url, media_dir):
    try:
        with TemporaryDirectory() as tmpdirname:
            logging.info(f'Created tempdir at: {tmpdirname}')
            #NOTE: tmpdirname should be an absolute path name, so this should just work
            opts = generate_ydl_opts_music(tmpdirname)
            with youtube_dl.YoutubeDL(opts) as ydl:
                # Do the actual download
                ydl.download([url])

                info = ydl.extract_info(url)
                title    = info.get('title')
                watch_id = info.get('id')

                src_filename = f'{watch_id}.mp3' #Based on outtmpl = '%(id)s.%(ext)s'
                src = os.path.join(tmpdirname, src_filename)

                sanitized_title = sanitize_title(title)
                sanitized_filename = f'{sanitized_title}-{watch_id}.mp3'

                dest = os.path.join(media_dir, sanitized_filename)
                shutil.copyfile(src=src, dst=dest, follow_symlinks=True)
                logging.debug("Successfully copied file to hosted!")
    #TODO: Add actual exceptions like: FileNotFound
    except Exception as e:
        #TODO: do some testing and verify that I can rely fully on logging instead of print for catching these errors
        print(f'ERROR: Caught exception!  Exception was: {e}')
        logging.error(f'ERROR: Caught exception!  Exception was: {e}')
