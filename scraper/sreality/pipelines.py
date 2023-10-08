# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter

from sreality.items import SrealityItem

import database


class PostgresPipeline:
    """ saves items to the database """

    def __init__(self) -> None:
        self._connection = database.Connection(create_database=True)

    def open_spider(self, spider):
        ''' creates database, table and clear the table if not empty '''
        self._connection.make_table(clear=True)

    def close_spider(self, spider):
        self._connection.close()

    def process_item(self, item: SrealityItem, spider):
        spider.logger.info(f'Inserting {item}')
        self._connection.insert(**ItemAdapter(item).asdict())
        return item
