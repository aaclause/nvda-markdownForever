"""
Markdown Forever

Full-featured Markdown and HTML converter for NVDA

Copyright 2020 André-Abush Clause, Sof and other contributors. Released under GPL.
GitHub: https://github.com/andre9642/nvda-markdownForever/
"""

import codecs
import json
import os, os.path
import re
import sys
import gui, wx

import addonHandler
addonHandler.initTranslation()
import api
import config
import globalPluginHandler
import languageHandler
import scriptHandler
import ui
from logHandler import log

from . import HTTPServer
from . import settings
from . import updateCheck


confSpecs = {
	"autoCheckUpdate": "boolean(default=True)",
	"lastNVDAVersion": 'string(default="unknown")',
	"updateChannel": "option(dev, stable, default=stable)",
	"lastCheckUpdate": "float(min=0, default=0)",
	"toc": 'boolean(default=False)',
	"autonumber-headings": 'boolean(default=True)',
	"extratags": 'boolean(default=True)',
	"extratags-back": 'boolean(default=True)',
	"detectExtratags": 'boolean(default=True)',
	"genMetadata": 'boolean(default=True)',
	"IM_defaultAction": 'integer(min=0, max=4, default=0)',
	"defaultPath": 'string(default="%USERPROFILE%\documents")',
	"markdownEngine": 'option("html2markdown", "html2text", default="html2text")',
	"HTMLTemplate": 'string(default="default")',
	"HTMLTemplates": {},
	"HTTPServer": {
		"host": 'string(default="127.0.0.1")',
		"port": "integer(min=1, max=65535, default=8794)",
		"defaultEncoding": 'string(default="UTF-8")',
		"rootDirs": {}
	}
}
config.conf.spec["markdownForever"] = confSpecs

from .common import *

