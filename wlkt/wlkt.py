# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os.path
import sys
import time

__author__ = "memory-yancy <root@memory-yancy.com> "
# fork by shylocks <shylocksyang@gmail.com>
# http://wlkt.nuist.edu.cn/ will produce redirection, so get latest url in time.
http_headers = { 'Accept': '*/*','Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'}
rs = requests.get('http://wlkt.nuist.edu.cn/',headers=http_headers)
session = requests.session()
base_url = rs.url

def get_captcha():
    """
    Get captcha from NUIST wlkt.

    If current environment installed PIL module, this method will use it to display captcha automatically.
    However, if PIL doesn't find and then tell captcha image location to input its value manually.

    Returns
    -------
    nuist_captcha: str
        Return wlkt system captcha's content, only four digitals.
    """
    soup = BeautifulSoup(requests.get(base_url,headers=http_headers).text, "html.parser")
    captcha_url = base_url.replace('default.aspx',soup.iframe['src'])
    file_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(file_dir + '/nuist-captcha.gif', 'wb') as f:
        f.write(session.get(captcha_url,headers=http_headers).content)
    try:
        import PIL.Image
        print("WARNING: will pop a window to display captcha content and you should remember it, we will reuse it.")
        image = PIL.Image.open(file_dir + '/nuist-captcha.gif')
        image.show()
        # Close image file pointer and release its memory
        image.close()
    except ImportError:
        print("WARNING: cann't find PIL(Python Image Library) to identify captcha content, so please look at "
        "captcha in [%s" % (file_dir + "/nuist-captcha.gif]") + " file.\n", flush = True)

    nuist_captcha = input('INFO: please input captcha content [4-numbers] ---> ')
    while len(nuist_captcha) != 4:
        print('ERROR: please input 4 captcha', flush = True)
        nuist_captcha = input('INFO: please input captcha content [4-numbers] ---> ')

    return nuist_captcha

def is_login():
    """
    Judge login status to decrease unuseful login.

    Returns
    -------
    flag: bool

        True is successful, False isn't successful.
    """
    logined_url = "http://wlkt.nuist.edu.cn/(S(1mgpqz332kcepuyovyeycj45))/public/newslist.aspx"
    login_flag = True

    if not "yzm.aspx" in session.get(logined_url).text:
        return login_flag
    else:
        login_flag = False
        return login_flag

def login(username, password, role='RadioButton3', action='%E7%99%BB%E5%BD%95'):
    """
    Use student number and password to login system, only support student role. And no plan to
    add other role to login.

    Parameters:
    ----------
    username: student number, the length is 11 and str type.
    password: system password, the length is 8 and str type.
    role: only support student role, its value is only RadioButton3.
    action: submit button, use unicode.

    Return:
    ------
    nuist: requests.sessions.Session object.

        requests.sessions.Session object if ok, and then get other pages.

    nuist: None
        None if failed.
    """
    if len(username) != 11:
        raise ValueError("The %s argument don't 11 numbers." % username)
    # __VIEWSTATE parameter's value is fixed, and it must be exist. Or dataset don't submit.
    params = {'__VIEWSTATE': '', 'TextBox1': username, 'TextBox2': password, 'js': role, 'Button1': action}
    login_captcha = get_captcha()
    params['TxtYZM'] = login_captcha

    nuist = session.get(base_url, headers=http_headers , params = params, timeout = 20)
    os.remove(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/nuist-captcha.gif')
    #print(session.cookies.get_dict())
    if str(session.cookies.get_dict()).find('MYWEBAPP.ASPXAUTH'):
        print('Login Successfully!')
        return session
    if '(' + username + ')' in nuist.text and username[0:4] in nuist.text:
        return session
    elif 'Error.htm' in nuist.url:
        print("\nINFO: system run errors! Sorry, possible reasons look like below following.\n\
    1) Progrom run error!\n\
    2) The number of people visiting the site is so high that it has reached the maximum connection limit!\n\
        Sorry ...\n")
        return None
    elif 'alert' in nuist.text and r'<html>' in nuist.text:
        print(u"\nERROR: captcha input wrong, please check it(验证码不正确!).")
        return None
    elif 'alert' in nuist.text:
        print(u"\nERROR: Student-Number or Password wrong and check it(用户名或密码不正确!).")
        return None
    else:
        print('\nERROR: login failed for some reason and try again wait a minute.')
        return None

def quit():
    """
    Call method while wanting to quit system.

    Return:
    ------
    flag: bool

        True if quit successfully and session closed.
    """
    if 'default.aspx' in session.get(base_url + '/' + 'default.aspx?action=quit').url:
        return True

if __name__ == '__main__':
    username = input('INFO: please input your Student Number ---> ')
    password = input('INFO: please input your Password ---> ')
    login(username,password)
