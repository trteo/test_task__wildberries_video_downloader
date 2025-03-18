import sys
from pathlib import Path

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from settings.config import settings
from src.key_press_detektor import KeyPressMonitoring
from src.m3u8_downloader import M3U8Downloader
from src.video_links_parser import WildberriesFeedbackVideoLinksParser


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level= "DEBUG" if settings.DEBUG else "INFO")
    # logger.add(sys.stderr, level="DEBUG")

    logger.info('Opening browser')
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://www.wildberries.ru/catalog/192186031/feedbacks")

        logger.info('Init parser')
        parser = WildberriesFeedbackVideoLinksParser(driver=driver)

        logger.info('Init video downloader')
        vd = M3U8Downloader(downloading_path=settings.DOWNLOADING_ROOT_PATH)

        logger.info('Init key monitoring')
        keyboard_monitoring = KeyPressMonitoring(video_downloader=vd, parser=parser)

        keyboard_monitoring.start_key_listener()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        driver.quit()
