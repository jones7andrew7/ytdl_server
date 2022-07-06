import re, json, os
import logging
from pathlib import Path #https://docs.python.org/3/library/pathlib.html#pathlib.Path for research later

#https://www.youtube.com/watch?v=ljSITVHdJ5c
#Testing basic url parsing and options
def extract_watch_val(link):
    #p = re.compile('.*/watch\?v=([\w\-_]+).*')
    #Reference: https://stackoverflow.com/a/67255602
    # ^(?:https?:)?(?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/(?:watch|v|embed)(?:\.php)?(?:\?.*v=|\/))([a-zA-Z0-9\_-]{7,15})(?:[\?&][a-zA-Z0-9\_-]+=[a-zA-Z0-9\_-]+)*(?:[&\/\#].*)?$
    regex = r'^(?:https?:)?(?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/(?:watch|v|embed)(?:\.php)?(?:\?.*v=|\/))([a-zA-Z0-9\_-]{7,15})(?:[\?&][a-zA-Z0-9\_-]+=[a-zA-Z0-9\_-]+)*(?:[&\/\#].*)?$'
    p = re.compile(regex)
    m = p.match(link)
    return str(m.group(1))

def reconstruct_url_from_watch(watch):
    return 'https://www.youtube.com/watch?v=' + str(watch)

def sanitize_title(title):
    sanitized =  re.sub(r'[\s]+', '_', re.sub(r'[^\s\w\+\-]', '', title))
    #logging.debug(f"DEBUG: title: {title}\nDEBUG: sanitized: {sanitized}")
    return sanitized

#OLD version that just writes the percent by itself:
#def update_job_progress_file(progress=50, job_file_path='/tmp/yt-job-data.txt'):
#    with open(job_file_path, 'w') as f:
#        data = f.write(json.dumps(progress, indent=2))
#
#def read_job_progress_file(job_file_path='/tmp/yt-job-data.txt'):
#    progress = 0
#    with open(job_file_path, 'r') as f:
#        data = f.read()
#        progress = json.loads(data)['progress']
#    return progress

#New version that writes the entire hook status:
def initialize_job_progress_file(d):
    job_file_path='/tmp/yt-job-data.txt'
    d['true_progress'] = 0.0
    with open(job_file_path, 'w') as f:
        data = f.write(json.dumps(d, indent=2))

def get_and_track_true_progress(orig_d):
    #if d.get('status') == 'finished':
    #if d.get('status') == 'downloading':
    d = orig_d.copy()
    #logging.debug(f'DEBUG: d (copied) is: {d}')
    job_file_path='/tmp/yt-job-data.txt'
    p = Path(job_file_path)
    #First test if a file for a previous or active job is in place
    #If there is no file, no proper file, or if the file is from a different
    #job, then skip down to the else and initialize a fresh file
    #DEBUG#logging.debug('DEBUG: in function: get_and_track_true_progress')
    #DEBUG#logging.debug("DEBUG: Testing: p.is_file() ...")
    #DEBUG#logging.debug(p.is_file())
    #DEBUG#logging.debug("DEBUG: Testing: read_job_progress_file().get('true_progress') ...")
    #DEBUG#logging.debug(read_job_progress_file().get('true_progress'))
    #DEBUG#logging.debug("DEBUG: Testing: is_same_job_id(d)")
    #DEBUG#logging.debug(is_same_job_id(d))
    #Fails?#if p.is_file() and read_job_progress_file().get('true_progress') and is_same_job_id(d):
    if p.is_file() and is_same_job_id(d):
        #Read the true_progress value from the previous file
        last_true_progress = read_job_progress_file().get('true_progress')
        logging.debug(f'DEBUG: last_true_progress was: {last_true_progress}')
        #If the last update had finished the first phase and actively in progress on
        #the second phase then call the matching function
        if last_true_progress >= 50:
            #logging.debug('DEBUG: In the last_true_progress if loop: True')
            update_job_progress_file(d, second_phase=True)
        else:
            #logging.debug('DEBUG: In the last_true_progress if loop: False')
            update_job_progress_file(d, second_phase=False)
    #TODO: Everything is ending up in this for some reason?
    else:
        #logging.debug('DEBUG: In the global else for initialize_job_progress_file')
        initialize_job_progress_file(d)


        #This will be true when the last entry was a fully completed job (ideally)
        #Assuming the file exists (after being created by the init in the final else
        #or from a previous update run) we just need to check the true progress of the last
        #entry to see if it's time to add 50 to the result
