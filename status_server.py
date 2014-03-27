#!/usr/bin/python

import os.path
import subprocess as sp

import tornado.ioloop
import tornado.httpserver
import tornado.web

def check_status():
	return sp.check_output(["/home/motherbrain/minecraft/mc_vanilla/init/minecraft", "status"])

GENERATE_LOCKED = False
def regenerate_overviewer():
	if not GENERATE_LOCKED:
		GENERATE_LOCKED = True
		sp.call(["/home/motherbrain/init/minecraft", "overviewer"])
		GENERATE_LOCKED = False
		return True
	else:
		return False

print check_status()

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		st = check_status()
		self.write("<h2>Zebes status</h2><p>" + st + "</p>")

class OverviewerHandler(tornado.web.RequestHandler):
	def get(self):
		self.redirect("static/index.html")

class UpdateOverviewerHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("generating_map.html")
		regenerate_overviewer()

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/map", OverviewerHandler),
			(r"/mapupdate", UpdateOverviewerHandler),
			(r"/static", tornado.web.StaticFileHandler, { "path": "./map" }),
		]
		settings = dict(
			static_path=os.path.join(os.path.dirname(__file__), "map"),
			debug=True,
		)
		tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(80)
	tornado.ioloop.IOLoop.instance().start()
