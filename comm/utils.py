# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
import platform
import random
import re
from datetime import datetime
from time import sleep

import requests
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from loguru import logger
from fake_useragent import UserAgent
from playwright.sync_api import Page, sync_playwright, Playwright, Browser, BrowserContext
from pyhandytools.file import FileUtils
from pyhandytools.env import EnvUtils


class SystemUtils:
    @staticmethod
    def init_env():
        EnvUtils.init_env()


class BrowserController:
    JS_AVOID_DETECT: str = 'Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});'
    JS_SCROLL_TOP: str = 'var q=document.documentElement.scrollTop=10000'

    @staticmethod
    def load(sp: Playwright,
             browser_type: str = 'chromium',
             headless: bool = True,
             proxy: bool = False) -> [Browser, BrowserContext, Page]:
        """
        加载浏览器内核进来，模拟浏览器行为
        无代理则默认本地
        有代理则优先随机，随机无效则选最快，最快无效则选本地
        Args:
            sp: sync_playwright
            browser_type: 可选chromium|firefox|webkit|edge
            headless: 默认无头，可以设为True方便调试程序，看到爬虫的效果
            proxy: 可选择使用的代理，输入格式是ip:port

        Returns:
            browser浏览器对象, context上下文对象, page当前页面对象
        """
        launch_options = {
            'headless': headless,
            'chromium_sandbox': False,
            'proxy': {
                'server': '',
            }
        }
        if not proxy:
            del launch_options['proxy']
        else:
            random_proxy = ProxyHelper.get_fastest_proxy()
            launch_options['proxy']['server'] = random_proxy

        browser, context, page = BrowserController.launch_browser(sp,
                                                                  browser_type,
                                                                  launch_options)

        if not proxy:
            return browser, context, page
        if ProxyHelper.proxy_isvalid(page):
            return browser, context, page
        # 代理无效，切换代理
        # 先切换最快的，若无效则使用默认本机代理
        launch_options['proxy']['server'] = ProxyHelper.get_fastest_proxy()
        browser, context, page = BrowserController.launch_browser(sp,
                                                                  browser_type,
                                                                  launch_options)
        if ProxyHelper.proxy_isvalid(page):
            return browser, context, page
        else:
            del launch_options['proxy']
            browser, context, page = BrowserController.launch_browser(sp,
                                                                      browser_type,
                                                                      launch_options)
            logger.info('use local proxy')
            return browser, context, page

    @classmethod
    def launch_browser(cls, sp, browser_type, launch_options):
        if browser_type == 'chromium':
            launch_options['args'] = ['--userDataDir=~/Library/Application\ Support/Google/Chrome/Default']
            browser = sp.chromium.launch(**launch_options)
        elif browser_type == 'firefox':
            browser = sp.firefox.launch(**launch_options)
        elif browser_type == 'webkit':
            browser = sp.webkit.launch(**launch_options)
        elif browser_type == 'edge':
            launch_options['channel'] = 'msedge'
            launch_options['args'] = ['--userDataDir=~/Library/Application\ Support/Microsoft\ Edge/Default']
            browser = sp.chromium.launch(**launch_options)
        else:
            logger.error('input browser_type error')
            browser = sp.chromium.launch(**launch_options)
        context = browser.new_context()
        page = context.new_page()
        page.add_init_script(cls.JS_AVOID_DETECT)

        return browser, context, page

    @staticmethod
    def close(context: BrowserContext, browser: Browser) -> None:
        """
        关闭、释放浏览器资源
        Args:
            context: 上下文对象
            browser: 浏览器对象

        Returns:

        """
        context.close()
        browser.close()

    @classmethod
    def scroll(cls, page: Page, times: int,
               sleep_time: int = 1, scroll_type='END'):
        """
        模拟页面滚动
        Args:
            page: 页面对象
            times: 页面滚动的次数
            sleep_time: 每次页面滚动停留的时间，单位是秒s
            scroll_type: 页面滚动类型
                        END 表示模拟键盘End向下滚动
                        其他 表示模拟鼠标向下滑动

        Returns:

        """
        st = sleep_time * 1000
        if scroll_type == 'END':
            for _ in range(times):
                page.keyboard.press('End')
                page.wait_for_timeout(st)
        else:
            for _ in range(times):
                page.evaluate(cls.JS_SCROLL_TOP)
                page.wait_for_timeout(st)
        return page


class ProxyHelper:
    proxy_root_path = './data/proxy_pool/'

    @staticmethod
    def get_random_proxy(
            ok_proxy_path=f"{proxy_root_path}/{str(datetime.now()).split(' ')[0]}/cn_ok_ip.json"
    ):
        """
        随机获取一个代理ip
        Args:
            ok_proxy_path: 可选指定的代理文件路径

        Returns:
            返回一个随机的代理ip
        """

        ok_proxy_data = FileUtils.load_json(ok_proxy_path)
        random_num = random.randint(0, len(ok_proxy_data))
        return ok_proxy_data[random_num]['ip_port']

    @staticmethod
    def get_fastest_proxy(
            ok_proxy_path=f"{proxy_root_path}/{str(datetime.now()).split(' ')[0]}/cn_ok_ip.json"):
        """
        选择响应时间最短的代理ip
        Args:
            ok_proxy_path: 可选指定的代理文件路径

        Returns:
            返回指定代理池中响应时间最短的代理ip
        """
        ok_proxy_data = FileUtils.load_json(ok_proxy_path)
        return ok_proxy_data[0]['ip_port']

    @staticmethod
    def proxy_isvalid(page: Page = None,
                      static_dict_param: dict = None,
                      url: str = 'https://www.baidu.com'):
        """
        判断使用playwright的时候，代理是否有效
        Args:
            static_dict_param: 请求静态页面时候的参数
            page: 页面对象
            url: 测试代理的url

        Returns:
            有效返回True，无效则返回False
        """
        if page:
            try:
                page.goto(url)
                _ = page.title()
            except Exception:
                logger.warning('playwright 代理无效，请切换代理')
                return False
            return True
        # 静态网页
        try:
            _ = requests.get(**static_dict_param)
            return True
        except Exception:
            logger.warning('requests 代理无效，请切换代理')
            return False


class Logger:
    @staticmethod
    def init_logger(logger_path: str, filter_word: str = '',
                    level: str = 'DEBUG', rotation: int = 10):
        """
        初始化日志，可以自定义日志等级，日志大小，还有指定关键字去输出到不同的日志文件
        Args:
            logger_path: 日志路径
            filter_word: 通过关键字来选择输出到不同的日志文件
            level: 日志等级
            rotation: 日志文件指定最大的存储大小，默认10MB

        Returns:
            返回logger日志对象
        """
        logger.add(logger_path, rotation=f'{rotation} MB',
                   level=level.upper(), filter=lambda x: filter_word in x['message'],
                   encoding="utf-8", enqueue=True, retention="30 days")
        logger.info(f'logger file load in: {logger_path}')
        return logger

    @staticmethod
    def init_comm_logger(logger_path: str, level: str = 'DEBUG'):
        """
        初始化通用的日志
        Args:
            logger_path: 日志文件路径
            level: 日志等级

        Returns:
            返回logger日志对象
        """
        logger.add(logger_path, rotation='10 MB',
                   level=level.upper(), encoding="utf-8",
                   enqueue=True, retention="30 days")
        logger.info(f'comm logger file load in: {logger_path}')
        return logger