#TEMP#        if last_true_progress >= 100 not is_same_job_id(d):
#TEMP#            #So we prepare a new file for this new job
#TEMP#            initialize_job_progress_file(d)
#TEMP#            #TODO: This is a bug, right now this will zero out the progress once it hits 100
#TEMP#            #This needs to be fixed with some sort of job id, maybe based off the random
#TEMP#            #tempdir name from the previous entries

def parse_job_id_from_tempdir(text):
    p = re.compile(r'\/tmp\/(tmp[\w]*)\/.*')
    m = p.match(text)
    return m.group(1)

def is_same_job_id(d):
    #logging.debug('DEBUG: inside function: is_same_job_id')
    job_file_path='/tmp/yt-job-data.txt'
    job_progress_data = read_job_progress_file()
    if not 'filename' in job_progress_data:
        return False
    last_filename = job_progress_data.get('filename')
    last_job_id = parse_job_id_from_tempdir(last_filename)
    new_filename = d.get('filename')
    new_job_id = parse_job_id_from_tempdir(new_filename)
    if new_job_id == last_job_id:
        #logging.debug('DEBUG: is_same_job_id returning True')
        return True
    #logging.debug('DEBUG: is_same_job_id returning False')
    return False

def update_job_progress_file(d, second_phase=False):
    job_file_path='/tmp/yt-job-data.txt'
    raw_progress = 100
    if d.get('status') == 'downloading':
        raw_progress = convert_percent_str_to_float(d.get('_percent_str'))
    true_progress = raw_progress / 2
    if second_phase:
        true_progress += 50
    if true_progress > 100:
        true_progress = 100
    #logging.debug(f'DEBUG: About to add true_progress value: {true_progress}')
    #logging.debug(f'DEBUG: raw_progress value was: {raw_progress}')
    d['true_progress'] = true_progress
    #logging.debug(f'DEBUG: full d after update is: {d}')
    with open(job_file_path, 'w') as f:
        data = f.write(json.dumps(d, indent=2))

def read_job_progress_file():
    job_file_path='/tmp/yt-job-data.txt'
    data = {}
    if os.path.isfile(job_file_path):
        with open(job_file_path, 'r') as f:
            data = json.loads(f.read())
    return data

def get_true_progress():
    job_progress_data = read_job_progress_file()
    if not 'true_progress' in job_progress_data:
        return 0
    return int(job_progress_data.get('true_progress'))

def convert_percent_str_to_float(text):
    #logging.debug(f'DEBUG: text: {text}')
    if text is None:
        return float(100.0)
    p = re.compile(r'\s*([0-9\.]+)%\s*')
    m = p.match(text)
    #logging.debug(f'DEBUG: m: {m}')
    return float(m.group(1))

def temp_log_hook(message):
    job_details_path = '/tmp/yt-job-details.txt'
    with open(job_details_path, 'a') as f:
        data = f.write(message)


#Reference:
#{
#  "downloaded_bytes": 1017302,
#  "total_bytes": 1017302,
#  "filename": "/tmp/tmpxsa7zndr/q0EumyQgEBw.m4a",
#  "status": "finished",
#  "elapsed": 15.091556310653687,
#  "_total_bytes_str": "993.46KiB",
#  "_elapsed_str": "00:15"
#}{
#  "status": "downloading",
#  "downloaded_bytes": 1024,
#  "total_bytes": 1017302,
#  "tmpfilename": "/tmp/tmpxsa7zndr/q0EumyQgEBw.m4a.part",
#  "filename": "/tmp/tmpxsa7zndr/q0EumyQgEBw.m4a",
#  "eta": 143,
#  "speed": 7082.064014431361,
#  "elapsed": 0.21049976348876953,
#  "_eta_str": "02:23",
#  "_percent_str": "  0.1%",
#  "_speed_str": " 6.92KiB/s",
#  "_total_bytes_str": "993.46KiB"
#}
