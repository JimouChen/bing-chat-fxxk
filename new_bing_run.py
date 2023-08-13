# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
from comm.bing_chat import NewBingCrawler

if __name__ == '__main__':
    # NewBingCrawler.search_from_prompt_json(prompt_path='./data/answer/answer.json')
    print(NewBingCrawler.search('你好，请你介绍一下你自己吧'))
