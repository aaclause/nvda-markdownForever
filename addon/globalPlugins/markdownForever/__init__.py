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
import yaml
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


def md2HTML(md, toc):
	extras = ["footnotes", "tables", "fenced-code-blocks", "task_list"]
	if toc: extras.append("toc")
	res = markdown2.markdown(md, extras=extras)
	toc = (res.toc_html if res.toc_html and res.toc_html.count("<li>") > 1 else '')
	return res, toc

def writeFile(fp, content):
	f = open(fp, "wb")
	if isPy3: f.write(content.encode())
	else:
		try: f.write(bytearray(content, "UTF-8"))
		except UnicodeDecodeError: f.write(bytearray(content.decode("UTF-8"), "UTF-8"))
	f.close()

def extractMetadata(text):
	metadata = {}
	if text.startswith("---"):
		ln = text[3]
		if ln in ["\r", "\n"]:
			if ln == "\r": ln = "\r\n"
			try:
				end = (text.index(ln * 2)-3)
				y = text[(3 + len(ln)):end].strip()
				docs = yaml.load_all(y, Loader=yaml.FullLoader)
				for doc in docs: metadata = doc
				text = text[end+3:].strip()
			except (ValueError, yaml.scanner.ScannerError): pass
	if not isinstance(metadata, dict): metadata = {}
	if not "title" in metadata.keys(): metadata["title"] = ""
	if not "toc" in metadata.keys(): metadata["toc"] = True
	return metadata, text

def convertToHTML(text, metadata, save=False, src=False, useTemplateHTML=True, display=True, fp=os.path.dirname(__file__) + r"\\tmp.html"):
	toc = metadata["toc"]
	title = metadata["title"]
	body, toc = md2HTML(text, toc)
	content = body
	if toc:
		tocReplacement = "<toc />"
		if not tocReplacement in content:
			pre = "<h1>%s</h1>" % _("Table of contents")
			content = pre + tocReplacement + content
		content = content.replace(tocReplacement, toc, 1)
	if save:
		if not isPy3: fp = fp.decode("mbcs")
		if useTemplateHTML: useTemplateHTML = not re.search("</html>", body, re.IGNORECASE)
		if not title.strip(): title = _("Markdown to HTML conversion")+(" (%s)" % time.strftime("%X %x"))
		if useTemplateHTML: content = template_HTML.format(title=title, body=content)
		writeFile(fp, content)
		if display: os.startfile(fp)
	else:
		if display:
			title = "%s%s" % (title + " - " if title else title, _("Markdown to HTML conversion (preview)")) if not src else _("Markdown to HTML source conversion")
			ui.browseableMessage(content, title, not src)
		else: return content

def convertToMD(text, metadata, display=True):
	title = metadata["title"]
	if title: dmp = "---\r\n%s\r\n...\r\n\r\n" % yaml.dump(metadata).strip()
	else: dmp = ""
	res = dmp+html2markdown.convert(text)
	if display:
		pre = (title + " - ") if title else title
		ui.browseableMessage(res, pre + _("HTML to Markdown conversion"), False)
	else: return res

