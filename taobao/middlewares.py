# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html


from scrapy.http import HtmlResponse
from logging import getLogger
# selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
# 滑块验证
from .selenium_component.slider_verify import slider_verification


class CommondityIndexMiddleware():
    def __init__(self, timeout=None):
        self.logger = getLogger(__name__)
        self.timeout = timeout
        self.chrome_option = webdriver.ChromeOptions()
        # self.chrome_option.add_argument('headless')
        self.chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])  # 使用开发者模式
        self.browser = webdriver.Chrome(options=self.chrome_option)
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()

    def login(self):
        """淘宝自动化登录"""
        try:
            # 账号/密码input
            username = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#fm-login-id'))
            )
            password = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#fm-login-password'))
            )
            username.send_keys('18395327553')  # 用户名
            password.send_keys('zPq19961014')  # 密码
            # 登录button
            login_submit = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#login-form > div.fm-btn > button'))
            )

            # 滑动验证：使用ActionChains拖动滑块
            slip_square = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#nc_1_n1z'))
            )
            verify = slider_verification(self.browser, slip_square, 258)
            tracks = verify.get_tracks()
            verify.move_to_gap(tracks)

            # 点击登录
            login_submit.click()
        finally:
            pass

    def process_request(self, request, spider):
        self.logger.debug("已启动Chrome")
        page = request.meta.get('page')
        try:
            self.browser.get(request.url)
            # 如需登录验证的话
            if 'login.taobao.com' in self.browser.current_url:
                self.login()
            #
            if page > 1:
                # 跳转page对应页面
                page_input = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')
                    )
                )
                submit = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')
                    )
                )
                page_input.clear()
                page_input.send_keys(page)

                submit.click()
                time.sleep(2)
                print("****************************test**********************************")
                print(self.browser.current_url)
                print('*********************************************************************')
                # try:
                #     slip_square = self.browser.find_element_by_id('nc_1_n1z')
                #     # 如果submit不可用，即遇到访问验证，则需要先解除访问认证
                #     print("遇到访问验证")
                #     print(slip_square)
                #     time.sleep(1000)
                #     action = ActionChains(self.browser)
                #     action.click_and_hold(slip_square).perform()  # perform()用来执行ActionChains中存储的行为
                #     action.reset_actions()
                #     action.move_by_offset(258, 0).perform()
                #     time.sleep(10)
                #     submit.click()
                # finally:
                #     pass
            # 等待对应页码处于激活
            self.wait.until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page)
                )
            )
            # 等待每个商品块加载
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="mainsrp-itemlist"]/div/div/div[@class="items"]/div[starts-with(@class, "item")]')
                )
            )
            # 返回response给spider
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request,
                                encoding='utf8', status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
        )
