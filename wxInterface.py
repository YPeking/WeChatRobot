#coding: utf-8

import hashlib
import web
import os

import receive
import reply

class wxInterface:
	def __init__(self):
		self.app_root = os.path.dirname(__file__)
		self.templates_root = os.path.join(self.app_root, 'templates')
		self.render = web.template.render(self.templates_root)
        
	def GET(self):
		try:
			data = web.input()
			signature = data.signature
			timestamp = data.timestamp
			nonce = data.nonce
			echostr = data.echostr
			token = "wechat token"
            
            # 加密验证
			list = [token, timestamp, nonce]
			list.sort()
			sha1 = hashlib.sha1()
			map(sha1.update, list)
			hashcode = sha1.hexdigest()
			if hashcode == signature:
				return echostr
			else:
				return ""
		except Exception, Argument:
			return Argument

	def POST(self):
		try:
			webData = web.data()
			print "Post webData is ", webData

			recMsg = receive.parse_xml(webData)
			if isinstance(recMsg, receive.Msg):
				toUser = recMsg.FromUserName
				fromUser = recMsg.ToUserName
				if recMsg.MsgType == 'text':
					content = recMsg.Content
					replyMsg = reply.TextMsg(toUser, fromUser, content)
					return replyMsg.send()
				elif recMsg.MsgType == 'image':
					mediaId = recMsg.MediaId
					replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
					return replyMsg.send()
				elif recMsg.MsgType == 'voice':
					content = recMsg.Content
					replyMsg = reply.TextMsg(toUser, fromUser, content)
					return replyMsg.send()
				else:
					print "No Processing"
					return reply.Msg().send()
			else:
				print "暂且不处理"
				return reply.Msg().send()
		except Exception, Argment:
				return Argment