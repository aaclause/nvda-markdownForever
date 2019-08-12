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
sys.path.append(os.path.join(os.path.dirname(__file__), "lib/common"))
if isPy3: sys.path.append(os.path.join(os.path.dirname(__file__), "lib/py3"))
else: sys.path.append(os.path.join(os.path.dirname(__file__), "lib/py2"))
import re
import time

import addonHandler
addonHandler.initTranslation()
import api
import globalPluginHandler
import scriptHandler
import textInfos
import treeInterceptorHandler
import ui
from logHandler import log

import markdown2
import html2markdown
from . import winClipboard
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

def convert(text, save=False, html=True, useTemplateHTML = True):
	body, toc = md2HTML(text)
	if save:
		fp = os.path.dirname(__file__) + r"\\tmp.html"
		if not isPy3: fp = fp.decode("mbcs")
		if useTemplateHTML: useTemplateHTML = not re.search("</html>", body, re.IGNORECASE)
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

def copyToClipAsHTML():
	text = getText()
	if text:
		body, toc = md2HTML(text)
		winClipboard.copy(body, html=True)
		print("start", winClipboard.get(html=True), body)
		if body in winClipboard.get(html=True): ui.message(_("Formatted HTML copied in clipboard"))
		else: ui.message(_("An error occurred"))
	else: ui.message(_("No text"))


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = _("Markdown Forever")

	def script_md2htmlSrcInNVDA(self, gesture):
		text = getText()
		if text: convert(text, False, False)
		else: ui.message(_("No text"))
	script_md2htmlSrcInNVDA.__doc__ = _("Show the HTML source from Markdown")

	def script_html2md(self, gesture):
		text = getText()
		if text:
			res = html2markdown.convert(text)
			ui.browseableMessage(res, _("HTML to Markdown conversion"), False)
		else: ui.message(_("No text"))
	script_html2md.__doc__ = _("HTML to markdown conversion")

	def script_md2htmlInNVDA(self, gesture):
		text = getText()
		if text: convert(text)
		else: ui.message(_("No text"))
	script_md2htmlInNVDA.__doc__ = _("Markdown to HTML conversion. The result is displayed in a virtual buffer of NVDA")

	def script_md2htmlInBrowser(self, gesture):
		text = getText()
		if text: convert(text, True)
		else: ui.message(_("No text"))
	script_md2htmlInBrowser.__doc__ = _("Markdown to HTML conversion. The result is displayed in your default browser")

	def script_copyToClip(self, gesture):
		if scriptHandler.getLastScriptRepeatCount() == 0: 
			text = getText()
			if text:
				res = md2HTML(text)[0]
				if not isPy3: res = res.decode("UTF-8")
				api.copyToClip(res)
				ui.message("HTML source copied to clipboard")
			else: ui.message(_("No text"))
		else: copyToClipAsHTML()
	script_copyToClip.__doc__ = _("Copy the result to the clipboard from Markdown. One press: copy the HTML source. Two quick presses: copy the formatted HTML")

	__gestures = {
		"kb:nvda+alt+b": "md2htmlInBrowser",
		"kb:nvda+alt+n": "md2htmlInNVDA",
		"kb:nvda+alt+k": "md2htmlSrcInNVDA",
		"kb:nvda+alt+l": "html2md",
		"kb:nvda+shift+h": "copyToClip",
	}
