# Youtube-DL Music Server

This project contains the code required to generate a very simple (and insecure, see the disclaimer below for more info) Docker container that can act as a front end for running the "youtube-dl" project (more info on that here: https://youtube-dl.org/) to download music to a locally run docker container.  This project also serves a front end that allows users to browse, stream, and download from the container to whatever host/device they are connecting to with a web browser.

## Disclaimer

This project was created more as a personal exercise where I could play around with multiple technologies.  The owner of this repository takes no responsibility for any usage of this code.  In addition, many libraries this code uses come with their own license considerations (such as: https://github.com/ytdl-org/youtube-dl/blob/master/LICENSE).

As of 2022-07-06 many standard lockdowns and security controls such as TLS/SSL encryption and user input sanitation have not yet been fully implemented.  Attempting to host a server based on this code can expose the network it is hosted on to network interception or server-side exploitation.

In short, look but don't touch unless you're willing to put in a lot more work than what this basic project already has!


## Features
#### Endpoints
###### /rip
This page includes a text input field where users can provide a youtube video url.  The format can match any format the `extract_watch_val` function in `ytdl_server/helpers.py` can parse (some example values are included in `tests/test_helpers.py`).  After copying in a url and pressing enter, a simple javascript function will run and show the progress of the download, pulling the value from the `/jobs` (application/json type) endpoint.

###### /browse
This page reads `*.mp3` files from the configured `working_dir` variable (set in the `etc/ytdl-server.ini` config file that is currently baked into the Docker container).  Users can chose to mount a directory of their choice over this location to host their own music or to persist the storage locally after the docker container is destoryed.  Alternatively, the hyperlinks created for each song name can be clicked directly to download the song from the docker container to their web browser.

This page also allows any of the downloaded/mounted songs to be streamed using a standard html5 `<audio>` element.  I have it on my roadmap to eventually look at creating playlists or other ways to group and play songs, but that would be easier to do by introducing a database as an intermediary between the web frontend and the media backend.  And I may not get around to this for awhile yet.

###### /jobs
As mentioned above in `/rip`, this endpoint exists to serve application/json data from the download progress javascript.  This is fed by some of the functions in helpers.py and backend.py, although much of the existing logic would benefit from a rework.  Ideally this would have a better way to create, id, and track individual jobs and manage parallel downloads.  This could be potentially scaled up by introducting a queue service like activeMQ or kafka as an intermediary to track the creation and consumption of individual jobs by individual servers.  But this wouldn't do much good until the frontend and backend code were further seperated into individual containers.

## Usage

#### Setup
While the docker container created by this project can be immediatly used on any hosts that can run docker, building the docker container will require a workstation that can install python3 and the various dependencies included in this project.

This project was built on an Ubuntu workstation with python 3.8.10.  Virtual Environment (venv) was used to create the dev install where pytests were run and the sdist was created (through setuptools).  Additionally, running the actual backend youtube-dl processes requires the additional packages mentioned in the Dockerfile such as `ffmpeg`.

Given that this project was not really intended to be used by others, I won't be including detailed usage instructions.

Commands for the major build and (dev) deployment process can be found in the Makefile and run like:
```bash
make docker-quicktest
```
