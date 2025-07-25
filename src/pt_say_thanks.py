#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PT 站点自动感谢脚本

功能：
- 自动解析指定页码范围内的种子 ID
- 批量向种子发送感谢

使用方式：
1. 修改 config.env 中的配置信息
2. 直接运行脚本: python pt_say_thanks.py

注意事项：
- 需要提前登录获取有效的 Cookie
- 请遵守站点的请求频率限制，避免被封禁
- 建议在非高峰期运行

author : tudan110
date   : 2024-02-04 16:55:17
version: 1.0
"""
import logging
import os
import re
import time
from pathlib import Path
from typing import Set
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('../config/config.env')

# 配置常量
PT_DOMAIN = os.getenv('PT_DOMAIN', 'ptcafe.club')
PT_COOKIE = os.getenv('PT_COOKIE', '')
PAGE_START = int(os.getenv('PAGE_START', 0))
PAGE_END = int(os.getenv('PAGE_END', 10))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 60))
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', 0.5))
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0')

# 日志配置
LOG_DIR = Path(__file__).parent.parent / 'logs'  # 获取脚本所在目录的上级目录中的logs
LOG_FILE = LOG_DIR / 'pt_say_thanks.log'


def setup_logger():
    """配置并返回一个带有文件和终端处理器的logger"""

    # 确保日志目录存在
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 文件处理器
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # 终端处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()


def get_torrent_ids(page_url: str, headers: dict) -> Set[str]:
    """从页面URL提取种子ID"""

    try:
        # 从URL中提取页码
        page_num = re.search(r'page=(\d+)', page_url).group(1)

        response = requests.get(
            page_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        if not response.text:
            logger.warning(f"第 {page_num} 页返回空内容")
            return set()

        torrent_ids = set(re.findall(r'href="details\.php\?id=(\d+)&amp;hit=1', response.text))
        logger.info(f"第 {page_num} 页解析到 {len(torrent_ids)} 个种子")
        return torrent_ids

    except requests.exceptions.RequestException as e:
        logger.error(f"获取第 {page_num} 页失败: {str(e)}")
        return set()


def say_thanks(torrent_id: str, count: int, thanks_url: str, headers: dict) -> bool:
    """为指定种子ID说谢谢"""

    data = {'id': str(torrent_id)}

    try:
        response = requests.post(
            thanks_url,
            headers=headers,
            data=data,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        logger.info(f"种子 #{count}; ID: {torrent_id} - 感谢表示成功")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"为种子ID {torrent_id} 说谢谢失败: {str(e)}")
        return False


def thank_batch(all_torrent_ids: Set[str], headers: dict, thanks_url: str):
    """批量向所有种子发送感谢"""

    failed_torrent_ids = set()  # 用于记录失败的种子ID
    # 为每个种子说谢谢
    for count, torrent_id in enumerate(all_torrent_ids, 1):
        success = say_thanks(torrent_id, count, thanks_url, headers)

        if not success:
            failed_torrent_ids.add(torrent_id)  # 记录失败的种子ID
            if REQUEST_DELAY > 0:
                logger.info(f"等待 {REQUEST_DELAY} 秒后继续...")
                time.sleep(REQUEST_DELAY)
    # 打印失败的种子 ID 集合
    if failed_torrent_ids:
        logger.warning(f"以下种子感谢失败: {failed_torrent_ids}")
        logger.info("提示：可以复制这些 ID 并遍历调用 say_thanks() 函数重试，"
                    "参考 /tests/test_pt_say_thanks.py test_retry_failed_torrent_ids 方法。")
    else:
        logger.info("所有种子感谢成功！")


def process_all_pages():
    """处理所有页面并为找到的所有种子说谢谢"""

    if not PT_COOKIE:
        logger.error("请在 config.env 中配置有效的 Cookie")
        return

    base_url = f'https://{PT_DOMAIN}'
    headers = {
        'Cookie': PT_COOKIE,
        'User-Agent': USER_AGENT,
        'Referer': base_url
    }

    parse_url = urljoin(base_url, '/torrents.php?inclbookmarked=0&incldead=1&spstate=0&page=')
    thanks_url = urljoin(base_url, '/thanks.php')

    page_urls = [f'{parse_url}{page}' for page in range(PAGE_START, PAGE_END + 1)]
    all_torrent_ids = set()

    logger.info(f"开始处理 {PT_DOMAIN} 的页面，第 {PAGE_START} 到 {PAGE_END} 页")

    # 收集所有种子ID
    for page_url in page_urls:
        logger.debug(f"正在处理页面: {page_url}")
        torrent_ids = get_torrent_ids(page_url, headers)
        all_torrent_ids.update(torrent_ids)

    if not all_torrent_ids:
        logger.warning("没有找到任何种子ID，请检查配置和页面内容")
        return

    logger.info(f"共找到 {len(all_torrent_ids)} 个种子，开始说谢谢...")

    thank_batch(all_torrent_ids, headers, thanks_url)

    logger.info("说谢谢完成")


if __name__ == "__main__":
    try:
        process_all_pages()
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}", exc_info=True)
