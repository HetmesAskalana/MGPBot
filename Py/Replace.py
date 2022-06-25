#!/usr/bin/python3

from distutils import filelist
from distutils.command.upload import upload
from pickle import FALSE
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
    res = workspace['SESSION'].get(url=workspace['URL'], params=PARAMS)
    data = res.json()
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
    res = workspace['SESSION'].get(url=workspace['URL'], params=PARAMS)
    data = res.json()
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


def page_edit(pageid, text, minor = False, summary = "", spaceid = 'ZH'):
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
    res = workspace['SESSION'].post(workspace['URL'], data=PARAMS)
    data = res.json()
    if 'error' in res and res['error']['code'] == 'permissiondenied':
        PARAMS['token'] = workspace['csrftoken'] = login(spaceid)
        res = workspace['SESSION'].post(workspace['URL'], data=PARAMS)
        data = res.json()
    print(data)
    return data

def editAsTitle(title, text, minor = False, summary = "", spaceid = 'ZH'):
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
    res = workspace['SESSION'].post(workspace['URL'], data=PARAMS)
    data = res.json()
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

def page_regsub(pageid, find, replace, spaceid = 'ZH'):
    wikitext = get_text(pageid, "", spaceid)
    wikitext = re.sub(find, replace, wikitext)
    page_edit(pageid, wikitext, True, "文本替换 - 替换『" + find + "』为『" + replace + "』", spaceid)

def upload_file(igwarn = False):
    workspace = WORKSPACE['COM'];
    fileList = os.listdir("");
    list1=[];
    for fileName in fileList:
        PARAMS = {
            "action": "upload",
            "format": "json",
            "smaxage": "0",
            "filename": fileName,
            "text": "[[Category:秤亚津子语音]]",
            "watchlist": "nochange",
            "token": workspace['csrftoken'],
            "tags": "Bot",
            "ignorewarnings": igwarn
        };
        FILE = {'file':(fileName, open(""+fileName, 'rb'), 'multipart/form-data')};
        R = workspace['SESSION'].post(url=WORKSPACE['COM']['URL'], files=FILE, data=PARAMS);
        DATA = R.json();
        print(DATA);
        '''if DATA['upload']['result'] == 'Success':
            print(fileName + "已成功上传");
        else:
            print(fileName + "上传失败");
            print(DATA);'''
    print("exit");

def delete_s(pages, reason, spaceid = "ZH"):
    for page in pages:
        editAsTitle(page, "<noinclude>{{即将删除|1="+ reason +"|user=HetmesAskalana}}</noinclude>", False, "挂删："+ reason, spaceid);
        time.sleep(8)

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

    '''pagelist = readLine("");
    delete_s(pagelist, "移动导致的重复上传", "COM");'''

    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": "BA_V_Atsuko",
        "srnamespace": "6",
        "srlimit": "max"
    }
    res = WORKSPACE['COM']['SESSION'].get(url=WORKSPACE['COM']['URL'], params=PARAMS);
    data = res.json();
    members = data['query']['search'];
    print(members);

    '''for page in members:
        page_replace(page['pageid'], "Category:蔚蓝档案语音", "Category:秤亚津子语音", 'ZH')'''
        



if __name__ == '__main__':
    main()
