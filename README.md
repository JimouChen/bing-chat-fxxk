# bing-chat-fxxk

## 环境

- 克隆到本地

    `git clone https://github.com/JimouChen/bing-chat-fxxk`
- 安装依赖

    `pip3 install -r requirements.txt`
- Playwright注意
  - playwright的安装比较特殊，这里可参考一下网上
    在上面正常安装完之后，记得 `python -m playwright install`，这一句是下载对应的浏览器内核
  - 本代码是以有痕谷歌浏览的方式启动，具体可在配置参数修改
  - 本代码是在MacOS下完成，若是Windows下，且使用有痕的方式，那么对应的 `User Data Dir`要修改，具体可在浏览器用：`chrome://version/`查看
    > 下面是Mac的user data dir的地址：
    `launch_options['user_data_dir'] = r'~/Library/Application Support/Google/Chrome/Default'`
    

## 启动

### 使用方法

- 单条
```python
NewBingCrawler.search('你好，请你介绍一下你自己吧')
```
- 多条
  - 把prompt都写到一个json文件

```python
NewBingCrawler.search_from_prompt_json(prompt_path='./data/answer/answer.json')
```

- 直接运行 `bing_chat.py` 即可
  `python3 bing_chat.py`
- 或者PyCharm直接运行


## 效果

- 见：[演示视频](https://www.bilibili.com/video/BV1Lm4y1W7hU/?spm_id_from=333.999.0.0&vd_source=f211b55f6edc2cc09cd5609cdd5f5cab)


## 注意

- 若链接不可用，则换一个链接，若出现连接网络的问题，则可能是该网站访问请求量较大，暂时用不了
- 一般来说，不需要科学上网即可访问
- 更换网络可参考：[不用代理的Bing镜像站](https://github.com/Nothingness-Void/Public-bing-chatgpt-proxy)
- 对于NewBing镜像url，请控制好每天请求的数量，目前测试过一天几百条不是问题


## Author

- @JimouChen/Neaya
