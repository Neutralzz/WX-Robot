#coding=utf-8
from wxpy import *
from wxutil import *
import json,os,sys
current_path = os.path.dirname(__file__)
module_path = os.path.join(current_path, 'pencil_python')
sys.path.append(module_path)
from pencil_python.pencil import pencil_draw



global chatStatus,locMarker
chatStatus = {}
locMarker = {}
bot = Bot()
myself = bot.friends().search('Neutrali')[0]
mygril = bot.friends().search('包琛')[0]

@bot.register(except_self=False)
def auto_reply(msg):
	# 如果是群聊，但没有被 @，则不回复
	if isinstance(msg.chat, Group) and not msg.is_at:
		return
	userid = str(msg.sender)
	print(userid)
	if not chatStatus.__contains__(userid):
		chatStatus[userid] = 0
	if chatStatus[userid] == 1:
		chatStatus[userid] = 0
		if msg.type == TEXT and msg.text.isdigit():
			op = int(msg.text)
			if op == 1:
				return get_weather(locMarker[userid])
			elif op == 2:
				#rint('2',locMarker[userid])
				return get_trafficinfo(locMarker[userid])
			elif op == 3:
				return get_around(locMarker[userid])

	if chatStatus[userid] == 0:
		if msg.type == RECORDING:
			print('voice msg ')
			filename = '../temp/audio/%d.mp3'%msg.id
			msg.get_file(filename)
			text = cloud_speech_recognition(filename)
			replys = get_response(text,userid)
			return ""+replys
		elif msg.type == TEXT:
			print('text msg :'+msg.text)
			replys = get_response(msg.text,userid)
			return ""+replys
		elif msg.type == MAP:
			print(msg.location)
			chatStatus[userid] = 1
			locMarker[userid] = msg.location
			return "您想查询该位置的哪些信息？\n1.天气查询\n2.交通态势查询\n3.周边服务查询\n（请回复对应数字）\n"
		elif msg.type == PICTURE:
			try:
				print('pic msg')
				filename = '../temp/img/%d.jpg'%msg.id
				msg.get_file(filename)
				dstfile = '../temp/zip_img/%d.jpg'%msg.id
				resize_image(filename,dstfile)
				print('pencil draw begin')
			
				pencil_draw(path=dstfile, gammaS=1, gammaI=1)
			except Exception as e:
				print('Exception',e)
			print('pencil drawing end')
			msg.reply_image('./pencil_python/output/%d_pencil.jpg'%msg.id)

bot.start()

embed()
