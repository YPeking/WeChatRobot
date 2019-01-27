#coding: utf-8
import os
import sys
import sae
import web
from wxInterface import wxInterface

app_root = os.path.dirname(__file__)


urls = ('/wx', 'wxInterface')
templates_root = os.path.join(app_root, 'templates')
render = web.template.render(templates_root)

app = web.application(urls, globals()).wsgifunc()
application = sae.create_wsgi_app(app)
