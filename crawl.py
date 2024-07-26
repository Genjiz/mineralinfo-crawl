from lxml import etree
from time import sleep
import json
from tqdm import tqdm
import requests
import os
import time
from bs4 import BeautifulSoup
import json
import codecs
from urllib.parse import unquote
from urllib.parse import quote

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Authorization': 'null',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json; charset=utf-8',
    'Host': 'www.mineralinfo.org.cn',
    # 'Origin': 'https://www.inindex.com',
    'Referer': 'http://www.mineralinfo.org.cn/',
    'sec-ch-ua': '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42'
}

classList = [
    "modern",
    "classical",
    "medicine",
    "ancient",
    "new",
    "structure",
    "international"]

classCnList = [
    "中国产出的矿物种类",
    "中国特色矿物晶体",
    "药用矿物",
    "古籍记载矿物",
    "中国发现的新矿物",
    "中国地质博物馆矿物种类",
    "世界矿物种(IMA)"
]

urlList = ["http://www.mineralinfo.org.cn/index.php?option=com_gmc_functiondb&task=getMatchArray",
           "http://www.mineralinfo.org.cn/index.php?option=com_gmc_functiondb&task=getMatchArray&type=classical",
           "http://www.mineralinfo.org.cn/index.php?option=com_gmc_functiondb&task=getMatchArray&type=medicine",
           "http://www.mineralinfo.org.cn/index.php?option=com_gmc_functiondb&task=getMatchArray&type=ancient",
           "http://www.mineralinfo.org.cn/index.php?option=com_gmc_functiondb&task=getMatchArray&type=new",
           "http://www.mineralinfo.org.cn/index.php?option=com_gmc_functiondb&task=getMatchArray&type=structure",
           "http://www.mineralinfo.org.cn/index.php?option=com_gmc_functiondb&task=getMatchArray&type=international"]

last_url = "http://www.mineralinfo.org.cn/index.php?option=com_gmc_functiondb&task=complexQuery&sg=1&keywrods="


def create_fold(path):
    if not os.path.exists(path):
        os.makedirs(path)

def url_search(htmlContent,className):
    soup = BeautifulSoup(htmlContent, 'html.parser')
    if className=="classical":
        new_className = "search-modern"
    else:
        new_className = "search-"+className
    search_div = soup.find('div', class_=new_className)
    checkbox_elements = search_div.find_all('input', type='checkbox')
    key_str = ""
    for i, checkbox in enumerate(checkbox_elements):
        if i != 0:
            key_str += checkbox.get('value') + ','
    return key_str

def url_name(cnName):
    encoded_cnName = quote(cnName)
    encodeded_cnName = quote(encoded_cnName)
    return encodeded_cnName

def parse_first_url(newurl,item):
    try:
        newhtml = requests.get(newurl, params=headers, timeout=50)
        htmlContent = newhtml.text
        return htmlContent
    except Exception as e:
        with open('error_get_page.txt', 'a+', encoding='utf-8') as ef:
            ef.write('first_url: {}\n'.format(item['cn_name'], e))
        return None

def parse_second_url(last_last_url,item):
    try:
        lasthtml = requests.get(last_last_url, params=headers, timeout=50)
        content = json.loads(lasthtml.text.lstrip(codecs.BOM_UTF8.decode('utf-8')))['data']
        return content
    except Exception as e:
        with open('error_get_page.txt', 'a+', encoding='utf-8') as ef:
            ef.write('second_url: {}\n'.format(item['cn_name'], e))
        return None
def main():
    create_fold(path='待解析json文件')


    for i in range(len(urlList)):
        need = []

        # 查询当前类别下所有矿物
        url = urlList[i]
        html = requests.get(url, params=headers, timeout=50)
        text = html.text.lstrip(codecs.BOM_UTF8.decode('utf-8'))
        dicts = json.loads(text)

        # 遍历当前类别下所有矿物
        for value in dicts.values():
            for item in tqdm(value):
                # 查询当前矿物详情
                newurl = "http://www.mineralinfo.org.cn/index.php?template=gmc_map&option=com_gmc_map&sg=1&sort=" + classList[i] + "_mineral&mineral=" + item['cn_name']
                htmlContent = parse_first_url(newurl,item)
                if htmlContent==None:
                    continue

                search = url_search(htmlContent,classList[i])
                name = url_name(item['cn_name'])

                last_last_url = last_url+name+"&type="+classList[i]+"_mineral&search="+search+"&page=1"
                content = parse_second_url(last_last_url,item)
                if content==None:
                    continue

                need_data = {'url': newurl,
                             'name': item['cn_name'],
                             'source': classCnList[i],
                             'content': content,
                             }
                need.append(need_data)

                print(last_last_url)
        with open('待解析json文件/测试结果_'+classCnList[i]+'.json', 'w', encoding='utf-8') as file:
                    # 确保指定ensure_ascii为False以支持中文字符
                    json.dump(need, file, ensure_ascii=False, indent=4)





if __name__ == "__main__":
    main()
