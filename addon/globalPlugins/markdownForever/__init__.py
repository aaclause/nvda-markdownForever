# coding: utf-8
"""
Markdown Forever

A small NVDA add-on that provides preview of MarkDown or HTML contents in any textarea

Copyright 2019 André-Abush Clause, released under GPL.
GitHub: https://github.com/andre9642/nvda-markdownForever/
"""

from __future__ import unicode_literals
import os
import sys
isPy3 = True if sys.version_info >= (3, 0) else False
import re
import time

import addonHandler
addonHandler.initTranslation()
import api
import globalPluginHandler
import textInfos
import treeInterceptorHandler
import ui
from logHandler import log

from . import markdown2

template_HTML = """
<!DOCTYPE HTML>
<html>
    <head>
        <meta charset="UTF-8" />
        <title>{title}</title>
    </head>
    <body>
        {body}
    </body>
</html>
"""

def getText():
	obj = api.getFocusObject()
	treeInterceptor = obj.treeInterceptor
	if isinstance(
			treeInterceptor,
			treeInterceptorHandler.DocumentTreeInterceptor) and not treeInterceptor.passThrough:
		obj = treeInterceptor
	try:
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
	except (RuntimeError, NotImplementedError):
		info = None
	if not info or info.isCollapsed:
		try:
			info = obj.makeTextInfo(textInfos.POSITION_ALL)
		except (RuntimeError, NotImplementedError):
			obj = api.getNavigatorObject()
			text = obj.value
			return "%s" % text if text else ''
	return info.text


def md2HTML(md):
	res = markdown2.markdown(md, extras=["footnotes", "tables", "toc", "fenced-code-blocks", "task_list"])
	if isPy3: toc = (res.toc_html if res.toc_html else '')
	else: toc = (res.toc_html.encode("UTF-8") if res.toc_html else '')
	if toc: toc = ("<h1>%s</h1>" % _("Table of contents")) + toc
	if isPy3: return res, toc
	else: return res.encode("UTF-8"), toc.encode("UTF-8")

def convert(text, save=False, html=True):
	body, toc = md2HTML(text)
	if save:
		fp = os.path.dirname(__file__) + r"\\tmp.html"
		if not isPy3: fp = fp.decode("mbcs")
		useTemplateHTML = not re.search("</html>", body, re.IGNORECASE)
		title = _("Conversion (%s)") % time.strftime("%X %x")
		if useTemplateHTML:
			if isPy3: body = template_HTML.format(title=title, body=(toc+body))
			else: body = template_HTML.format(title=title, body=(toc+body).decode("UTF-8"))
		f = open(fp, "wb")
		if isPy3: f.write(body.encode())
		else: f.write(bytearray(body, "UTF-8"))
		f.close()
		os.startfile(fp)
	else:
		ui.browseableMessage(
			(toc + body).decode("UTF-8") if not isPy3 else (toc + body),
			_("Preview of MarkDown or HTML") if html else _("HTML source from Markdown"),
			html
		)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = _("Markdown Forever")

	def script_showSourceViaNVDA(self, gesture):
		text = getText()
		convert(text, False, False)
	script_showSourceViaNVDA.__doc__ = _("Show HTML source from Markdown through NVDA")

	def script_showViaNVDA(self, gesture):
		text = getText()
		convert(text)
	script_showViaNVDA.__doc__ = _("Preview of MarkDown or HTML through NVDA")

	def script_showInBrowser(self, gesture):
		text = getText()
		convert(text, True)
	script_showInBrowser.__doc__ = _("Preview of MarkDown or HTML through your default browser")

	__gestures = {
		"kb:nvda+alt+j": "showSourceViaNVDA",
		"kb:nvda+alt+k": "showViaNVDA",
		"kb:nvda+alt+l": "showInBrowser"
	}
	
