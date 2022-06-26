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

def category_replace(pageid, find, replace, spaceid = 'ZH'):
    wikitext = get_text(pageid, "", spaceid)
    wikitext = re.sub(r"\[\[(Category|分类):%s\]\]"%find, "[[Category:"+replace+"]]", wikitext);
    page_edit(pageid, wikitext, True, "分类替换 - 替换『Category:" + find + "』为『Category:" + replace + "』", spaceid);

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
        "list": "categorymembers",
        "cmtitle": "Category:蔚蓝档案语音",
        "cmnamespace": "6",
        "cmlimit": "1"
    }
    res = WORKSPACE['COM']['SESSION'].get(url=WORKSPACE['COM']['URL'], params=PARAMS);
    data = res.json();
    members = data['query']['categorymembers'];
    #print(members);
    names = {
        'Shiroko' : '砂狼白子', 'Hoshino' : '小鸟游星野', 'Ayane' : '奥空绫音', 'Serika' : '黑见茜香' , 'Nonomi' : '十六夜野乃美',#阿拜多斯
        'Iroha': '枣伊吕波', 'Hina':'空崎阳奈', 'Ako':'天雨亚子', 'Iori':'银镜伊织', 'Chinatsu': '日野宫千夏', 'Aru': '陆八魔亚瑠', 'Kayoko':'鬼方佳世子', 'Mutsuki': '浅黄无月', 'Haruka': '伊草遥香', 'Haruna': '黑馆羽留奈', 'Izumi': '狮子堂泉', 'Zunko': '赤司淳子', 'Akari': '鳄渊亚伽里', 'Fuuka': '爱清风华', 'Juri': '牛牧茱莉', 'Sena': '冰室濑奈', #格黑娜
        'Yuuka': '早濑优香', 'Midori':'才羽绿', 'Yuuzu': '花冈柚子', 'Aris': '天童爱丽丝', 'Momoi': '才羽桃井', 'Hibiki': '猫冢响', 'Utaha':'白石咏叶', 'Kotori':'丰见亚都梨', 'Chihiro': '各务千寻', 'Maki': '小涂真纪', 'Hare': '小钩晴', 'Kotama':'音濑小玉', 'Karin': '角楯花凛', 'Neru': '美甘宁瑠', 'Akane': '室笠朱音', 'Asuna': '一之濑明日奈', 'Sumire': '乙花堇', 'Eimi': '和泉元英美',#千年
        'Hifumi': '阿慈谷日步美', 'Azusa': '白洲梓', 'Koharu': '下江小春', 'Hanako': '浦和花子', 'Tsurugi': '剑先弦生', 'Mashiro': '静山麻白', 'Hasumi': '羽川莲实', 'Natsu': '柚鸟夏', 'Airi': '栗村爱莉', 'Yoshimi': '伊原木喜美', 'Hanae': '朝颜花绘', 'Serina': '鹫见芹奈', 'Ui': '古关忧', 'Shimiko': '圆堂志美子', 'Suzumi': '守月铃美', 'Hinata': '若叶日向', 'Mari': '伊落玛丽',#三一
        'Shizuko':'河和静子','Pina':'朝比奈菲娜','Mimori':'水羽三森','Kaede':'勇美枫','Tsubaki':'春日椿','Chise':'和乐知世','Izuna':'久田伊树菜','Tsukuyo':'大野筑夜','Michiru':'千鸟满','Wakamo':'狐坂若藻',#百鬼
        'Shun':'春原旬','Saya':'药子沙耶','Cherino':'连河洁莉诺','Marina':'池仓玛丽娜','Michiru':'佐城智惠','Nodoka':'天见和香',#山海经
        'Kirino':'中务桐乃','Fubuki':'合欢垣吹雪',#瓦尔基里
        'Miyako':'月雪宫子','Saki':'空井咲','Miyu':'霞泽美游',#SRT
        'Hiyori':'槌永日和','Misaki':'戒野美咲','Atsuko':'秤亚津子',#阿里乌斯
        'Miku':'初音未来'#其他
    };
    flag = [];

    for page in members:
        tmp = page['title'].split(" ");
        category_replace(page['pageid'], "蔚蓝档案语音", names[tmp[2]]+"语音", 'COM');
        '''if not flag[names[tmp[2]]]:
            PARAMS = {
                "action": "query",
                "format": "json",
                "prop": "revisions",
                "titles": "Category:"+names[tmp[2]]+"语音",
                "rvprop": "content"
            }
            res = WORKSPACE['COM']['SESSION'].get(url=WORKSPACE['COM']['URL'], params=PARAMS);
            data = res.json();
            if data['query']['pages']['-1']:
                wikitext = "{{catnav|蔚蓝档案|蔚蓝档案语音}} \n {{catnav|人物|...|蔚蓝档案中角色|"+names[tmp[2]]+"}} \n [[Category:蔚蓝档案语音]] \n [[Category:"+names[tmp[2]]+"| ]]";
                editAsTitle("Category:"+names[tmp[2]]+"语音", wikitext, False, "创建分类: Category"+names[tmp[2]], "COM");
                flag[names[tmp[2]]] = True;'''


if __name__ == '__main__':
    main()
