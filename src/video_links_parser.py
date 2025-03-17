from typing import List

from loguru import logger
from selenium.webdriver.common.by import By


class WildberriesFeedbackVideoLinksParser:
    def __init__(self, driver):
        self.__driver = driver

    def try_to_find_links(self) -> List[str]:
        video_elements = self.__driver.find_elements(By.TAG_NAME, "video")
        video_elements_with_poster_tag = [
            video.get_attribute("poster")
            for video in video_elements
            if video.get_attribute("poster")
        ]

        result = []
        for video_element in video_elements_with_poster_tag:
            logger.debug(f'Parsed link on preview: {video_element}')

            link_on_m3u8 = video_element.replace("preview.webp", "index.m3u8")

            logger.info(f'Build link on m3u8: {link_on_m3u8}')
            result.append(link_on_m3u8)

        if not result:
            logger.warning('No video tags with poster attribute was found on page')
        return result
