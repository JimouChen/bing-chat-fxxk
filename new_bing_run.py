# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
from comm.bing_chat import NewBingCrawler

if __name__ == '__main__':
    NewBingCrawler.search_from_prompt_json(prompt_path='./data/answer/answer.json')
