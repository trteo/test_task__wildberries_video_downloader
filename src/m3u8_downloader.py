import asyncio
import os
import shutil
import threading
from os.path import exists
from pathlib import Path
from typing import List
from urllib.error import HTTPError
from urllib.parse import urlparse

import ffmpeg
import m3u8
import requests
from loguru import logger


class M3U8Downloader:
    def __init__(self, downloading_path: Path):
        self.__loop = asyncio.get_event_loop()
        self.__thread = threading.Thread(target=self.__loop.run_forever).start()

        self.__downloading_path = downloading_path
        self.__tmp_path = downloading_path / '.tmp'

    def add_video_to_downloading_pool(self, m3u8_url: str):
        asyncio.run_coroutine_threadsafe(self.__download_video(m3u8_url=m3u8_url), self.__loop)

    async def __download_video(self, m3u8_url: str):
        logger.info(f"Start downloading video by link {m3u8_url}")

        video_uuid = urlparse(m3u8_url).path.split('/')[1]
        video_tmp_dir = self.__tmp_path / video_uuid
        concat_list_path = video_tmp_dir / "concat_list.txt"
        output_video_path = f'{self.__downloading_path}/{video_uuid}.mp4'

        if exists(output_video_path):
            logger.info(f'Video {video_uuid} already exists at path {output_video_path}')
            return

        self.__prepare_paths(video_tmp_dir=video_tmp_dir)
        self.__download_segments(
            m3u8_url=m3u8_url,
            concat_list_path=concat_list_path,
            video_tmp_dir=video_tmp_dir
        )
        self.__m3u8_2_mp4_converter(
            output_file_path=output_video_path,
            concat_list_path=concat_list_path
        )
        self.__clear_temporary_files(video_tmp_dir=video_tmp_dir)

        logger.info(f"Video downloaded: {m3u8_url} to {output_video_path}")

    @staticmethod
    def __prepare_paths(video_tmp_dir: Path):
        video_tmp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f'Created tmp folder: {video_tmp_dir}')

    def __download_segments(self, m3u8_url: str, concat_list_path: Path, video_tmp_dir: Path):
        logger.info(f"Start downloading segments to {video_tmp_dir}")

        playlist = m3u8.load(m3u8_url)
        segment_files: List[Path] = [
            self.__download_segment(segment=segment, video_tmp_dir=video_tmp_dir)
            for segment in playlist.segments
        ]

        logger.info(f"Downloading segments to {video_tmp_dir} done")

        with open(concat_list_path, "w") as f:
            for segment_file in segment_files:
                f.write(f"file '{segment_file}'\n")

        logger.info(f"Created concat list {concat_list_path}")

    @staticmethod
    def __download_segment(segment: m3u8.Segment, video_tmp_dir: Path) -> Path:
        segment_url: str = segment.absolute_uri
        segment_path = video_tmp_dir / os.path.basename(segment_url)

        logger.info(f"Downloading {segment_url}...")
        response = requests.get(segment_url)
        if response.status_code == 200:
            with open(segment_path, 'wb') as f:
                f.write(response.content)
        else:
            raise HTTPError(code=response.status_code, msg=f'Failed to load segment: {segment_url}')

        logger.info(f"Downloading {segment_url} done")
        return segment_path

    @staticmethod
    def __m3u8_2_mp4_converter(output_file_path: str, concat_list_path: Path) -> None:
        (
            ffmpeg
            .input(concat_list_path, format='concat', safe=0)
            .output(output_file_path, c='copy')
            .overwrite_output()
            .run()
        )
        logger.info(f'Finished converting video to mp4: {output_file_path}')

    @staticmethod
    def __clear_temporary_files(video_tmp_dir: Path):
        shutil.rmtree(video_tmp_dir)
        logger.info(f'Removed tmp folder: {video_tmp_dir}')
