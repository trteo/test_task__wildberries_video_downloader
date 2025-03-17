import sys
import time
import urllib
from urllib.parse import urlparse

from loguru import logger

from src.key_press_detektor import KeyPressMonitoring
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Запуск Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.wildberries.ru/catalog/192186031/feedbacks")

print("Ожидание нажатия F4 для загрузки видео...")


downloaded = set()


def check_key_press():
    while True:
        try:
            # if pyautogui.keyDown('ctrl'):
            #     print('Pressed')
            video_elements = driver.find_elements(By.TAG_NAME, "video")
            video_elements_with_src = [video for video in video_elements if video.get_attribute("src")]

            if video_elements_with_src:
                for e in video_elements_with_src:
                    link_on_preview = e.get_attribute("poster")
                    logger.debug(f'Parsed link on preview: {link_on_preview}')

                    link_on_m3u8 = link_on_preview.replace("preview.webp", "index.m3u8")

                    video_uuid = urlparse(link_on_m3u8).path.split('/')[1]
                    if video_uuid not in downloaded:
                        logger.info(f'Build link on m3u8: {link_on_m3u8}')
                        downloaded.add(video_uuid)
            else:
                logger.info("Видео не найдено на странице")
        except Exception as e:
            logger.info("Ошибка при обработке F4:", e)
        time.sleep(0.5)


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    check_key_press()

    # t = KeyPressMonitoring()
    # t.start_key_listener()
