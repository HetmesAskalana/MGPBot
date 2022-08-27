#!/usr/bin/python3

from asyncore import read
from distutils import filelist
from distutils.command.upload import upload
from pickle import FALSE
from tabnanny import filename_only
from typing import ParamSpec
from webbrowser import get
from pathlib import *
import glob
import requests;
import re;
import os;
import time;
import json;

def get_text(pageid, section = "", spaceid = 'ZH'):
    workspace = WORKSPACE[spaceid]
    PARAMS = {
        'action': "parse",
        'pageid': pageid,
        'prop': 'wikitext',
        'section': section,
        'format': "json"
    }
    if section == "":
        PARAMS.pop('section')
    while True:
        try:
            res = workspace['SESSION'].post(url=workspace['URL'], data=PARAMS)
            data = res.json()
            break;
        except:
            time.sleep(1)
    #print(data)
    return data['parse']['wikitext']['*']

def get_text_as_title(title, section = "", spaceid = 'ZH'):
    workspace = WORKSPACE[spaceid]
    PARAMS = {
        'action': "parse",
        'page': title,
        'prop': 'wikitext',
        'section': section,
        'format': "json"
    }
    if section == "":
        PARAMS.pop('section')
    while True:
        try:
            res = workspace['SESSION'].post(url=workspace['URL'], data=PARAMS)
            data = res.json()
            break;
        except:
            time.sleep(1)
    #print(data)
    return data['parse']['wikitext']['*']


def login(spaceid = 'ZH'):
    workspace = WORKSPACE[spaceid]
    # Step 1: GET request to fetch login token
    PARAMS_0 = {
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    }

    R = workspace['SESSION'].get(url=workspace['URL'], params=PARAMS_0)

    DATA = R.json()

    LOGIN_TOKEN = DATA['query']['tokens']['logintoken']

    # Step 2: POST request to log in. Use of main account for login is not
    # supported. Obtain credentials via Special:BotPasswords
    # (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
    PARAMS_1 = {
        "action": "login",
        "lgname": workspace['lgname'],
        "lgpassword": workspace['lgpassword'],
        "lgtoken": LOGIN_TOKEN,
        "format": "json"
    }

    R = workspace['SESSION'].post(workspace['URL'], data=PARAMS_1)
    DATA = R.json()
    #print(DATA)

    # Step 3: GET request to fetch CSRF token
    PARAMS_2 = {
        "action": "query",
        "meta": "tokens",
        "format": "json"
    }

    R = workspace['SESSION'].get(url=workspace['URL'], params=PARAMS_2)
    DATA = R.json()
    print(DATA)
    workspace['csrftoken'] = DATA['query']['tokens']['csrftoken']
    return workspace['csrftoken']


def page_edit(pageid, text, minor = False, summary = "", spaceid = 'ZH', nocreate = False):
    workspace = WORKSPACE[spaceid]
    PARAMS = {
        "action": "edit",
        "pageid": pageid,
        "text": text,
        "token": workspace['csrftoken'],
        "tags": "Bot",
        "bot": True,
        "format": "json"
    }
    if minor:
        PARAMS["minor"] = True
    if summary != "":
        PARAMS["summary"] = summary
    if nocreate:
        PARAMS["nocreate"] = True,
    while True:
        try:
            res = workspace['SESSION'].post(workspace['URL'], data=PARAMS)
            data = res.json()
            break;
        except:
            time.sleep(1)
    if 'error' in res and res['error']['code'] == 'permissiondenied':
        PARAMS['token'] = workspace['csrftoken'] = login(spaceid)
        res = workspace['SESSION'].post(workspace['URL'], data=PARAMS)
        data = res.json()
    print(data)
    return data