if not os.path.exists(configDir): os.mkdir(configDir)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = addonSummary

	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		self.createMenu()
		self.updateCheckThread = updateCheck.UpdateCheck()
		self.updateCheckThread.start()
		if not self.updateCheckThread.is_alive(): log.error("Update check system not started")

	def createMenu(self):
		self.submenu = wx.Menu()
		documentationsMenu = wx.Menu()
		self.submenu.AppendSubMenu(documentationsMenu, _("Documentation"), _("Documentation menu"))
		langs = self.getDocumentationLanguages()
		for lang, langDesc in langs.items():
			item = documentationsMenu.Append(wx.ID_ANY, langDesc, _("Open the add-on documentation in this language."))
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, lambda evt, lang=lang: self.onDoc(evt, lang), item)
		item = self.submenu.Append(wx.ID_ANY, "%s..." % _("Settings"), _("Add-on settings"))
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU,
			lambda event: wx.CallAfter(gui.mainFrame._popupSettingsDialog, settings.AddonSettingsDialog),
			item
		)
		item = self.submenu.Append(wx.ID_ANY, _("HTTP server"), _("Web server"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onHTTPServer, item)
		item = self.submenu.Append(wx.ID_ANY, "%s..." % _("&Check for update"), _("Checks if update is available"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onUpdate, item)
		item = self.submenu.Append(wx.ID_ANY, _("&Web site"), _("Open the add-on website."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onWebsite, item)
		self.submenu_item = gui.mainFrame.sysTrayIcon.menu.InsertMenu(2, wx.ID_ANY, "%s (%s)" % (_("&Markdown Forever"), addonVersion), self.submenu)


	def getDocumentationLanguages(self):
		langs = {}
		docDir = os.path.join(baseDir, "..", "..", "doc", "")
		ls = os.listdir(docDir)
		for f in ls:
			if os.path.isfile(os.path.join(docDir, f)) and f.lower().endswith(".md"):
				lang = f.replace(".md", '')
				langDesc = languageHandler.getLanguageDescription(lang)
				if langDesc: langs[lang] = langDesc
		return langs

	def removeMenu(self):
		gui.mainFrame.sysTrayIcon.menu.DestroyItem(self.submenu_item)

	def terminate(self):
		HTTPServer.stop()
		self.removeMenu()
		self.updateCheckThread.stop()
		self.updateCheckThread.join()
		if self.updateCheckThread.is_alive(): log.info("Update check system stopped")
		super(GlobalPlugin, self).terminate()

	@staticmethod
	def onHTTPServer(evt):
		if HTTPServer.isRun:
			HTTPServer.run()
		host = config.conf["markdownForever"]["HTTPServer"]["host"]
		port = config.conf["markdownForever"]["HTTPServer"]["port"]
		os.startfile("http://{host}:{port}/".format(host=host, port=port))

	@staticmethod
	def onDoc(evt, lang=defaultLanguage.split('_')[0]):
		MDLocation = os.path.join(addonPath, "doc", lang + ".md")
		if not os.path.exists(MDLocation):
			MDLocation = os.path.join(addonPath, "doc", "en"+".md")
		f = codecs.open(MDLocation, "rb")
		raw = f.read()
		if raw.startswith(codecs.BOM_UTF8): raw = raw[3:]
		metadata, text = extractMetadata(raw.decode("UTF-8"))
		HTMLLocation = MDLocation.replace(".md", ".html")
		convertToHTML(text, metadata, save=True, src=False, useTemplateHTML=True, display=True, fp=HTMLLocation)
		os.startfile(HTMLLocation)

	@staticmethod
	def onUpdate(evt):
		return updateCheck.checkUpdates()

	@staticmethod
	def onWebsite(evt):
		return os.startfile("https://andreabc.net/projects/NVDA_addons/MarkdownForever/")

	def script_md2htmlSrcInNVDA(self, gesture):
		text, err = getText()
		if err: return ui.message(err)
		metadata, text = extractMetadata(text)
		convertToHTML(text, metadata, save=False, src=True, useTemplateHTML=False)
	script_md2htmlSrcInNVDA.__doc__ = _("Show the HTML source from Markdown")

	def script_html2md(self, gesture):
		metadata, text = getMetadataAndTextForMarkDown()
		if metadata: convertToMD(text, metadata)
	script_html2md.__doc__ = _("HTML to Markdown conversion")

	def extractMetadata(self, text):
		return extractMetadata(text)

	def convertToMD(self, text, metadata):
		return convertToMD(text, metadata)

	def script_md2htmlInNVDA(self, gesture):
		text, err = getText()
		if err: return ui.message(err)
		metadata, text = extractMetadata(text)
		convertToHTML(text, metadata)
	script_md2htmlInNVDA.__doc__ = _("Markdown to HTML conversion. The result is displayed in a virtual buffer of NVDA")

	def script_md2htmlInBrowser(self, gesture):
		text, err = getText()
		if err: return ui.message(err)
		metadata, text = extractMetadata(text)
		convertToHTML(text, metadata, save=True)
	script_md2htmlInBrowser.__doc__ = _("Markdown to HTML conversion. The result is displayed in your default browser")

	def script_copyHTMLSrcToClip(self, gesture):
		text, err = getText()
		if err: return ui.message(err)
		metadata, text = extractMetadata(text)
		api.copyToClip(convertToHTML(text, metadata, src=True, display=False, useTemplateHTML=False))
		ui.message(_("HTML source copied to clipboard"))
	script_copyHTMLSrcToClip.__doc__ = _("Markdown to HTML source conversion. The result is copied to clipboard")

	def script_copyFormattedHTMLToClip(self, gesture):
		text, err = getText()
		if err: return ui.message(err)
		metadata, text = extractMetadata(text)
		if copyToClipAsHTML(convertToHTML(text, metadata, src=True, display=False, save=False)): return ui.message(_("Formatted HTML copied to clipboard"))
		else: ui.message(_("An error occured"))
	script_copyFormattedHTMLToClip.__doc__ = _("Markdown to formatted HTML conversion. The result is copied to clipboard")

	def script_copyMarkdownToClip(self, gesture):
		metadata, text = getMetadataAndTextForMarkDown()
		if not metadata: return
		res = convertToMD(text, metadata, display=False)
		if res:
			api.copyToClip(res)
			ui.message(_("Markdown copied to clipboard"))
		else: ui.message(_("An error occured"))
	script_copyMarkdownToClip.__doc__ = _("HTML to Markdown conversion. The result is copied to clipboard")

	def script_interactiveMode(self, gesture):
		text, err = getText()
		if err: return ui.message(err)
		gui.mainFrame._popupSettingsDialog(InteractiveModeDlg, text=text)
	script_interactiveMode.__doc__ = _("Interactive mode")

	__gestures = {
		"kb:nvda+alt+b": "md2htmlInBrowser",
		"kb:nvda+alt+n": "md2htmlInNVDA",
		"kb:nvda+alt+k": "html2md",
		"kb:nvda+alt+l": "md2htmlSrcInNVDA",
		"kb:nvda+Control+h": "copyHTMLSrcToClip",
		"kb:nvda+shift+h": "copyFormattedHTMLToClip",
		"kb:nvda+shift+g": "copyMarkdownToClip",
		"kb:nvda+Control+i": "interactiveMode",
	}

class InteractiveModeDlg(wx.Dialog):
	destFormatChoices = ["HTML", _("HTML source"), "Markdown"]
	destFormatChoices_ = ["HTML", "HTMLSrc", "md"]

	# Translators: This is the label for the edit dictionary entry dialog.
	def __init__(self, parent=None, title=_("Interactive mode") + f" — {addonSummary}", text=''):
		self.metadata, self.text = extractMetadata(text)
		metadata = self.metadata
		defaultAction = config.conf["markdownForever"]["IM_defaultAction"]
		super(InteractiveModeDlg, self).__init__(parent, title=title)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)

		isHTMLPattern = re.search("(?:</html>|</p>)", self.text, re.IGNORECASE)
		guessDestFormat = 2 if isHTMLPattern else 0
		destFormatText = _("C&onvert to")
		self.destFormatListBox = sHelper.addLabeledControl(destFormatText, wx.Choice, choices=self.destFormatChoices)
		self.destFormatListBox.Bind(wx.EVT_CHOICE, self.onDestFormatListBox)
		self.destFormatListBox.SetSelection(guessDestFormat)

		genMetadataText = _("Generate corresponding &metadata from HTML source")
		self.genMetadataCheckBox = sHelper.addItem(wx.CheckBox(self, label=genMetadataText))
		self.genMetadataCheckBox.SetValue(metadata["genMetadata"])
		self.genMetadataCheckBox.Bind(wx.EVT_CHECKBOX, self.onDestFormatListBox)

		tableOfContentsText = _("&Generate a table of contents")
		self.tableOfContentsCheckBox = sHelper.addItem(wx.CheckBox(self, label=tableOfContentsText))
		self.tableOfContentsCheckBox.SetValue(metadata["toc"])

		numberHeadingsText = _("Try to automatically &number headings")
		self.numberHeadingsCheckBox = sHelper.addItem(wx.CheckBox(self, label=numberHeadingsText))
		self.numberHeadingsCheckBox.SetValue(metadata["autonumber-headings"])

		extratagsText = _("Enable e&xtra tags")
		self.extratagsCheckBox = sHelper.addItem(wx.CheckBox(self, label=extratagsText))
		self.extratagsCheckBox.SetValue(metadata["extratags"])

		backTranslateExtraTagsText = _("Allow extratags bac&k translation")
		self.backTranslateExtraTagsCheckBox = sHelper.addItem(wx.CheckBox(self, label=backTranslateExtraTagsText))
		self.backTranslateExtraTagsCheckBox.SetValue(metadata["extratags-back"])

		detectExtratagsText = _("&Detect extratags if possible")
		self.detectExtratagsCheckBox = sHelper.addItem(wx.CheckBox(self, label=detectExtratagsText))
		self.detectExtratagsCheckBox.SetValue(True)

		titleLabelText = _("&Title")
		self.titleTextCtrl = sHelper.addLabeledControl(titleLabelText, wx.TextCtrl)
		self.titleTextCtrl.SetValue(metadata["title"])
		self.titleTextCtrl.Bind(wx.EVT_TEXT, self.onUpdateMetadata)

		subtitleText = _("S&ubtitle")
		self.subtitleTextCtrl = sHelper.addLabeledControl(subtitleText, wx.TextCtrl)
		self.subtitleTextCtrl.SetValue(metadata["subtitle"])
		self.subtitleTextCtrl.Bind(wx.EVT_TEXT, self.onUpdateMetadata)

		HTMLTemplatesText = _("HTML temp&late to use")
		self.HTMLTemplatesListBox = sHelper.addLabeledControl(HTMLTemplatesText, wx.Choice, choices=getHTMLTemplates())
		self.HTMLTemplatesListBox.SetSelection(getDefaultHTMLTemplateID(metadata["template"]))
		self.HTMLTemplatesListBox.Bind(wx.EVT_CHOICE, self.onUpdateMetadata)

		correspondingMetadataBlockText = _("Corres&ponding metadata block")
		self.correspondingMetadataBlock = sHelper.addLabeledControl(correspondingMetadataBlockText, wx.TextCtrl, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_PROCESS_TAB, size=(700, -1))
		self.correspondingMetadataBlock.SetValue(getMetadataBlock(metadata))

		checkboxesToBind = [self.tableOfContentsCheckBox, self.numberHeadingsCheckBox, self.extratagsCheckBox, self.backTranslateExtraTagsCheckBox]
		for checkbox in checkboxesToBind:
			checkbox.Bind(wx.EVT_CHECKBOX, self.onUpdateMetadata)

		self.virtualBufferBtn = bHelper.addButton(self, label=_("Show in &virtual buffer"))
		self.virtualBufferBtn.Bind(wx.EVT_BUTTON, self.onVB)
		if defaultAction == IM_actions["virtualBuffer"]: self.virtualBufferBtn.SetDefault()
		self.browserBtn = bHelper.addButton(self, label=_("Show in &browser"))
		self.browserBtn.Bind(wx.EVT_BUTTON, self.onBrowser)
		if defaultAction == IM_actions["browser"]: self.browserBtn.SetDefault()
		self.copyToClipBtn = bHelper.addButton(self, label=_("&Copy to clipboard"))
		self.copyToClipBtn.Bind(wx.EVT_BUTTON, self.onCopyToClipBtn)
		if defaultAction == IM_actions["copyToClip"]: self.copyToClipBtn.SetDefault()
		saveResultBtn = bHelper.addButton(self, label=_("&Save the result as..."))
		saveResultBtn.Bind(wx.EVT_BUTTON, self.onSave)
		if defaultAction == IM_actions["saveResultAs"]: saveResultBtn.SetDefault()
		saveSourceBtn = bHelper.addButton(self, label=_("Save the sou&rce as..."))
		saveSourceBtn.Bind(wx.EVT_BUTTON, lambda evt: self.onSave(evt, source=True))
		if defaultAction == IM_actions["saveSourceAs"]: saveSourceBtn.SetDefault()
		sHelper.addItem(bHelper)

		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.CANCEL))

		mainSizer.Add(sHelper.sizer,border=20,flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.destFormatListBox.SetFocus()
		self.onDestFormatListBox(None)

	def onUpdateMetadata(self, evt=None):
		self.updateMetadata()
		self.correspondingMetadataBlock.SetValue(getMetadataBlock(self.metadata))

	def onDestFormatListBox(self, evt):
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		if destFormatChoices_ > 0: self.browserBtn.Disable()
		else: self.browserBtn.Enable()
		if destFormatChoices_ != 2:
			self.detectExtratagsCheckBox.Disable()
			self.genMetadataCheckBox.Disable()
			self.backTranslateExtraTagsCheckBox.Enable()
			self.correspondingMetadataBlock.Enable()
			self.extratagsCheckBox.Enable()
			self.numberHeadingsCheckBox.Enable()
			self.tableOfContentsCheckBox.Enable()
			self.titleTextCtrl.Enable()
			self.subtitleTextCtrl.Enable()
			self.HTMLTemplatesListBox.Enable()
		else:
			self.detectExtratagsCheckBox.Enable()
			self.genMetadataCheckBox.Enable()
			self.backTranslateExtraTagsCheckBox.Disable()
			self.correspondingMetadataBlock.Disable()
			self.extratagsCheckBox.Disable()
			self.numberHeadingsCheckBox.Disable()
			self.tableOfContentsCheckBox.Disable()
			self.titleTextCtrl.Disable()
			self.subtitleTextCtrl.Disable()
			self.HTMLTemplatesListBox.Disable()

	def onBrowser(self, evt): self.onExecute(False)

	def onVB(self, evt): self.onExecute(True)
	def updateMetadata(self):
		metadata = self.metadata
		metadata["toc"] = self.tableOfContentsCheckBox.IsChecked()
		metadata["extratags"] = self.extratagsCheckBox.IsChecked()
		metadata["extratags-back"] = self.backTranslateExtraTagsCheckBox.IsChecked()
		metadata["genMetadata"] = self.genMetadataCheckBox.IsChecked()
		metadata["autonumber-headings"] = self.numberHeadingsCheckBox.IsChecked()
		metadata["detectExtratags"] = self.detectExtratagsCheckBox.IsChecked()
		metadata["title"] = self.titleTextCtrl.GetValue()
		metadata["subtitle"] = self.subtitleTextCtrl.GetValue()
		templateID = self.HTMLTemplatesListBox.GetSelection()
		metadata["template"] = getHTMLTemplateFromID(templateID)

	def onExecute(self, vb=False):
		self.updateMetadata()
		metadata = self.metadata
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		if destFormatChoices_ == 0: convertToHTML(self.text, metadata, useTemplateHTML=True, save=not vb)
		elif destFormatChoices_ == 1: convertToHTML(self.text, metadata, save=False, src=True)
		elif destFormatChoices_ == 2: convertToMD(self.text, metadata)
		self.Destroy()

	def onCopyToClipBtn(self, event):
		self.updateMetadata()
		metadata = self.metadata
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		if destFormatChoices_ == 0: copyToClipAsHTML(convertToHTML(self.text, metadata, display=False))
		elif destFormatChoices_ == 1: api.copyToClip(convertToHTML(self.text, metadata, src=True, display=False))
		else: api.copyToClip(convertToMD(self.text, metadata, display=False))
		self.Destroy()

	def onSave(self, event, source=False):
		self.updateMetadata()
		metadata = self.metadata
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		formats = [
			"HTML format (*.htm, *.html)|*.htm;*.html",
			"Text file (*.txt)|*.txt",
			"Markdown file (*.md)|*.md"
		]
		format = formats[1] if source else formats[destFormatChoices_]
		dlg = wx.FileDialog(None, _("Select the location"), metadata["path"], metadata["filename"], format, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			fp = dlg.GetDirectory() + '\\' + dlg.GetFilename()
			if source: text = self.text
			else:
				text = ''
				if destFormatChoices_ == 0: convertToHTML(self.text, metadata, useTemplateHTML=True, save=True, fp=fp)
				elif destFormatChoices_ == 1: text = convertToHTML(self.text, metadata, src=True, display=False)
				else: text = convertToMD(self.text, metadata, display=False)
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
