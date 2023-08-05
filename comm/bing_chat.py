# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
from comm.utils import *


class NewBingCrawler:
    # url = 'https://ai.nothingnessvoid.tech/web/index.html#/'
    url = 'https://bing.nvoid.live/'
    close_flag_selector = 'body > div.n-modal-container > div > div > div.n-scrollbar-container > div > div.n-card.n-modal.w-11\/12.lg\:w-\[900px\] > div.n-card-header > button > i > svg'
    max_conversation_times = 30 # 默认是30，30次对话就刷新页面

    @classmethod
    def search(cls, prompt: str):
        with sync_playwright() as sp:
            browser, context, page = BrowserController.load(sp,
                                                            browser_type='chromium',
                                                            # browser_type='edge',
                                                            headless=False)
            page.goto(cls.url, timeout=10000)
            page.click('#tone-options > li:nth-child(1) > button')
            page.locator('#searchbox').fill(prompt, timeout=1000)
            page.wait_for_timeout(500)
            page.keyboard.press('Enter')
            ans_text = ''
            while True:
                if 'aria-live="polite"' in page.content():
                    soup = BeautifulSoup(page.content(), 'lxml')
                    res = soup.findAll('div', {'aria-live': 'polite'})[-1]
                    ans_text = res.text[7:] if res else ''
                    break
                page.wait_for_timeout(2000)
            logger.debug(f'Q: {prompt}')
            logger.success(f'A: {ans_text}\n\n')
            BrowserController.close(context, browser)
            return ans_text

    @classmethod
    def search_from_prompt_json(cls, prompt_path: str):
        prompt_data = FileUtils.load_json(prompt_path)

        with sync_playwright() as sp:
            browser, context, page = BrowserController.load(sp,
                                                            browser_type='chromium',
                                                            # browser_type='edge',
                                                            headless=False)
            page.goto(cls.url, timeout=10000)
            # if cls.close_flag_selector in page.content():
            page.click(cls.close_flag_selector)
            page.click('#tone-options > li:nth-child(1) > button')
            temp_last_ans = ''

            for idx, item in enumerate(prompt_data):
                if idx % cls.max_conversation_times == 0 and idx != 0:
                    page.reload(wait_until="load")  # 重新加载页面并等待加载完成

                prompt = item['Q']
                page.locator('#searchbox').fill(prompt, timeout=1000)
                page.wait_for_timeout(500)
                page.keyboard.press('Enter')
                page.wait_for_timeout(2000)
                ans_text = ''
                while True:
                    if 'aria-live="polite"' in page.content():
                        soup = BeautifulSoup(page.content(), 'lxml')
                        res = soup.findAll('div', {'aria-live': 'polite'})[-1]
                        ans_text = res.text[7:] if res else ''
                        if ans_text != temp_last_ans and ans_text != '':
                            break
                    page.wait_for_timeout(2000)

                temp_last_ans = ans_text
                prompt_data[idx]['A'] = ans_text
                FileUtils.write2json(prompt_path, prompt_data)
                logger.debug(f'Q: {prompt}')
                logger.success(f'A: {ans_text}\n\n')
                page.wait_for_timeout(1000)

            BrowserController.close(context, browser)
