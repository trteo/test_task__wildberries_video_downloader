from loguru import logger
from pynput import keyboard

from src.video_dawnloader import VideoDownloader


class KeyPressMonitoring:
    def __init__(self):
        self.video_downloader = VideoDownloader()

        self.f4_pressed = False

    def on_press(self, key):
        logger.debug(f'Pressed key: {key}')
        if key == keyboard.Key.f4 and not self.f4_pressed:  # Отсеиваем зажатие f4
            self.f4_pressed = True
            logger.debug("F4 key pressed. Starting download...")

            self.video_downloader.add_video_to_downloading_pool()

    def on_release(self, key):
        logger.debug(f'Released key: {key}')
        if key == keyboard.Key.f4:
            self.f4_pressed = False

    def start_key_listener(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
        logger.info('Key listener started!')
