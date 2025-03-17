from loguru import logger
from pynput import keyboard

from src.m3u8_downloader import M3U8Downloader
from src.video_links_parser import WildberriesFeedbackVideoLinksParser


class KeyPressMonitoring:
    def __init__(self, video_downloader: M3U8Downloader, parser: WildberriesFeedbackVideoLinksParser):
        self.__video_downloader = video_downloader
        self.__video_link_parser = parser
        self.__f4_pressed = False

    def start_key_listener(self):
        with keyboard.Listener(on_press=self.__on_press, on_release=self.__on_release) as listener:
            listener.join()
        logger.info('Key listener started!')

    def __on_press(self, key):
        logger.debug(f'Pressed key: {key}')

        if key == keyboard.Key.f4 and not self.__f4_pressed:  # Отсеиваем зажатие f4
            self.__f4_pressed = True
            logger.debug("F4 key pressed. Starting download...")
            try:
                links_on_page = self.__video_link_parser.try_to_find_links()

                for link_on_page in links_on_page:
                    if link_on_page and '.m3u8' in link_on_page:
                        self.__video_downloader.add_video_to_downloading_pool(m3u8_url=link_on_page)
                    else:
                        logger.error(f'Unprocessable url: {link_on_page}')
            except Exception as e:
                logger.error(f"Failed to process links: {e}")

    def __on_release(self, key):
        logger.debug(f'Released key: {key}')
        if key == keyboard.Key.f4:
            self.__f4_pressed = False

