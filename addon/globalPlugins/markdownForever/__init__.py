# coding: utf-8
"""
Markdown Forever

A small NVDA add-on that converts Markdown or HTML contents easily

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
import gui, wx

import addonHandler
addonHandler.initTranslation()
import api
import globalPluginHandler
import scriptHandler
import textInfos
import treeInterceptorHandler
import ui

import markdown2
import html2markdown
from . import winClipboard

template_HTML = ("""
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
""").strip()

def getText():
	obj = api.getFocusObject()
	treeInterceptor = obj.treeInterceptor
	if isinstance(treeInterceptor, treeInterceptorHandler.DocumentTreeInterceptor) and not treeInterceptor.passThrough: obj = treeInterceptor
	try: info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
	except (RuntimeError, NotImplementedError): info = None
	if not info or info.isCollapsed:
		try: info = obj.makeTextInfo(textInfos.POSITION_ALL)
		except (RuntimeError, NotImplementedError):
			obj = api.getNavigatorObject()
			text = obj.value
			return "%s" % text if text else ''
	return info.text


def md2HTML(md):
	res = markdown2.markdown(md, extras=["footnotes", "tables", "toc", "fenced-code-blocks", "task_list"])
	toc = (res.toc_html if res.toc_html and res.toc_html.count("<li>") > 1 else '')
	if toc: toc = ("<h1>%s</h1>" % _("Table of contents")) + toc
	if isPy3: return res, toc
	else: return res.encode("UTF-8"), toc.encode("UTF-8")

def writeFile(fp, content):
	f = open(fp, "wb")
	if isPy3: f.write(content.encode())
	else:
		try: f.write(bytearray(content, "UTF-8"))
		except UnicodeDecodeError: f.write(bytearray(content.decode("UTF-8"), "UTF-8"))
	f.close()

def convertToHTML(text, save=False, src=False, useTemplateHTML=True, display=True, fp=os.path.dirname(__file__) + r"\\tmp.html"):
	body, toc = md2HTML(text)
	if save:
		if not isPy3: fp = fp.decode("mbcs")
		if useTemplateHTML: useTemplateHTML = not re.search("</html>", body, re.IGNORECASE)
		title = _("Markdown to HTML conversion")+(" (%s)" % time.strftime("%X %x"))
		if useTemplateHTML:
			if isPy3: body = template_HTML.format(title=title, body=(toc+body))
			else: body = template_HTML.format(title=title, body=(toc+body).decode("UTF-8"))
		writeFile(fp, body)
		if display: os.startfile(fp)
	else:
		content = (toc + body).decode("UTF-8") if not isPy3 else (toc + body)
		if display:
			title = _("Markdown to HTML conversion (preview)") if not src else _("Markdown to HTML source conversion")
			ui.browseableMessage(content, title, not src)
		else: return content

def convertToMD(text):
	res = html2markdown.convert(text)
	ui.browseableMessage(res, _("HTML to Markdown conversion"), False)

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
		if text: convertToHTML(text, save=False, src=True)
		else: ui.message(_("No text"))
	script_md2htmlSrcInNVDA.__doc__ = _("Show the HTML source from Markdown")

	def script_html2md(self, gesture):
		text = getText()
		if text: convertToMD(text)
		else: ui.message(_("No text"))
	script_html2md.__doc__ = _("HTML to Markdown conversion")

	def script_md2htmlInNVDA(self, gesture):
		text = getText()
		if text: convertToHTML(text, useTemplateHTML=False)
		else: ui.message(_("No text"))
	script_md2htmlInNVDA.__doc__ = _("Markdown to HTML conversion. The result is displayed in a virtual buffer of NVDA")

	def script_md2htmlInBrowser(self, gesture):
		text = getText()
		if text: convertToHTML(text, save=True)
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

	def script_interactiveMode(self, gesture):
		text = getText()
		if text: gui.mainFrame._popupSettingsDialog(InteractiveModeDlg, text=text)
		else: ui.message(_("No text"))
	script_interactiveMode.__doc__ = _("Interactive mode")

	__gestures = {
		"kb:nvda+alt+b": "md2htmlInBrowser",
		"kb:nvda+alt+n": "md2htmlInNVDA",
		"kb:nvda+alt+k": "html2md",
		"kb:nvda+alt+l": "md2htmlSrcInNVDA",
		"kb:nvda+shift+h": "copyToClip",
		"kb:nvda+alt+,": "interactiveMode",
	}

class InteractiveModeDlg(wx.Dialog):
	destFormatChoices = ["HTML", _("HTML source"), "Markdown"]
	destFormatChoices_ = ["HTML", "HTMLSrc", "md"]

	# Translators: This is the label for the edit dictionary entry dialog.
	def __init__(self, parent=None, title=_("Interactive mode") + " — MarkdownForever", text=''):
		self.text = text
		super(InteractiveModeDlg, self).__init__(parent, title=title)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		destFormatText = _("Convert &to")
		self.destFormatListBox = sHelper.addLabeledControl(destFormatText, wx.Choice, choices=self.destFormatChoices)
		self.destFormatListBox.Bind(wx.EVT_CHOICE, self.onDestFormatListBox)
		self.destFormatListBox.SetSelection(0)
		self.virtualBufferBtn = bHelper.addButton(self, label=_("Show in &virtual buffer"))
		self.virtualBufferBtn.Bind(wx.EVT_BUTTON, self.onBrowser)
		self.browserBtn = bHelper.addButton(self, label=_("Show in &browser"))
		self.browserBtn.Bind(wx.EVT_BUTTON, self.onVB)
		saveBtn = bHelper.addButton(self, label=_("&Save as..."))
		saveBtn.Bind(wx.EVT_BUTTON, self.onSave)
		saveBtn.SetDefault()
		sHelper.addItem(bHelper)

		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.CANCEL))

		mainSizer.Add(sHelper.sizer,border=20,flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.destFormatListBox.SetFocus()

	def onDestFormatListBox(self, evt):
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		if destFormatChoices_ > 0: self.browserBtn.Disable()
		else: self.browserBtn.Enable()

	def onBrowser(self, evt): self.onExecute(False)

	def onVB(self, evt): self.onExecute(True)

	def onExecute(self, vb=False):
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		if destFormatChoices_ == 0: convertToHTML(self.text, useTemplateHTML=False, save=vb)
		elif destFormatChoices_ == 1: convertToHTML(self.text, save=vb, src=True)
		elif destFormatChoices_ == 2: convertToMD(self.text)
		self.Destroy()

	def onSave(self, event):
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		formats = [
			"HTML format (*.htm, *.html)|*.htm;*.html",
			"Text file (*.txt)|*.txt",
			"Markdown file (*.md)|*.md"
		]
		format = formats[destFormatChoices_]
		dlg = wx.FileDialog(None, _("Select the location"), "%USERPROFILE%\documents", time.strftime("%y-%m-%d_-_%H-%M-%S"), format, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			fp = dlg.GetDirectory() + '\\' + dlg.GetFilename()
			text = ''
			if destFormatChoices_ == 0: convertToHTML(self.text, useTemplateHTML=False, save=True, fp=fp)
			elif destFormatChoices_ == 1: text = convertToHTML(self.text, src=True, display=False)
			elif destFormatChoices_ == 2: text = html2markdown.convert(self.text)
			if text:
				writeFile(fp, text)
				os.startfile(fp)
			dlg.Destroy()
			self.Destroy()
			return
		else:
			dlg.Destroy()
			self.destFormatListBox.SetFocus()

	def onOk(self, evt):
		self.Destroy()
