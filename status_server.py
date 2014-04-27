#!/usr/bin/python

import time
import os.path
import re
import subprocess as sp

import tornado.ioloop
import tornado.httpserver
import tornado.web

def init_minecraft_with_result(command):
	return sp.check_output(["/home/motherbrain/minecraft/mc_vanilla/init/minecraft", command])

def check_status():
	return init_minecraft_with_result("status")

GENERATE_LOCKED = False
def regenerate_overviewer():
	global GENERATE_LOCKED

	if not GENERATE_LOCKED:
		GENERATE_LOCKED = True
		sp.call(["/home/motherbrain/init/minecraft", "overviewer"])
		GENERATE_LOCKED = False
		return True
	else:
		return False


is_running_regexp = re.compile(r'.*(not running).*')

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		status = check_status()
		running = (is_running_regexp.search(status) is None)

		playercount, connected = "", ""

		if running:
			playercount = int(init_minecraft_with_result("playercount"))
			connected   = init_minecraft_with_result("connected")
			# remove the server log tag
			connected   = connected[33:]

			# There's a bug with ./minecraft playercount
			if len(connected) == 1:
				playercount = "0"

		self.render("index.html", status=status, playercount=playercount, connected=connected)

class OverviewerHandler(tornado.web.RequestHandler):
	def get(self):
		self.redirect("static/map/index.html")

class UpdateOverviewerHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.render("generating_map.html")
		if not regenerate_overviewer():
			print "Already running!"

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/map", OverviewerHandler),
			(r"/mapupdate", UpdateOverviewerHandler),
			(r"/map_static", tornado.web.StaticFileHandler, { "path": "./static/map" }),
		]
		settings = dict(
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			debug=True,
		)
		tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(80)
	tornado.ioloop.IOLoop.instance().start()