def editAsTitle(title, text, minor = False, summary = "", spaceid = 'ZH', nocreate = False):
    workspace = WORKSPACE[spaceid]
    PARAMS = {
        "action": "edit",
        "title": title,
        "text": text,
        "token": workspace['csrftoken'],
        "tags": "Bot",
        "bot": True,
        "format": "json"
    }
    if minor:
        PARAMS["minor"] = True
    if summary != "":
        PARAMS["summary"] = summary
    if nocreate:
        PARAMS["nocreate"] = True,
    while True:
        try:
            res = workspace['SESSION'].post(workspace['URL'], data=PARAMS)
            data = res.json()
            break;
        except:
            time.sleep(1)
    if 'error' in res and res['error']['code'] == 'permissiondenied':
        PARAMS['token'] = workspace['csrftoken'] = login(spaceid)
        res = workspace['SESSION'].post(workspace['URL'], data=PARAMS)
        data = res.json()
    print(data)
    return data


def page_replace(pageid, find, replace, spaceid = 'ZH'):
    wikitext = get_text(pageid, "", spaceid)
    wikitext = wikitext.replace(find, replace)
    page_edit(pageid, wikitext, True, "文本替换 - 替换『" + find + "』为『" + replace + "』", spaceid)

def page_replace_as_title(title, find, replace, spaceid = 'ZH'):
    wikitext = get_text_as_title(title, "", spaceid)
    wikitext = wikitext.replace(find, replace)
    editAsTitle(title, wikitext, True, "文本替换 - 替换『" + find + "』为『" + replace + "』", spaceid)

def category_replace(pageid, find, replace, spaceid = 'ZH'):
    wikitext = get_text(pageid, "", spaceid)
    wikitext = re.sub(r"\[\[([Cc][Aa][Tt][Ee][Gg][Oo][Rr][Yy]|分[类類]|[Cc][Aa][Tt]):%s\]\]"%find, "[[Category:"+replace+"]]", wikitext);
    page_edit(pageid, wikitext, True, "分类替换 - 替换『Category:" + find + "』为『Category:" + replace + "』", spaceid);

def page_regsub(pageid, find, replace, spaceid = 'ZH'):
    wikitext = get_text(pageid, "", spaceid)
    wikitext = re.sub(find, replace, wikitext)
    page_edit(pageid, wikitext, True, "文本替换 - 替换『" + find + "』为『" + replace + "』", spaceid)

def add_category(pageid, category, spaceid = "COM"):
    wikitext = get_text(pageid, "", spaceid);
    wikitext = wikitext + "\n[[Category:%s]]" % category;
    page_edit(pageid, wikitext, True, "添加[[分类:%s]]" % category, "COM", True)

def add_categor_as_title(title, category, spaceid = "COM"):
    wikitext = get_text_as_title(title, "", spaceid);
    wikitext = wikitext + "\n[[Category:%s]]" % category;
    editAsTitle(title, wikitext, True, "添加[[分类:%s]]" % category, "COM", True)

def upload_file(igwarn = False):
    workspace = WORKSPACE['COM'];
    dirpath = "D:\\DATA\\萌百\\bot\\待上传文件\\"
    files = Path(dirpath)
    fileList = files.glob("*/*")
    listerr=[];
    for item in fileList:
        if item.is_file() and item.parent == files:
            print("%s是不是放错地方了?"%re.sub(r"D:\\DATA\\萌百\\bot\\待上传文件\\", "", str(item)));
            continue;
        if not item.is_file():
            continue
        category = re.sub(r"D:\\DATA\\萌百\\bot\\待上传文件\\", "", str(item.parent));
        filename = re.sub(r"D:\\DATA\\萌百\\bot\\待上传文件\\%s\\"%category, "", str(item));
        PARAMS = {
            "action": "upload",
            "format": "json",
            "smaxage": "0",
            "filename": filename,
            "text": "== 文件说明 ==\n[[Category:"+category+"]]\n\n== 授权协议 ==\n{{Copyright}}",
            "watchlist": "nochange",
            "token": workspace['csrftoken'],
            "tags": "Bot",
            "ignorewarnings": igwarn
        };
        FILE = {'file':(filename, open(item, 'rb'), 'multipart/form-data')};
        R = workspace['SESSION'].post(url=WORKSPACE['COM']['URL'], files=FILE, data=PARAMS);
        try:
            DATA = R.json();
            print("%s上传成功"%filename);
        except:
            listerr.append(filename + "报错");
    if(listerr):
        print(listerr);
    print("exit");

