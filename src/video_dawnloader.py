import asyncio
import random
import threading

from loguru import logger


class VideoDownloader:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever).start()

        self.downloading_dir_path = ''

    def add_video_to_downloading_pool(self):
        asyncio.run_coroutine_threadsafe(self.download_video('url'), self.loop)

    @staticmethod
    async def download_video(url):
        logger.info(f"Downloading video by link {url}")
        # Simulate a download delay
        await asyncio.sleep(3)
        logger.info(f"Video downloaded: {url}")
