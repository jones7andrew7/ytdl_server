# save this as app.py
from flask import Flask, url_for, render_template, send_from_directory, request, redirect, jsonify

import os, json
import logging

from backend import download_mp3, ensure_filesystem_structure
from helpers import extract_watch_val, reconstruct_url_from_watch, read_job_progress_file, get_true_progress
from config import YTDLServerConfig

# load config
config = YTDLServerConfig()

# create new app
app = Flask(__name__)

WORKING_DIR=app.root_path
if config.working_dir is not None:
    WORKING_DIR = config.working_dir

# base dirs
STATIC_DIR = os.path.join(app.root_path, 'static')
MEDIA_DIR = os.path.join(WORKING_DIR, 'media')
MUSIC_DIR = os.path.join(MEDIA_DIR, 'music')

#Flask App Routing
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(STATIC_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# for downloading (aka "ripping") media from youtube via youtube-dl
@app.route("/rip", methods=['GET', 'POST'])
def rip():
    if request.method == 'POST':
         watch = extract_watch_val(request.form['link'])
         link = reconstruct_url_from_watch(watch)
         logging.debug(f'DEBUG: watch was: {watch}')
         logging.debug(f'DEBUG: reconstructed link was: {link}')
         download_mp3(url=link, media_dir=MUSIC_DIR)
    return render_template('rip.html')

# for browsing downloaded media
@app.route("/browse/")
def browse():
    list_of_files = [x for x in os.listdir(MUSIC_DIR) if x.endswith(".mp3")]
    logging.debug(f'DEBUG: list_of_files: {list_of_files}')
    return render_template('browse.html', files=list_of_files)

@app.route('/media/music/<filename>')
def serve_music(filename):
    logging.debug('DEBUG: serve_music filename: ' + filename)
    return send_from_directory(MUSIC_DIR, filename, as_attachment=True)

@app.route('/jobs/')
def get_job_progress():
    logging.debug('DEBUG: Running get_job_progress')
    true_progress = get_true_progress()
    progress = {'progress': true_progress}
    return jsonify(progress)

# basic test functions that I'll rewrite eventually
def basic_tests():
    with app.test_request_context():
        logging.info(url_for('index'))
        logging.info(url_for('rip'))
        logging.info(url_for('browse'))
    logging.info(extract_watch_val('https://www.youtube.com/watch?v=ljSITVHdJ5c'))

# the start of the application
if __name__ == "__main__":
    #Top level log config:
    logftm = '%(asctime)s:[%(levelname)s][%(process)d][%(module)s]: %(message)s'
    #loglevel = logging.DEBUG
    loglevel = logging.INFO
    #log_file = '/var/log/ytdl_server.log'
    #log_file = 'ytdl_server.log'
    logging.basicConfig(filename=config.log_file, level=loglevel, format=logftm)
    logging.info("Starting ytdl_server...")

    basic_tests()
    ensure_filesystem_structure([MEDIA_DIR, MUSIC_DIR])
    #app.run(host='0.0.0.0', port=5000)
    app.run(host=config.host, port=config.port)
