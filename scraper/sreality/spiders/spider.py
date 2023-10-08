import logging

from typing import Optional, Any, Iterable

import scrapy
import scrapy.exceptions
from scrapy_playwright.page import PageMethod

from sreality.items import SrealityItem


class SrealitySpider(scrapy.Spider):
    """ goes through sreality.cz using ?page=N; N=1,2,3... """

    name = 'sreality'

    URL_TEMPLATE = r'https://www.sreality.cz/en/search/for-sale/apartments/praha?page={page}'

    def __init__(self, name: Optional[str] = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.close_signal: bool = False
        self.page = 0
        self.ads_processed = 0
        self.maximum_ads_processed = 0

        # logging
        self.logger.setLevel(logging.INFO)

        logger = logging.getLogger("scrapy-playwright")
        logger.setLevel(logging.INFO)

        logger = logging.getLogger("scrapy.core.scraper")
        logger.setLevel(logging.INFO)

    def start_requests(self) -> Iterable[scrapy.Request]:
        self.page = 0
        self.maximum_ads_processed = \
            self.settings.get("MAXIMUM_LOADED_ITEMS", 0)

        yield self.create_next_request()

    def create_next_request(self):
        self.page += 1
        act_url = self.URL_TEMPLATE.format(page=self.page)

        return scrapy.Request(
            url=act_url,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                errback=self.errback,
                playwright_page_methods=[
                    # html is loaded
                    PageMethod("wait_for_load_state", "load"),

                    # waits for property list
                    PageMethod("wait_for_selector", "div.dir-property-list"),

                    # waits for first ad
                    PageMethod("wait_for_selector", "div.property"),

                    # waits for left and right button under ads to be visible
                    PageMethod("wait_for_selector", ".paging-prev"),
                    PageMethod("wait_for_selector", ".paging-next"),

                    # name in the ad
                    PageMethod("wait_for_selector", "span.name"),

                    # adds half second (just in case)
                    PageMethod("wait_for_timeout", 500),
                ],
                dont_redirect=True,
            ),
            callback=self.parse
        )

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        ads = response.css('div.property')

        if not len(ads):
            # I assume that there are always >500 flats in prague...
            self.logger.error("No ads: quitting")
            exit(1)

        for ad in ads:
            title = self.parse_extract_title(ad)
            image_url = self.parse_extract_first_image(ad)

            self.ads_processed += 1
            yield SrealityItem(title=title, url=image_url)

            if self.ads_processed >= self.maximum_ads_processed:
                raise scrapy.exceptions.CloseSpider("Ads limit reached")

        yield self.create_next_request()

    def parse_extract_title(self, property):
        # returns title of the property
        title = property.xpath(r'.//h2//*[string-length(normalize-space(text())) > 0]/text()').getall()

        if len(title) == 0:
            self.logger.error("Title not found")
            exit(1)
        elif len(title) > 1:
            self.logger.error("Found more than one title")
            exit(1)
        return title[0].strip()

    def parse_extract_first_image(self, property):
        # returns first image
        # the a/img removes "camera.svg"
        image_urls = property.xpath(r'.//a/img/@src').getall()

        if len(image_urls) == 0:
            self.logger.error("Image not found")
            exit(1)

        return image_urls[0]
