# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class CommodityIndexItem(Item):
    """商品的索引信息"""
    image = Field()
    price = Field()
    deal_cnt = Field()
    title = Field()
    shop = Field()
    location = Field()
    href = Field()
