import codecs
import os.path as osp
import re
import threading
import time
import urllib.parse as urlParse
from http.server import BaseHTTPRequestHandler, HTTPServer
import config
from logHandler import log
from .common import *
HTMLTemplate = """<!DOCTYPE HTML>
<html>
	<head>
		<title>{title}</title>
		<meta charset="{encoding}" />
	</head>
	<body>
		{body}
	</body>
</html>"""

def mergeHTMLTemplate(
	title=_("No title"),
	body=_("<p>No content</p>"),
	encoding=None
):
	if not encoding: encoding = config.conf["markdownForever"]["HTTPServer"]["defaultEncoding"]
	return HTMLTemplate.format(
		title=title,
		body=body,
		encoding=encoding
	)

def indexOf(path):
	ls = os.listdir(path)
	out = "<h1>%s</h1><ul>" % _(f"Index of {path}")
	for e in ls:
		if isPath(path + e): e += '/'
		elif not re.match("^.+\.(html?|md|txt)$", e.lower()): continue
		out += f'<li><a href="{e}">{e}</a></li>'
	out += "</li>"
	return out

def getFile(path, params=None, baseDir=None):
	if not baseDir: baseDir = config.conf["markdownForever"]["defaultPath"]
	fullPath = realpath(baseDir) + path.replace('/', r'\\')
	while "\\\\" in fullPath: fullPath = fullPath.replace("\\\\", '\\')
	status_code = 200
	body = None
	if not osp.exists(fullPath):
		status_code = 404
		body = mergeHTMLTemplate(
			title=_("Error 404"),
			body="<p>%s.</p>" % _(f"The requested URL “{path}” was not found")
		)
	elif isPath(fullPath):
		if not fullPath.endswith('\\'): fullPath += '\\'
		if not osp.exists(fullPath + "index.md"):
			body = indexOf(fullPath)
			body = mergeHTMLTemplate(
				title=_(f"Index of {path}"),
				body=body
			)
	if not body:
		f = codecs.open(fullPath, encoding=config.conf["markdownForever"]["HTTPServer"]["defaultEncoding"])
		text = f.read()
		if fullPath.endswith(".html") or fullPath.endswith(".htm"):
			body = text
		else:
			metadata, text = extractMetadata(text)
			body = convertToHTML(text, metadata, display=False)
			body = mergeHTMLTemplate(title=metadata["title"], body=body)
			f.close()
	return status_code, body.encode(config.conf["markdownForever"]["HTTPServer"]["defaultEncoding"])

class Server(BaseHTTPRequestHandler):

	def log_request(code='-', size='-'): pass

	def _set_response(self, status_code=200):
		self.send_response(status_code)
		self.send_header("Content-type", "text/html; charset=%s" % config.conf["markdownForever"]["HTTPServer"]["defaultEncoding"])
		self.end_headers()

	def do_GET(self):
		path = urlParse.unquote(self.path)
		params = {}
		if '?' in path:
			splitPath = path.split('?')
			params = dict(urlParse.parse_qsl(''.join(splitPath[1:])))
			path = splitPath[0]
		satus_code, body = getFile(path, params)
		self._set_response(satus_code)
		self.wfile.write(body)

	def do_POST(self):
		content_length = int(self.headers["Content-Length"])  # <--- Gets the size of data
		post_data = self.rfile.read(content_length)  # <--- Gets the data itself
		self._set_response()
		self.wfile.write("POST request for {}".format(self.path).encode("utf-8"))

class CreateHTTPServer(threading.Thread):

	httpd = None

	def run(self):
		server_class = HTTPServer
		handler_class = Server
		host = config.conf["markdownForever"]["HTTPServer"]["host"]
		port = config.conf["markdownForever"]["HTTPServer"]["port"]
		server_address = (host, port)
		self.httpd = server_class(server_address, handler_class)
		self.httpd.serve_forever()

httpdThread = None
def run():
	global httpdThread
	if httpdThread: return
	httpdThread = CreateHTTPServer()
	httpdThread.start()

def stop():
	global httpdThread
	if not httpdThread: return
	httpdThread.httpd.shutdown()
	httpdThread.httpd.socket.close()
	httpdThread.join()
	httpdThread = None

def isRun():
	if httpdThread: return True
	return False