def copyToClipAsHTML(html):
	winClipboard.copy(html, html=True)
	return html == winClipboard.get(html=True)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = _("Markdown Forever")

	def script_md2htmlSrcInNVDA(self, gesture):
		text = getText()
		if not text: return ui.message(_("No text"))
		metadata, text = extractMetadata(text)
		convertToHTML(text, metadata, save=False, src=True)
	script_md2htmlSrcInNVDA.__doc__ = _("Show the HTML source from Markdown")

	def script_html2md(self, gesture):
		text = getText()
		metadata = {}
		metadata["title"] = ""
		if text: convertToMD(text, metadata)
		else: ui.message(_("No text"))
	script_html2md.__doc__ = _("HTML to Markdown conversion")

	def script_md2htmlInNVDA(self, gesture):
		text = getText()
		if not text: return ui.message(_("No text"))
		metadata, text = extractMetadata(text)
		convertToHTML(text, metadata, useTemplateHTML=False)
	script_md2htmlInNVDA.__doc__ = _("Markdown to HTML conversion. The result is displayed in a virtual buffer of NVDA")

	def script_md2htmlInBrowser(self, gesture):
		text = getText()
		if not text: return ui.message(_("No text"))
		metadata, text = extractMetadata(text)
		convertToHTML(text, metadata, save=True)
	script_md2htmlInBrowser.__doc__ = _("Markdown to HTML conversion. The result is displayed in your default browser")

	def script_copyToClip(self, gesture):
		text = getText()
		if not text: return ui.message(_("No text"))
		metadata, text = extractMetadata(text)
		if scriptHandler.getLastScriptRepeatCount() == 0:
			api.copyToClip(convertToHTML(text, metadata, src=True, display=False))
			ui.message(_("HTML source copied to clipboard"))
		else:
			if copyToClipAsHTML(convertToHTML(text, metadata, src=True, display=False, save=False)): ui.message(_("Formatted HTML copied to clipboard"))
			else: ui.message(_("An error occured"))
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
		self.metadata, text = extractMetadata(text)
		metadata = self.metadata
		self.text = text
		super(InteractiveModeDlg, self).__init__(parent, title=title)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		destFormatText = _("Convert &to")
		self.destFormatListBox = sHelper.addLabeledControl(destFormatText, wx.Choice, choices=self.destFormatChoices)
		self.destFormatListBox.Bind(wx.EVT_CHOICE, self.onDestFormatListBox)
		self.destFormatListBox.SetSelection(0)
		tableOfContentext = _("&Generate a table of contents")
		self.tableOfContentCheckBox = sHelper.addItem(wx.CheckBox(self, label=tableOfContentext))
		self.tableOfContentCheckBox.SetValue(metadata["toc"])
		titleLabelText = _("&Title")
		self.titleTextCtrl = sHelper.addLabeledControl(titleLabelText, wx.TextCtrl)
		self.titleTextCtrl.SetValue(metadata["title"])
		self.virtualBufferBtn = bHelper.addButton(self, label=_("Show in &virtual buffer"))
		self.virtualBufferBtn.Bind(wx.EVT_BUTTON, self.onVB)
		self.browserBtn = bHelper.addButton(self, label=_("Show in &browser"))
		self.browserBtn.Bind(wx.EVT_BUTTON, self.onBrowser)
		self.copyToClipBtn = bHelper.addButton(self, label=_("&Copy to clipboard"))
		self.copyToClipBtn.Bind(wx.EVT_BUTTON, self.onCopyToClipBtn)
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
		if destFormatChoices_ > 0:
			self.browserBtn.Disable()
		else:
			self.browserBtn.Enable()
		if destFormatChoices_ == 2: self.tableOfContentCheckBox.Disable()
		else: self.tableOfContentCheckBox.Enable()

	def onBrowser(self, evt): self.onExecute(False)

	def onVB(self, evt): self.onExecute(True)

	def onExecute(self, vb=False):
		metadata = self.metadata
		metadata["toc"] = self.tableOfContentCheckBox.IsChecked()
		metadata["title"] = self.titleTextCtrl.GetValue()
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		if destFormatChoices_ == 0: convertToHTML(self.text, metadata, useTemplateHTML=True, save=not vb)
		elif destFormatChoices_ == 1: convertToHTML(self.text, metadata, save=False, src=True)
		elif destFormatChoices_ == 2: convertToMD(self.text, metadata)
		self.Destroy()

	def onCopyToClipBtn(self, event):
		metadata = self.metadata
		metadata["toc"] = self.tableOfContentCheckBox.IsChecked()
		metadata["title"] = self.titleTextCtrl.GetValue()
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		if destFormatChoices_ == 0: copyToClipAsHTML(self.text, metadata)
		elif destFormatChoices_ == 1: api.copyToClip(convertToHTML(self.text, metadata, src=True, display=False))
		else: api.copyToClip(convertToMD(self.text, metadata, display=False))
		self.Destroy()

	def onSave(self, event):
		metadata = self.metadata
		metadata["toc"] = self.tableOfContentCheckBox.IsChecked()
		metadata["title"] = self.titleTextCtrl.GetValue()
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		formats = [
			"HTML format (*.htm, *.html)|*.htm;*.html",
			"Text file (*.txt)|*.txt",
			"Markdown file (*.md)|*.md"
		]
		format = formats[destFormatChoices_]
		filename = metadata["filename"] if "filename" in metadata.keys() else time.strftime("%y-%m-%d_-_%H-%M-%S")
		dlg = wx.FileDialog(None, _("Select the location"), "%USERPROFILE%\documents", filename, format, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			fp = dlg.GetDirectory() + '\\' + dlg.GetFilename()
			text = ''
			if destFormatChoices_ == 0: convertToHTML(self.text, metadata, useTemplateHTML=True, save=True, fp=fp)
			elif destFormatChoices_ == 1: text = convertToHTML(self.text, metadata, src=True, display=False)
			else: text = html2markdown.convert(self.text)
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