def mark_delete(page, reason, spaceid = "ZH"):
    editAsTitle(page, "<noinclude>{{即将删除|1="+ reason +"|user=UNC HA Bot}}</noinclude>", False, "挂删："+ reason, spaceid, True);

def delete_s(pages, reason, spaceid = "ZH", links = False):
    workspace = WORKSPACE[spaceid]
    if links:
        tmp1 = []
    for page in pages:
        if spaceid == "COM":
            page = re.sub(r"(c|C)(m|M):", "", page)
        if links:
            tmp = re.sub(r"(F|f)(I|i)(L|l)(e|E):", "", page)
            PARAMS = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": "insource:\"%s\""%tmp,
                "srnamespace": "0|10|6"
            }
            while(True):
                try:
                    res = workspace['SESSION'].post(url=workspace['URL'], data=PARAMS)
                    DATA = res.json();
                    break;
                except:
                    time.sleep(5);
            if DATA['query']['searchinfo']['totalhits'] != 0:
                tmp1.append(tmp);
                continue;
        mark_delete(page, reason, spaceid);
    if links:
        for item in tmp1:
            print("%s链入清理不完全"%item)

def protect_page(pageid, level, reason, expiry, spaceid = "ZH"):
    workspace = WORKSPACE[spaceid]
    PARAMS = {
        'action':"protect",
        'pageid': pageid,
        'protections': level, 
        'token': workspace['csrftoken'],
        'format':"json",
        'tags': "Bot",
        'expiry': expiry,
        "reason": reason 
    }
    while(True):
        try:
            res = workspace['SESSION'].post(url=workspace['URL'], data=PARAMS)
            DATA = res.json();
            break;
        except:
            time.sleep(5);
    print(DATA)

def category_protect(category, level, reason, expiry, spaceid = "ZH"):
    workspace = WORKSPACE[spaceid]
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:%s"%category,
        "cmlimit": "max"
    }
    while(True):
        try:
            res = workspace['SESSION'].get(url=workspace['URL'], data=PARAMS)
            DATA = res.json()
            break
        except:
            time.sleep(5)
    for page in DATA['query']['categorymembers']:
        protect_page(page['pageid'], level, reason, expiry, spaceid)

def category_redirect(src, to, spaceid = "ZH"):
    workspace = WORKSPACE[spaceid]
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:%s"%src,
        "cmlimit": "max"
    }
    while(True):
        try:
            res = workspace['SESSION'].post(url=workspace['URL'], data=PARAMS)
            DATA = res.json();
            break;
        except:
            time.sleep(5)
    for page in DATA['query']['categorymembers']:
        category_replace(page['pageid'], src, to, spaceid)

def readLine(path):
    file = open(path, 'r', encoding='utf-8');
    list1 = [];
    while True:
        tmp = file.readline();
        if not tmp:
            break;
        list1.append(tmp);
    return list1;

def movePage(src, to, reason, noredirect = True, sub = False, talk = True, spaceid = "ZH"):
    workspace = WORKSPACE[spaceid];
    PARAMS = {
        "action": "move",
        "format": "json",
        "from": src,
        "to": to,
        "reason": reason,
        "tags": "Bot",
        "token": workspace['csrftoken']
    };
    if noredirect:
        PARAMS["noredirect"] = True;
    if sub:
        PARAMS["movesubpages"] = True;
    if talk:
        PARAMS["movetalk"] = True;
    res = workspace['SESSION'].post(workspace['URL'], data=PARAMS);
    data = res.json();
    print(data);
    return data;


def main():
    login('COM');
    login("ZH");


if __name__ == '__main__':
    main()
