import os
import re
import time
import wget
import requests
from lanzou.api import LanZouCloud
from retry import retry


class InvalidStatus(Exception):
    """Base class for other exceptions"""
    pass


# cookie解析
def cookie_parse(cookies_str):
    cookie_dict = {}
    cookies = cookies_str.split(';')
    for cookie in cookies:
        cookie = cookie.split('=')
        cookie_dict[cookie[0]] = cookie[1]
    return cookie_dict


# 消息发送
def send_telegram(msg):
    url = 'https://api.telegram.org/bot'
    url += os.environ["TGAPI"]
    url += '/sendMessage'
    data = {'chat_id': os.environ["CHATID"], 'text': msg, 'parse_mode': 'html'}
    requests.post(url, data)


# 获取下载路径
def get_info():
    url = "https://api.github.com/repos/pineappleEA/pineapple-src/releases/latest"
    with requests.get(url) as r:
        # print(r)
        c1 = re.compile(r'"browser_download_url":"(.*?)"')
        c2 = re.compile(r'"tag_name":"(.*?)"')
        download_url = c1.findall(r.text)
        tag_name = c2.search(r.text)
        # print(download_url[1])
        # print(tag_name.group(1))
        return ["Windows-Yuzu-"+tag_name.group(1)+".zip", download_url[1]]


# 下载进度条
def bar_progress(current, total, width=40):
    percent = current / total
    len_str = 40
    bar_str = '>' * round(len_str * percent) + '=' * round(len_str * (1 - percent))
    print('\r{} {:.2f}%\t[{}] {:.1f}/{:.1f}MB'.format(
        "下载:", percent * 100, bar_str, current / 1048576, total / 1048576), end='')
    if total == current:
        print('')  # 下载完成换行


# 上传进度条
def show_progress(file_name, total_size, now_size):
    percent = now_size / total_size
    bar_len = 40  # 进度条长总度
    bar_str = '>' * round(bar_len * percent) + '=' * round(bar_len * (1 - percent))
    print('\r{} {:.2f}%\t[{}] {:.1f}/{:.1f}MB '.format(
        "上传:", percent * 100, bar_str, now_size / 1048576, total_size / 1048576), end='')
    if total_size == now_size:
        print('')  # 下载完成换行


# 上传lzCloud
@retry(InvalidStatus,delay=5,tries=3)
def upload(file_name, lzy):
    if lzy.upload_file(file_name, 3864551, callback=show_progress) != LanZouCloud.SUCCESS:
        raise InvalidStatus("上传失败,尝试重传!")
    else:
        print("上传成功!")


# 上传准备
def pre_upload(download_info):
    lzy = LanZouCloud()
    try:
        cookie = cookie_parse(os.environ["COOKIE"])
    except:
        cookie = cookie_parse("")

    if lzy.login_by_cookie(cookie) == LanZouCloud.SUCCESS:
        # print("lz login success!")
        if lzy.get_file_list("3864551")[0].name == download_info[0]:
            print("当前已是最新版本,无需重传.")
        else:
            print("下载最新版本"+download_info[0])
            wget.download(download_info[1], bar=bar_progress)
            print("开始上传.")
            upload(download_info[0], lzy)
    else:
        print("cookie 失效~~~")
        send_telegram("lz-sync cookie 失效!")


def main():
    info = get_info()
    pre_upload(info)


if __name__ == '__main__':
    main()
