#!/usr/bin/python3

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


def page_replace(pageid, find, replace, spaceid = 'ZH'):
    wikitext = get_text(pageid, "", spaceid)
    wikitext = wikitext.replace(find, replace)
    page_edit(pageid, wikitext, True, "文本替换 - 替换『" + find + "』为『" + replace + "』", spaceid)


def page_regsub(pageid, find, replace, spaceid = 'ZH'):
    wikitext = get_text(pageid, "", spaceid)
    wikitext = re.sub(find, replace, wikitext)
    page_edit(pageid, wikitext, True, "文本替换 - 替换『" + find + "』为『" + replace + "』", spaceid)



def main():
    login('COM');
    workspace = WORKSPACE['COM'];
    fileList = os.listdir(FILEPATH);
    list1=[];
    for name in fileList:
        if os.path.splitext(name)[1] != ".jpg":
            continue;
        list1.append(os.path.splitext(name)[0]+os.path.splitext(name)[1]);
    for fileName in fileList:
        PARAMS = {
            "action": "upload",
            "format": "json",
            "smaxage": "0",
            "filename": fileName,
            "text": "[[Category:蔚蓝档案CG]]",
            "watchlist": "nochange",
            "token": workspace['csrftoken'],
            "tags": "Bot"
        };
        FILE = {'file':(fileName, open(FILEPATH+fileName, 'rb'), 'multipart/form-data')};
        R = workspace['SESSION'].post(url=WORKSPACE['COM']['URL'], files=FILE, data=PARAMS);
        DATA = R.json();
        if DATA['upload']['result'] == 'Success':
            print(fileName + "已成功上传");
        else:
            print(fileName + "上传失败");
            print(DATA);
    print("exit");
        

if __name__ == '__main__':
    main()
