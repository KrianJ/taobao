import scrapy
from scrapy import Request
from urllib.parse import quote
from taobao.items import CommodityIndexItem
from bs4 import BeautifulSoup

class CommodityIndexSpider(scrapy.Spider):
    name = 'commodity_index'
    allowed_domains = ['www.taobao.com']
    base_url = 'https://s.taobao.com/search?q='

    def start_requests(self):
        max_page = self.settings.get('MAX_PAGE')
        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1, max_page+1):
                # 在该循环中由于每次请求url都是相同的，所以不加入去重(dont_filter)
                url = self.base_url + quote(keyword)
                yield Request(url=url, callback=self.parse, meta={'page': page}, dont_filter=True)

    def parse(self, response):
        commodities = response.css('#mainsrp-itemlist > div > div > div:nth-child(1) > div[class*="item J_MouserOnverReq"]').extract()
        for commodity in commodities:
            commodity = BeautifulSoup(commodity, 'lxml')
            item = CommodityIndexItem()
            item['image'] = commodity.select('div.pic img')[0].get('data-src')
            item['price'] = commodity.select('div[class="price g_price g_price-highlight"]')[0].get_text().strip()
            item['deal_cnt'] = commodity.select('div[class="deal-cnt"]')[0].get_text()
            item['title'] = commodity.select('div[class="row row-2 title"]')[0].get_text().strip()
            item['shop'] = commodity.select('div[class="row row-3 g-clearfix"] .shop a')[0].get_text().strip()
            item['location'] = commodity.select('div[class="row row-3 g-clearfix"] .location')[0].get_text().strip()
            item['href'] = commodity.select('div[class="row row-2 title"] > a')[0].get('href')
            yield item
