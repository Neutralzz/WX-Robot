#coding=utf-8
import requests
import os
import json,wave
import urllib, pycurl, base64
from pydub import  AudioSegment
from PIL import Image

#{'maptype': 0, 'poiname': '大运村公寓', 'y': 116.344643, 'scale': 16, 'x': 39.97773, 'label': '北京市海淀区知春路29号'}
#baidu map api iIg5q0cxNn7yqQbr3AcqhljDe8qqchYY
#baidu audio rec api 
#	apiKey = 'eQvgGAHLKDfeouUuGgsxYy3W'
#	secretKey = '4ea58fc8186544bf044cc2fb02781e46'
global gaodeApi
gaodeApi = 'd4c095c90777fd166c824a06abcc42ae'

def resize_image(filein, fileout):
	img = Image.open(filein)
	w,h = img.size
	width = 400
	height = int(h*width/w)
	out = img.resize((width, height),Image.ANTIALIAS) #resize image with high-quality
	out.save(fileout)

def get_adcode(location):
	x = str(location['x'])
	y = str(location['y'])
	apiUrl = 'http://restapi.amap.com/v3/geocode/regeo?key=%s&location=%s,%s'%(gaodeApi,y,x)
	r = requests.get(apiUrl).text
	adcode = json.loads(r)['regeocode']['addressComponent']['adcode']
	return adcode

def get_weather(location):
	adcode = get_adcode(location)
	apiUrl = 'http://restapi.amap.com/v3/weather/weatherInfo?key=%s&city=%s'%(gaodeApi,adcode)
	r = json.loads(requests.get(apiUrl).text)
	pos = r['lives'][0]['province'] + r['lives'][0]['city']
	weather = r['lives'][0]['weather']
	temperature = r['lives'][0]['temperature']
	winddir = r['lives'][0]['winddirection']
	windpow = r['lives'][0]['windpower']
	humidity = r['lives'][0]['humidity']
	reporttime = r['lives'][0]['reporttime']
	replys = '您的位置：'+pos+'\n天气：'+weather+'\n气温：'+temperature+'摄氏度\n风向：'+winddir+ \
	'\n风力：'+windpow+'级\n空气湿度：'+humidity+'\n记录时间：'+reporttime
	return replys

def get_trafficinfo(location):
	print(location)
	x = str(location['x'])
	y = str(location['y'])
	#print("trafficinfo %s,%s"%(y,x))
	apiUrl = 'http://restapi.amap.com/v3/traffic/status/circle?location=%s,%s&key=%s'%(y,x,gaodeApi)
	r = json.loads(requests.get(apiUrl).text)
	#print("location(%s,%s) "%(y,x))
	#print("-> trafficinfo : "+str(r))
	return r['trafficinfo']['description'].replace('；','\n').replace('。','\n')
	
def get_around(location):
	x = str(location['x'])
	y = str(location['y'])
	apiUrl = 'http://restapi.amap.com/v3/place/around?key=%s&location=%s,%s&offset=10'%(gaodeApi,y,x)
	r = json.loads(requests.get(apiUrl).text)
	content = r['pois']
	replys = ""
	index = 0
	for item in content:
		index+=1
		replys += '%d.%s\n\t类型：%s\n\t地址：%s\n'%(index,item['name'],item['type'],item['address'])
	return replys

def get_response(_info,userid):
	apiUrl = 'http://www.tuling123.com/openapi/api'
	data = {
		'key' : '07b02a9d521c4ee584fa1a737e4a380d',
		'info' : _info,
		'userid' : userid,
	}
	r = requests.post(apiUrl,data=data).text
	replys = json.loads(r)['text']
	return replys

def get_audio_token():
	#App ID: 10398558
	apiKey = 'eQvgGAHLKDfeouUuGgsxYy3W'
	secretKey = '4ea58fc8186544bf044cc2fb02781e46'
	auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey
	res = urllib.request.urlopen(auth_url)
	json_data = res.read().decode()
	#print(json_data)
	return json.loads(json_data)['access_token']

def dump_res(buf):#输出百度语音识别的结果
	global duihua
	a = eval(buf)
	if a['err_msg']=='success.':
		#print a['result'][0]#终于搞定了，在这里可以输出，返回的语句
		duihua = a['result'][0]
		print ('百度语音识别的结果',duihua)

def toWAV(filename):
	newfilename = filename
	if 'mp3' in filename:
		sound = AudioSegment.from_mp3(filename)
		newfilename = filename.replace('mp3','wav')
		sound.export(newfilename, format="wav")
	return newfilename

#多用户同时发送语音消息时存在调度问题
def cloud_speech_recognition(filename):
	global duihua
	token = get_audio_token()
	if 'wav' not in filename:
		filename = toWAV(filename)

	fp = wave.open(filename, 'rb')
	##已经录好音的语音片段
	nf = fp.getnframes()
	f_len = nf * 2
	audio_data = fp.readframes(nf)
 
	cuid = "10398558" #你的产品id
	srv_url = 'http://vop.baidu.com/server_api' + '?cuid=' + cuid + '&token=' + token
	http_header = [
		'Content-Type: audio/pcm; rate=8000',
		'Content-Length: %d' % f_len
	]
	c = pycurl.Curl()
	c.setopt(pycurl.URL, str(srv_url)) #curl doesn't support unicode
	#c.setopt(c.RETURNTRANSFER, 1)
	c.setopt(c.HTTPHEADER, http_header)   #must be list, not dict
	c.setopt(c.POST, 1)
	c.setopt(c.CONNECTTIMEOUT, 30)
	c.setopt(c.TIMEOUT, 30)
	c.setopt(c.WRITEFUNCTION, dump_res)
	c.setopt(c.POSTFIELDS, audio_data)
	c.setopt(c.POSTFIELDSIZE, f_len)
	c.perform() #pycurl.perform() has no return val
	c.close()
	return duihua


if __name__ == '__main__':
	#text = cloud_speech_recognition('../temp/audio/6375034170691042424.mp3')
	#print(text)
	location = {'x':39.977692,'y':116.344704}
	adcode = get_adcode(location)
	print(adcode)
	print(get_weather(location))
	print(get_trafficinfo(location))
	print(get_around(location))

