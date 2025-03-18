import asyncio
import os
import shutil
import threading
from os.path import exists
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import aiofiles
import aiohttp
import m3u8
from loguru import logger


class M3U8Downloader:
    def __init__(self, downloading_path: Path):
        self.__loop = asyncio.get_event_loop()
        self.__thread = threading.Thread(target=self.__loop.run_forever).start()

        self.__downloading_path = downloading_path
        self.__tmp_path = downloading_path / '.tmp'

    def add_video_to_downloading_pool(self, m3u8_url: str):
        logger.info(f'Adding {m3u8_url} to pool')
        asyncio.run_coroutine_threadsafe(self.__download_video(m3u8_url=m3u8_url), self.__loop)

    async def __download_video(self, m3u8_url: str):
        logger.info(f"Start downloading video by link {m3u8_url}")

        video_uuid = urlparse(m3u8_url).path.split('/')[1]
        video_tmp_dir = self.__tmp_path / video_uuid
        concat_list_path = video_tmp_dir / "concat_list.txt"
        output_video_path = f'{self.__downloading_path}/{video_uuid}.mp4'

        try:
            if exists(output_video_path):
                logger.info(f'Video {video_uuid} already exists at path {output_video_path}')
                return

            self.__prepare_paths(video_tmp_dir=video_tmp_dir)
            await self.__download_segments(
                m3u8_url=m3u8_url,
                concat_list_path=concat_list_path,
                video_tmp_dir=video_tmp_dir
            )
            await self.__m3u8_2_mp4_converter(
                output_file_path=output_video_path,
                concat_list_path=concat_list_path
            )
            self.__clear_temporary_files(video_tmp_dir=video_tmp_dir)

            logger.info(f"Video downloaded: {m3u8_url} to {output_video_path}")
        except Exception as e:
            self.__clear_temporary_files(video_tmp_dir=video_tmp_dir)
            logger.error(f"Failed to download video {m3u8_url}: {e}")

    @staticmethod
    def __prepare_paths(video_tmp_dir: Path):
        try:
            video_tmp_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f'Created tmp folder: {video_tmp_dir}')
        except Exception as e:
            logger.error(f"Failed to create directory {video_tmp_dir}: {e}")
            raise

    async def __download_segments(self, m3u8_url: str, concat_list_path: Path, video_tmp_dir: Path):
        logger.info(f"Start downloading segments to {video_tmp_dir}")

        try:
            playlist = m3u8.load(m3u8_url)
            segment_files: List[Path] = await asyncio.gather(*[
                self.__download_segment(segment=segment, video_tmp_dir=video_tmp_dir)
                for segment in playlist.segments
            ])

            logger.info(f"Downloading segments to {video_tmp_dir} done")

            async with aiofiles.open(concat_list_path, "w") as f:
                for segment_file in segment_files:
                    await f.write(f"file '{segment_file}'\n")

            logger.info(f"Created concat list {concat_list_path}")
        except Exception as e:
            logger.error(f"Failed to download segments: {e}")
            raise

    @staticmethod
    async def __download_segment(segment: m3u8.Segment, video_tmp_dir: Path) -> Path:
        segment_url: str = segment.absolute_uri
        segment_path = video_tmp_dir / os.path.basename(segment_url)

        retries = 5
        logger.info(f"Downloading {segment_url}...")
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(segment_url) as response:
                        response.raise_for_status()
                        async with aiofiles.open(segment_path, 'wb') as f:
                            await f.write(await response.read())
                logger.info(f"Downloading {segment_url} done")
                return segment_path
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Attempt {attempt + 1} failed for {segment_url}: {e}")
                if attempt == retries - 1:
                    logger.error(f"Failed to download segment {segment_url} after {retries} attempts: {e}")
                    raise
                await asyncio.sleep(2)

    @staticmethod
    async def __m3u8_2_mp4_converter(output_file_path: str, concat_list_path: Path) -> None:
        try:
            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(concat_list_path), '-c', 'copy', output_file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            logger.info(f'Finished converting video to mp4: {output_file_path}')
        except Exception as e:
            logger.error(f"Failed to convert video to mp4: {e}")
            raise

    @staticmethod
    def __clear_temporary_files(video_tmp_dir: Path):
        try:
            shutil.rmtree(video_tmp_dir)
            logger.info(f'Removed tmp folder: {video_tmp_dir}')
        except Exception as e:
            logger.error(f"Failed to remove temporary files: {e}")
            raise
