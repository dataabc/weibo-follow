#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random
import sys
import traceback
from time import sleep

import requests
from lxml import etree
from tqdm import tqdm

from weiboSpider import Weibo


class Follow(object):
    cookie = {'Cookie': 'your cookie'}  # 将your cookie替换成自己的cookie

    def __init__(self, user_id):
        """Follow类初始化"""
        if not isinstance(user_id, int):
            sys.exit(u'user_id值应为一串数字形式,请重新输入')
        self.user_id = user_id
        self.follow_list = []  # 存储爬取到的所有关注微博的user_id

    def deal_html(self, url):
        """处理html"""
        try:
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            return selector
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_page_num(self):
        """获取关注列表页数"""
        url = "https://weibo.cn/%d/follow" % self.user_id
        selector = self.deal_html(url)
        if selector.xpath("//input[@name='mp']") == []:
            page_num = 1
        else:
            page_num = (int)(
                selector.xpath("//input[@name='mp']")[0].attrib['value'])
        return page_num

    def get_one_page(self, page):
        """获取第page页的user_id"""
        url = 'https://weibo.cn/%d/follow?page=%d' % (self.user_id, page)
        selector = self.deal_html(url)
        table_list = selector.xpath('//table')
        for t in table_list:
            im = t.xpath('.//a/@href')[-1]
            user_id = im[im.find('=') + 1:im.find('&')]
            print(user_id)
            self.follow_list.append(int(user_id))

    def get_follow_list(self):
        """获取关注用户主页地址"""
        page_num = self.get_page_num()
        print(u'用户关注页数：' + str(page_num))
        page1 = 0
        random_pages = random.randint(1, 5)
        for page in tqdm(range(1, page_num + 1), desc=u'关注列表爬取进度'):
            self.get_one_page(page)

            if page - page1 == random_pages and page < page_num:
                sleep(random.randint(6, 10))
                page1 = page
                random_pages = random.randint(1, 5)

        print(u'用户关注列表爬取完毕')


def main():
    try:
        # 爬取关注列表的user_id
        user_id = 12345678  # 爬虫的user_id
        fw = Follow(user_id)  # 调用Weibo类，创建微博实例wb
        fw.get_follow_list()  # 爬取微博信息

        filter = 1  # 值为0表示爬取全部微博（原创微博+转发微博），值为1表示只爬取原创微博
        pic_download = 0  # 值为0代表不下载微博原始图片,1代表下载微博原始图片
        for user in fw.follow_list:

            # 爬每个人的微博
            Weibo(user, filter, pic_download).start()

    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
