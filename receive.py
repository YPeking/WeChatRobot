# -*- coding:utf-8 -*-
# filename: receive.py

import xml.etree.ElementTree as ET
import json
import requests
import urllib2
import re
import random
import sys
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')


def parse_xml(web_data):
    if len(web_data) == 0:
        return None
    xmlData = ET.fromstring(web_data)
    msg_type = xmlData.find('MsgType').text
    if msg_type == 'text':
        return TextMsg(xmlData)
    elif msg_type == 'image':
        return ImageMsg(xmlData)
    elif msg_type == 'voice':
        return VoiceMsg(xmlData)

class Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text

class TextMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        content = xmlData.find('Content').text.encode('utf-8')
        if((u"段子" in content) or (u"笑话" in content)):
            self.Content = get_joke()
        elif(u"微博" == content):
            self.Content = get_weibo()
        elif(u"天气" == content):
            self.Content = get_weather()
        else:
            self.Content = get_tuling_answer(content).encode('utf-8')

class ImageMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.PicUrl = xmlData.find('PicUrl').text
        self.MediaId = xmlData.find('MediaId').text
        
class VoiceMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.MediaId = xmlData.find('MediaId').text
        self.Recognition = xmlData.find('Recognition').text
        if((u"段子" in self.Recognition) or (u"笑话" in self.Recognition)):
            self.Content = get_joke()
        elif(u"微博" in self.Recognition):
            self.Content = get_weibo()
        elif(u"天气" == self.Recognition):
            self.Content = get_weather()
        else:
            self.Content = get_tuling_answer(self.Recognition).encode('utf-8')
        

# 通过图灵机器人接口进行自动回复        
def get_tuling_answer(content):
    userId = '123456'
    inputText = {'text': content}
    # 替换成自己的图灵key
    key = 'tuling key'
    userInfo = {'apiKey':key, 'userId':userId}
    perception = {'inputText':inputText}
    data = {'perception':perception, 'userInfo':userInfo}
    
    url = 'http://openapi.tuling123.com/openapi/api/v2'
    response = requests.post(url=url, data=json.dumps(data))
    response.encoding = 'utf-8'
    result = response.json()
    answer = result['results'][0]['values']['text']
    return answer

# 自动获取糗事百科的段子
def get_joke():
    page_num = random.randint(1, 12)
    url = 'http://www.qiushibaike.com/hot/page/' + str(page_num)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent':user_agent}
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    content = response.read().decode('utf-8')
    pattern = re.compile('<div class="author clearfix">.*?<h2>(.*?)</h2>.*?<div.*?span>(.*?)</span>(.*?)<div class="stats">.*?"number">(.*?)</i>' ,re.S)
    items = re.findall(pattern,content)
    
    joke_num = random.randint(1, 15)
    joke_count = 0
    for item in items:
        haveImg = re.search("img", item[2])
        if not haveImg:
            joke_count += 1
            if joke_count == joke_num:
                strinfo = re.compile("<br/>")
                joke = strinfo.sub("", item[1])
                spaceinfo = re.compile("\n")
                joke_content = spaceinfo.sub("", joke)
                return joke_content
            
# 获取微博热搜
def get_weibo():
    url = 'http://s.weibo.com/top/summary?cate=realtimehot'
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent':user_agent}
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    content = response.read().decode('utf-8')
    bsObj=BeautifulSoup(content)
    
    i = 0
    weibo_content = ""
    # 获取热搜名称与链接
    for tag in bsObj.find_all("a", {"target":"_blank"}):
        weibo = re.findall(r"<a href=\"(.*?)\" target=\"_blank\">(.*?)</a>" ,str(tag))
        (weibo_url, weibo_title) = weibo[0]
        if("<img alt=" in weibo_title):
            nPos = weibo_title.index(" <img alt=")
            weibo_title = weibo_title[0:nPos]
        weibo_url = "https://s.weibo.com" + weibo_url
        weibo_link = "<a href=\"%s\">%s</a>" % (weibo_url, weibo_title)
        weibo_content = weibo_content + weibo_link + "\n\n"
        i += 1
        if i==6:
            break
    return weibo_content

# 获取北京天气
def get_weather():
    # 天气链接
	weatherJsonUrl = "http://wthrcdn.etouch.cn/weather_mini?city=北京"
	response = requests.get(weatherJsonUrl) 
    
	weather_content = ""
	#将json文件格式导入成python的格式
	weatherData = json.loads(response.text)
	# 今日最高温度与最低温度、风力信息
	total_info = weatherData['data']['forecast'][0]['type']
	high_temperature = weatherData['data']['forecast'][0]['high'][3:]
	low_temperature = weatherData['data']['forecast'][0]['low'][3:]
	fengli  = weatherData['data']['forecast'][0]['fengli'][9:]
	wind_info = weatherData['data']['forecast'][0]['fengxiang'] + "  " + fengli[:-3]
	today_info = "今天    " +  total_info + "  " + high_temperature +  "~" + low_temperature + "\n              " + wind_info

	# 明天最高温度与最低温度、风力信息
	total_info = weatherData['data']['forecast'][1]['type']
	high_temperature = weatherData['data']['forecast'][1]['high'][3:]
	low_temperature = weatherData['data']['forecast'][1]['low'][3:]
	fengli  = weatherData['data']['forecast'][1]['fengli'][9:]
	wind_info = weatherData['data']['forecast'][1]['fengxiang'] + "  " + fengli[:-3]
	tomorrow_info = "明天    " +  total_info + "  " + high_temperature +  "~" + low_temperature + "\n              " + wind_info
	# 后天最高温度与最低温度、风力信息
	total_info = weatherData['data']['forecast'][2]['type']
	high_temperature = weatherData['data']['forecast'][2]['high'][3:]
	low_temperature = weatherData['data']['forecast'][2]['low'][3:]
	fengli  = weatherData['data']['forecast'][2]['fengli'][9:]
	wind_info = weatherData['data']['forecast'][2]['fengxiang'] + "  " + fengli[:-3]
	last_info = "后天    " +  total_info + "  " + high_temperature +  "~" + low_temperature + "\n              " + wind_info

	# 建议
	suggest = "          " + weatherData['data']['ganmao']
	weather_content = today_info + "\n" + tomorrow_info + "\n" + last_info + "\n\n" + suggest
	
	return weather_content




