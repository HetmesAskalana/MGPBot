#群里先毛一个来用着
#!/usr/bin/python3

import requests;
import re;
import time;

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
    print(data)
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
    
    PARAMS_1 = {
        "action": "login",
        "lgname": workspace['lgname'],
        "lgpassword": workspace['lgpassword'],
        "lgtoken": LOGIN_TOKEN,
        "format": "json"
    }

    R = workspace['SESSION'].post(workspace['URL'], data=PARAMS_1)
    DATA = R.json()
    PARAMS_2 = {
        "action": "query",
        "meta": "tokens",
        "format": "json"
    }

    R = workspace['SESSION'].get(url=workspace['URL'], params=PARAMS_2)
    DATA = R.json()
    #print(DATA)
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
    login('ZH');
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:蔚蓝档案其它图片",
        "cmlimit": "max"
    };
    res = WORKSPACE['COM']['SESSION'].get(url=WORKSPACE['COM']['URL'], params=PARAMS);
    data = res.json();
    members = data['query']['categorymembers'];

    for page in members:
        page_replace(page['pageid'], "Category:蔚蓝档案其它图片", "Category:蔚蓝档案其他图片", "ZH");



if __name__ == '__main__':
    main()
