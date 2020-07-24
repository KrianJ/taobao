# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2020/7/24 15:24"
__doc__ = """ """
from random import randint
from selenium.webdriver import ActionChains
import time


class slider_verification(object):
    """破解滑块验证"""
    def __init__(self, driver, slider, distance):
        """
        :param driver: 当前浏览器驱动
        :param slider: 定位的滑块元素
        :param distance: 滑块的位移量
        """
        self.driver = driver
        self.slider = slider
        self.distance = distance

    def get_tracks(self):  # distance为传入的总距离
        """将轨迹长度拆分，模拟登录验证行为"""
        tracks = []
        steps = randint(4, 6)
        for step in range(steps):
            if step < steps - 1:
                offset = randint(6, 12)  # 每段位移的偏移量
                step_dis = self.distance // steps - offset
                tracks.append(step_dis)
            else:
                tracks.append(self.distance - sum(tracks))
        return tracks

    def move_to_gap(self, tracks):
        """
        滑动滑块
        :param slider: 要移动的滑块
        :param tracks: 传入的移动轨迹
        :return:
        """
        action = ActionChains(self.driver)
        action.click_and_hold(self.slider).perform()  # perform()用来执行ActionChains中存储的行为
        for x in tracks:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.driver).release().perform()
