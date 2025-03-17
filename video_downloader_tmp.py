import os
import shutil
from pathlib import Path
from typing import List

import requests
import m3u8
import ffmpeg


BASE_PATH = Path('/Users/fedortropin/Documents/work/intevus/test_task__wildberries_video_downloader/videos')
TEMP_DIR = BASE_PATH / 'temp_segments'


def prepare_paths():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def download_segments(m3u8_url: str):
    playlist = m3u8.load(m3u8_url)
    segment_files: List[Path] = []

    for segment in playlist.segments:
        segment_files.append(download_segment(segment))

    # Combine the segments into a single file using ffmpeg
    with open(TEMP_DIR / "concat_list.txt", "w") as f:
        for segment_file in segment_files:
            f.write(f"file '{segment_file}'\n")


def download_segment(segment: m3u8.Segment) -> Path:
    segment_url: str = segment.absolute_uri
    segment_path = TEMP_DIR / os.path.basename(segment_url)

    print(f"Downloading {segment_url}...")
    response = requests.get(segment_url)
    with open(segment_path, 'wb') as f:
        f.write(response.content)

    return segment_path


def m3u8_2_mp4_converter(output_file_path: str) -> None:
    (
        ffmpeg
        .input(f"{TEMP_DIR}/concat_list.txt", format='concat', safe=0)
        .output(output_file_path, c='copy')
        .run()
    )


def clear_temporary_files():
    shutil.rmtree(TEMP_DIR)


prepare_paths()
download_segments(m3u8_url='https://videofeedback04.wbbasket.ru/90a2b732-1b1c-4a74-b9c8-0a66fc599d74/index.m3u8')
m3u8_2_mp4_converter(output_file_path=f"{BASE_PATH}/output_video.mp4")
# clear_temporary_files()
