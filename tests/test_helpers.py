import pytest
import json
from ytdl_server.helpers import extract_watch_val, reconstruct_url_from_watch, sanitize_title, convert_percent_str_to_float

@pytest.fixture
def link_formats():
    return [r'https://www.youtube.com/watch?v=zQ2LfW-DWDc',
        r'https://www.youtube.com/watch?v=zQ2LfW-DWDc&list=LLsxxUyDTDiolcxP_6YF7jAQ'
        r'https://youtu.be/zQ2LfW-DWDc'
    ]

@pytest.fixture
def d_json_downloading():
    return json.loads('''{
         "status": "downloading",
         "downloaded_bytes": 1024,
         "total_bytes": 1017302,
         "tmpfilename": "/tmp/tmpxsa7zndr/q0EumyQgEBw.m4a.part",
         "filename": "/tmp/tmpxsa7zndr/q0EumyQgEBw.m4a",
         "eta": 143,
         "speed": 7082.064014431361,
         "elapsed": 0.21049976348876953,
         "_eta_str": "02:23",
         "_percent_str": "  0.1%",
         "_speed_str": " 6.92KiB/s",
         "_total_bytes_str": "993.46KiB"
    }''')

@pytest.fixture
def d_json_finished():
    return json.loads('''{
        "downloaded_bytes": 1017302,
        "total_bytes": 1017302,
        "filename": "/tmp/tmpxsa7zndr/q0EumyQgEBw.m4a",
        "status": "finished",
        "elapsed": 15.091556310653687,
        "_total_bytes_str": "993.46KiB",
        "_elapsed_str": "00:15"
    }''')

@pytest.fixture
def d_percent_str(d_json_downloading):
    return d_json_downloading.get('_percent_str')

def test_extract_watch_val(link_formats):
    watch = 'zQ2LfW-DWDc'
    for link in link_formats:
        assert extract_watch_val(link) == watch

def test_reconstruct_url_from_watch():
    link = 'https://www.youtube.com/watch?v=zQ2LfW-DWDc'
    watch = 'zQ2LfW-DWDc'
    assert reconstruct_url_from_watch(watch) == link

def test_sanitize_title():
    title = 'a b-c/d_e?f$g - h5i+j'
    want = 'a_b-cd_efg_-_h5i+j'
    assert sanitize_title(title) == want


def test_convert_percent_str_to_float(d_percent_str):
    text = d_percent_str
    assert convert_percent_str_to_float(text) ==  float(0.1)
