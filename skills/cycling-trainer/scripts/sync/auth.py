"""
认证模块

负责登录 session 管理，用于获取 Strava 同步数据的浏览器模拟方式
"""

import requests
import sys

BASE_URL = "https://intervals.icu"


def login_session(email, password):
    """
    模拟网页登录获取 session
    
    Args:
        email: intervals.icu 邮箱
        password: intervals.icu 密码
    
    Returns:
        requests.Session: 已登录的 session
    
    Raises:
        SystemExit: 登录失败时退出
    """
    session = requests.Session()
    login_data = {
        'email': email,
        'password': password,
        'deviceClass': "desktop"
    }
    resp = session.post(f'{BASE_URL}/api/login', data=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code}", file=sys.stderr)
        sys.exit(1)
    return session
