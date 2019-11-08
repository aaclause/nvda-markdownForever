# coding: utf-8
"""
Markdown Forever

Full-featured Markdown and HTML converter for NVDA

Copyright 2019 André-Abush Clause, Sof and other contributors. Released under GPL.
GitHub: https://github.com/andre9642/nvda-markdownForever/
"""

from __future__ import unicode_literals
import codecs
import locale
import os, os.path
import sys
from . import updateCheck
isPy3 = True if sys.version_info >= (3, 0) else False
baseDir = os.path.dirname(__file__)
if not isPy3: baseDir = baseDir.decode("mbcs")
libCommon = os.path.join(baseDir, "lib", "common")
if isPy3: libPy = os.path.join(os.path.dirname(__file__), "lib/py3")
else: libPy = os.path.join(baseDir, "lib", "py2")

sys.path.append(libCommon)
sys.path.append(libPy)
import re
import time
if isPy3:
	from urllib.request import Request, urlopen
else: from urllib2 import Request, urlopen
import ssl
import gui, wx

import addonHandler
addonHandler.initTranslation()
import api
import config
import globalPluginHandler
import languageHandler
import scriptHandler
import textInfos
import treeInterceptorHandler
import ui
import versionInfo
from logHandler import log

import markdown2
import html2markdown
import html2text
import yaml
import winClipboard
from bs4 import BeautifulSoup
sys.path.remove(libCommon)
sys.path.remove(libPy)

IM_actions = {
	"saveAs": 0,
	"browser": 1,
	"virtualBuffer": 2,
	"copyToClip": 3
}
IM_actionLabels = [
	_("Save as"), 
	_("Show in browser"),
	_("Show in virtual buffer"),
	_("Copy to clipboard")
]
confSpecs = {
	"autoCheckUpdate": "boolean(default=True)",
	"lastNVDAVersion": 'string(default="unknown")',
	"updateChannel": "option(dev, stable, default=stable)",
	"lastCheckUpdate": "float(min=0, default=0)",
	"toc": 'boolean(default=False)',
	"extratags": 'boolean(default=True)',
	"extratags-back": 'boolean(default=True)',
	"detectExtratags": 'boolean(default=True)',
	"genMetadata": 'boolean(default=True)',
	"IM_defaultAction": 'integer(min=0, max=3, default=0)',
	"defaultPath": 'string(default="%USERPROFILE%\documents")',
	"markdownEngine": 'option("html2markdown", "html2text", default="html2text")',
	"HTMLTemplate": 'string(default="default")',
	"HTMLTemplates": {}
}
markdownEngines = ["html2text", "html2markdown"]
markdownEngineLabels = [
	_("html2text: turn HTML into equivalent Markdown-structured text"),
	_("html2markdown: conservatively convert html to markdown"),
]
config.conf.spec["markdownForever"] = confSpecs

addonName = _("Markdown Forever")
_addonDir = os.path.join(baseDir, "..", "..")
addonInfos = addonHandler.Addon(_addonDir).manifest
internalTocTag = ":{tableOfContent:%s}/!$£:" % time.time()
internalAutoNumber = r"\!"
str_ = str if isPy3 else unicode

if isPy3: curDir = os.path.dirname(__file__)
else: curDir = os.path.dirname(__file__).decode("mbcs")
addonPath = '\\'.join(curDir.split('\\')[0:-2])
defaultLanguage = languageHandler.getLanguage()
pathPattern = r"^(?:%|[a-zA-Z]:[\\/])[^:*?\"<>|]+\.html?$"
URLPattern = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
template_HTML = ''

def getText():
	err = ''
	obj = api.getFocusObject()
	treeInterceptor = obj.treeInterceptor
	if isinstance(treeInterceptor, treeInterceptorHandler.DocumentTreeInterceptor) and not treeInterceptor.passThrough: obj = treeInterceptor
	try: info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
	except (RuntimeError, NotImplementedError): info = None
	if not info or info.isCollapsed:
		try:
			text = obj.makeTextInfo(textInfos.POSITION_ALL).text
		except (RuntimeError, NotImplementedError):
			obj = api.getNavigatorObject()
			text = obj.value
	else: text = info.text
	isLocalFile = False
	if re.match(pathPattern, text):
		fp = realpath(text)
		if os.path.isfile(fp):
			f = open(fp, "rb")
			raw = f.read()
			if raw.startswith(codecs.BOM_UTF8): raw = raw[3:]
			f.close()
			text = raw.decode()
			isLocalFile =True
		else:
			err = _("Invalid file path")
	if not isLocalFile and re.match(URLPattern, text.strip()):
		ctx = ssl.create_default_context()
		ctx.check_hostname = False
		ctx.verify_mode = ssl.CERT_NONE
		try:
			req = Request(text)
			req.add_header("user-agent", "private")
			req.add_header("Accept", "text/html")
			req.add_header("Accept-encoding", "identity")
			j = urlopen(req, context=ctx)
			data = j.read()
			possibleEncodings = []
			if isPy3: enc_ = j.headers.get_content_charset("UTF-8")
			else: enc_ = j.headers.getparam("charset")
			log.debug("%s charset found in HTTP headers" % enc_)
			possibleEncodings.append(enc_)
			pattern = r"^.*charset=\"?([0-9a-zA-Z\-]+)\"?.*$"
			try:
				start_ = data.index(b"charset=")
				if start_ >= 0:
					enc_ = data[start_:(start_+42)].split(b">")[0].replace(b'"', b"").replace(b'\'', b"")
					enc_ = re.sub(pattern, r"\1", enc_.decode("UTF-8"))
					possibleEncodings.insert(0, enc_)
			except ValueError: log.debug(j.headers)
			possibleEncodings.append("UTF-8")
			log.debug("%s charset found in <head> HTML" % enc_)
			for possibleEncoding in possibleEncodings:
				ok = 0
				try:
					log.debug("Trying %s" % possibleEncoding)
					text = data.decode(possibleEncoding)
					ok = 1
					break
				except (LookupError, UnicodeDecodeError) as e: log.debug(e)
			if not ok:
				log.error(possibleEncodings)
				err = _("Unable to guess the encoding")
		except BaseException as e: err = str_(e).strip()
	if not text: err = _("No text")
	return text, err

def md2HTML(md, toc, ol=True):
	extras = ["footnotes", "tables", "fenced-code-blocks", "task_list", "header-ids", "wiki-tables", "spoiler"]
	if toc: extras.append("toc")
	res = markdown2.markdown(md, extras=extras)
	toc = '<nav role="doc-toc" id="doc-toc">%s</nav>' % res.toc_html if res.toc_html and res.toc_html.count("<li>") > 1 else ''
	if ol: toc = toc.replace("<ul>", "<ol>").replace("</ul>", "</ol>")
	return res, toc

def writeFile(fp, content):
	fp = realpath(fp)
	f = open(fp, "wb")
	if isPy3: f.write(content.encode())
	else:
		try: f.write(bytearray(content, "UTF-8"))
		except UnicodeDecodeError: f.write(bytearray(content.decode("UTF-8"), "UTF-8"))
	f.close()

def backTranslateExtraTags(text):
	soup = BeautifulSoup(text)
	matches = soup.findAll(["span", "div"], class_=re.compile(r"^extratag_%.+%$"))
	for match in matches:
		extratag = match["class"][-1].split('_', 1)[-1]
		try:
			match.string.replaceWith(extratag)
			match.unwrap()
		except AttributeError as e: log.error(e)
	return str_(soup)

def extractMetadata(text):
	metadata = {}
	if len(text) > 4 and text.startswith("---"):
		ln = text[3]
		if ln in ["\r", "\n"]:
			if ln == "\r" and text[4] == "\n": ln = "\r\n"
			try:
				end = (text.index(ln * 2)-3)
				y = text[(3 + len(ln)):end].strip()
				docs = yaml.load_all(y, Loader=yaml.FullLoader)
				for doc in docs: metadata = doc
				text = text[end+3:].strip()
			except (ValueError, yaml.scanner.ScannerError): pass
	if not isinstance(metadata, dict): metadata = {}
	HTMLHead = [
		'<meta name="generator" content="MarkdownForever" />',
		'<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes" />'
	]
	HTMLHeader = []
	metadata = {k.lower(): v for k, v in metadata.items()}
	if "language" in metadata.keys(): metadata["lang"] = metadata.pop("language")
	if "authors" in metadata.keys(): metadata["author"] = metadata.pop("authors")
	if not "autonumber-headings" in metadata.keys() or not isinstance(metadata["autonumber-headings"], (int, bool)): metadata["autonumber-headings"] = True
	if not "title" in metadata.keys() or not isinstance(metadata["title"], (str, str_)): metadata["title"] = _("No title")
	if not "subtitle" in metadata.keys() or not isinstance(metadata["subtitle"], (str, str_)): metadata["subtitle"] = ""
	metadata["title"] = str_(processExtraTags(BeautifulSoup(metadata["title"], "html.parser"))[-1].text)
	if not "toc" in metadata.keys() or not isinstance(metadata["toc"], (int, bool)): metadata["toc"] = config.conf["markdownForever"]["toc"]
	if not "extratags" in metadata.keys() or not isinstance(metadata["extratags"], (int, bool)): metadata["extratags"] = config.conf["markdownForever"]["extratags"]
	if not "extratags-back" in metadata.keys() or not isinstance(metadata["extratags-back"], (int, bool)): metadata["extratags-back"] = config.conf["markdownForever"]["extratags-back"]
	if not "detectExtratags" in metadata.keys() or not isinstance(metadata["detectExtratags"], (int, bool)): metadata["detectExtratags"] = config.conf["markdownForever"]["detectExtratags"]
	if not "genMetadata" in metadata.keys() or not isinstance(metadata["genMetadata"], (int, bool)): metadata["genMetadata"] = config.conf["markdownForever"]["genMetadata"]
	if not "lang" in metadata.keys() or not isinstance(metadata["lang"], (str, str_)): metadata["lang"] = defaultLanguage
	if not "mathjax" in metadata.keys() or not isinstance(metadata["mathjax"], (int, bool)): metadata["mathjax"] = False
	metadata["path"] = metadata["path"] if "path" in metadata.keys() and isPath(metadata["path"]) else config.conf["markdownForever"]["defaultPath"]
	metadata["filename"] = metadata["filename"] if "filename" in metadata.keys() and isValidFileName(metadata["filename"]) else "MDF_%s" % time.strftime("%y-%m-%d_-_%H-%M-%S")
	if metadata["mathjax"]:
		HTMLHead.append('<script src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>')
	if "title" in metadata.keys():
		HTMLHead.append("<title>%s</title>" % metadata["title"])
		HTMLHeader.append('<h1 class="title">%s</h1>' % metadata["title"])
	if "subtitle" in metadata:
		HTMLHeader.append('<p class="subtitle">%s</p>' % metadata["subtitle"])
	if "keywords" in metadata.keys():
		HTMLHead.append('<meta name="keywords" content="%s" />' % metadata["keywords"])
	if "author" in metadata.keys():
		if isinstance(metadata["author"], (str, str_)): metadata["author"] = [metadata["author"]]
		for author in metadata["author"]:
			HTMLHeader.append('<p class="author">%s</p>' % md2HTML(author, toc=False)[0])
			author_ = str_(processExtraTags(BeautifulSoup(author, "html.parser"))[-1].text)
			HTMLHead.append('<meta name="author" content="%s" />' % author_)
	if "css" in metadata.keys():
		if isinstance(metadata["css"], (str, str_)): metadata["css"] = [metadata["css"]]
		for css in metadata["css"]: HTMLHead.append('<link rel="stylesheet" href="%s" />' % css)
	if "date" in metadata.keys():
		HTMLHeader.append('<p class="date">%s</p>' % metadata["date"])
		HTMLHead.append('<meta name="dcterms.date" content="%s" />' % metadata["date"])
	metadata["HTMLHead"] = '\n'.join(HTMLHead)
	if not HTMLHeader: HTMLHeader = ""
	else: metadata["HTMLHeader"] = '\n'.join(HTMLHeader)
	return metadata, text

def getHTMLTemplate():
	global template_HTML
	if template_HTML: return template_HTML
	HTMLTemplate = realpath(config.conf["markdownForever"]["HTMLTemplate"])
	if HTMLTemplate != "default" and os.path.isfile(HTMLTemplate): fp = HTMLTemplate
	else: fp = os.path.join(curDir, "res", "default.tpl")
	f = open(fp, "rb")
	template_HTML = f.read().decode("UTF-8").strip()
	f.close()
	return template_HTML

def processExtraTags(soup, lang='', allRepl=True, allowBacktranslate=True):
	try:
		if not lang and defaultLanguage == "en": lang = "enu"
		if lang: locale.setlocale(locale.LC_ALL, lang)
	except locale.Error as err:
		log.error(err)
		msg = _("Metadata and extra tags error. '%s' value was not recognized for lang field." % lang)
		return False, msg
	replacements = [
		("%day%", time.strftime("%A"), 1),
		("%Day%", time.strftime("%A").capitalize(), 1),
		("%dday%", time.strftime("%d"), 1),
		("%month%", time.strftime("%B"), 1),
		("%Month%", time.strftime("%B").capitalize(), 1),
		("%dmonth%", time.strftime("%m"), 1),
		("%year%", time.strftime("%y").capitalize(), 1),
		("%Year%", time.strftime("%Y").capitalize(), 1),
		("%date%", time.strftime("%x"), 1),
		("%time%", time.strftime("%X"), 1),
		("%now%", time.strftime("%c"), 1),
		("%addonVersion%", addonInfos["version"], 1),
		("%NVDAVersion%", versionInfo.version, 1),
		("%toc%", internalTocTag, 0)
	]
	for toSearch, replaceBy, replaceAlways in replacements:
		if allRepl or (not allRepl and replaceAlways):
			try:
				matches = soup.findAll(text=re.compile(r".{0,}%s.{0,}" % toSearch))
				for match in matches:
					parents = [parent.name for parent in match.parents]
					if "code" not in parents and "pre" not in parents:
						if allowBacktranslate:
							tag = "div" if "%toc%" in toSearch else "span"
							newContent = str_(match.string).replace(toSearch, '<%s class="extratag_%s">%s</%s>' % (tag, toSearch, replaceBy, tag))
							match.string.replaceWith(BeautifulSoup(newContent))
						else: match.string.replaceWith(match.string.replace(toSearch, replaceBy))
			except (UnicodeEncodeError, UnicodeDecodeError):
				match.replaceWith(match.string.replace(toSearch, replaceBy.decode(locale.getlocale()[1])))
	if lang: locale.setlocale(locale.LC_ALL, '')
	return True, soup

def applyAutoNumberHeadings(soup, before=""):
	patternHeaders = re.compile(r"h[0-6]")
	matches = soup.findAll(patternHeaders, recursive=True)
	l = []
	previousHeadingLevel = 0
	for match in matches:
		print(match.text.strip())
		if  match.text.strip().startswith(internalAutoNumber):
			match.string.replaceWith(match.string.replace(internalAutoNumber, ""))
			continue
		currentHeadingLevel = int(match.name[-1])
		if currentHeadingLevel == previousHeadingLevel: l[-1] += 1
		elif currentHeadingLevel < previousHeadingLevel:
			try:
				l = l[0:currentHeadingLevel]
				l[-1] += 1
			except KeyError as err:
				log.error((repr(err), l, previousHeadingLevel, currentHeadingLevel, match.text, d))
				return soup
		else:
			diff = currentHeadingLevel-previousHeadingLevel
			l += [0]*diff
			l[-1] = 1
		current = '.'.join([str_(k) for k in l])
		current = re.sub(r"^(0\.)+(.+)$", r"\2", current)
		match.string.replaceWith("%s. %s" % (current, match.string))
		previousHeadingLevel = currentHeadingLevel
	return soup

def convertToHTML(text, metadata, save=False, src=False, useTemplateHTML=True, display=True, fp=''):
	toc = metadata["toc"]
	title = metadata["title"]
	lang = metadata["lang"]
	extratags = metadata["extratags"]
	HTMLHeader = metadata["HTMLHeader"]
	HTMLHead = metadata["HTMLHead"]
	while "  " in text: text = text.replace("  ", "  ")
	body, toc = md2HTML(text, toc, metadata["autonumber-headings"])
	content = BeautifulSoup(body, "html.parser")
	if metadata["autonumber-headings"]:
		content = applyAutoNumberHeadings(content)
	if extratags:
		ok, content = processExtraTags(content, lang=metadata["langd"] if "langd" in metadata.keys() else '', allowBacktranslate=metadata["extratags-back"])
		if not ok: return wx.CallAfter(gui.messageBox, content, addonName, wx.OK|wx.ICON_ERROR)
	content = str_(content.prettify()) if save else str_(content)
	if toc:
		if internalTocTag not in content:
			pre = "<h1>%s</h1>" % _("Table of contents")
			content = pre + internalTocTag + content
		content = content.replace(internalTocTag, toc)
	if save:
		metadata["path"] = realpath(metadata["path"])
		if not os.path.exists(metadata["path"]): fp = os.path.dirname(__file__) + r"\\tmp.html"
		if not fp: fp = os.path.join(metadata["path"], "%s.html" % metadata["filename"])
		if not isPy3:
			try: fp = fp.decode("mbcs")
			except UnicodeEncodeError: pass
		if useTemplateHTML: useTemplateHTML = not re.search("</html>", body, re.IGNORECASE)
		if not title.strip(): title = _("Markdown to HTML conversion")+(" (%s)" % time.strftime("%X %x"))
		if useTemplateHTML:
			body = content
			content = getHTMLTemplate()
			content = content.replace("{lang}", lang, 1)
			content = content.replace("{head}", HTMLHead, 1)
			content = content.replace("{header}", HTMLHeader, 1)
			content = content.replace("{body}", body, 1)
		writeFile(fp, content)
		if display: os.startfile(realpath(fp))
	else:
		if lang != defaultLanguage: content = "<div lang=\"%s\">%s</div>" % (lang, content)
		if display:
			title = "%s%s" % (title + " - " if title else title, _("Markdown to HTML conversion (preview)")) if not src else _("Markdown to HTML source conversion")
			ui.browseableMessage("%s%s" % (HTMLHeader, content), title, not src)
		else: return "%s %s" % (HTMLHeader, content)

def getMetadataBlock(metadata, ignore=[]):
	ignore_ = ["HTMLHead", "HTMLHeader", "genMetadata", "detectExtratags"]
	metadata = {k: v for k, v in metadata.items() if k not in ignore and k not in ignore_}
	if isPy3: dmp = yaml.dump(metadata, encoding="UTF-8", allow_unicode=True, explicit_start=True, explicit_end=True)
	else: dmp = yaml.dump(metadata, Dumper=KludgeDumper, encoding="UTF-8", allow_unicode=True, explicit_start=True, explicit_end=True)
	return dmp.decode("UTF-8")

def convertToMD(text, metadata, display=True):
	title = metadata["title"]
	dmp = getMetadataBlock(metadata) if metadata["genMetadata"] else ""
	if metadata["detectExtratags"]: text = backTranslateExtraTags(text)
	if config.conf["markdownForever"]["markdownEngine"] == "html2markdown":
		convert = html2markdown.convert
	else: convert = html2text.html2text
	res = ("%s\n%s" % (dmp, convert(text))).strip()
	if display:
		pre = (title + " - ") if title else title
		ui.browseableMessage(res, pre + _("HTML to Markdown conversion"), False)
	else: return res

def copyToClipAsHTML(html):
	winClipboard.copy(html, html=True)
	return html == winClipboard.get(html=True)

def realpath(path):
	path = path.lower()
	vars = ["appdata", "tmp", "temp", "userprofile"]
	for var in vars: path = path.replace("%%%s%%" % var, os.environ[var])
	return path

def isPath(path):
	path = realpath(path)
	return os.path.exists(path) and os.path.isdir(path)

def isValidFileName(filename):
	return bool(re.match(r"^[^\\/:*?\"<>|]+$", filename))

from yaml.dumper import Dumper
from yaml.representer import SafeRepresenter
if not isPy3:
	class KludgeDumper(Dumper): pass

	KludgeDumper.add_representer(str, SafeRepresenter.represent_str)
	KludgeDumper.add_representer(unicode, SafeRepresenter.represent_unicode)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = addonName

	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		self.createMenu()
		self.updateCheckThread = updateCheck.UpdateCheck()
		self.updateCheckThread.start()
		if not self.updateCheckThread.is_alive():
			log.error("Update check system not started")

	def createMenu(self):
		menu = wx.Menu()
		item = menu.Append(wx.ID_ANY, _("Documentation"), _("Opens the addon's documentation"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onDoc, item)
		item = menu.Append(wx.ID_ANY, "%s..." % _("Settings"), _("Add-on settings"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, item)
		item = menu.Append(wx.ID_ANY, "%s..." % _("&Check for update"), _("Checks if update is available"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onUpdate, item)
		item = menu.Append(wx.ID_ANY, _("&Web site"), _("Open the add-on website."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onWebsite, item)
		self.markdownForeverMenu = gui.mainFrame.sysTrayIcon.preferencesMenu.AppendSubMenu(menu, _("Mar&kdown Forever"), _("%s menu") % addonName)

	def removeMenu(self):
		if hasattr(self, "markdownForeverMenu"): gui.mainFrame.sysTrayIcon.preferencesMenu.Remove(self.markdownForeverMenu)

	def terminate(self):
		self.updateCheckThread.stop()
		self.updateCheckThread.join()
		if self.updateCheckThread.is_alive(): log.info("Update check system stopped")
		self.removeMenu()

	@staticmethod
	def onDoc(evt):
		MDLocation = os.path.join(addonPath, "doc", defaultLanguage.split('_')[0]+".md")
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

	@staticmethod
	def onSettings(evt):
		gui.mainFrame._popupSettingsDialog(SettingsDlg)

	def script_md2htmlSrcInNVDA(self, gesture):
		text, err = getText()
		if err: return ui.message(err)
		metadata, text = extractMetadata(text)
		convertToHTML(text, metadata, save=False, src=True)
	script_md2htmlSrcInNVDA.__doc__ = _("Show the HTML source from Markdown")

	def script_html2md(self, gesture):
		text, err = getText()
		if err: return ui.message(err)
		metadata, text = extractMetadata(text)
		convertToMD(text, metadata)
	script_html2md.__doc__ = _("HTML to Markdown conversion")

	def script_md2htmlInNVDA(self, gesture):
		text, err = getText()
		if err: return ui.message(err)
		metadata, text = extractMetadata(text)
		convertToHTML(text, metadata, useTemplateHTML=False)
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
		api.copyToClip(convertToHTML(text, metadata, src=True, display=False))
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
		text, err = getText()
		if err: return ui.message(err)
		metadata, text = extractMetadata(text)
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
	def __init__(self, parent=None, title=_("Interactive mode") + " — MarkdownForever", text=''):
		self.metadata, self.text = extractMetadata(text)
		metadata = self.metadata
		defaultAction = config.conf["markdownForever"]["IM_defaultAction"]
		super(InteractiveModeDlg, self).__init__(parent, title=title)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)

		isHTMLPattern = re.search("(?:</html>|</p>)", self.text, re.IGNORECASE)
		guessDestFormat = 2 if isHTMLPattern else 0
		destFormatText = _("Convert &to")
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

		subtitleText = _("Subtitle")
		self.subtitleTextCtrl = sHelper.addLabeledControl(subtitleText, wx.TextCtrl)
		self.subtitleTextCtrl.SetValue(metadata["subtitle"])
		self.subtitleTextCtrl.Bind(wx.EVT_TEXT, self.onUpdateMetadata)

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
		saveBtn = bHelper.addButton(self, label=_("&Save as..."))
		saveBtn.Bind(wx.EVT_BUTTON, self.onSave)
		if defaultAction == IM_actions["saveAs"]: saveBtn.SetDefault()
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

	def onSave(self, event):
		self.updateMetadata()
		metadata = self.metadata
		destFormatChoices_ = self.destFormatListBox.GetSelection()
		formats = [
			"HTML format (*.htm, *.html)|*.htm;*.html",
			"Text file (*.txt)|*.txt",
			"Markdown file (*.md)|*.md"
		]
		format = formats[destFormatChoices_]
		dlg = wx.FileDialog(None, _("Select the location"), metadata["path"], metadata["filename"], format, style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			fp = dlg.GetDirectory() + '\\' + dlg.GetFilename()
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

class SettingsDlg(gui.settingsDialogs.SettingsDialog):
	title = "markdownForever - %s" % _("Default settings")

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		tableOfContentsText = _("&Generate a table of contents")
		markdownEngine = config.conf["markdownForever"]["markdownEngine"]
		self.tableOfContentsCheckBox = sHelper.addItem(wx.CheckBox(self, label=tableOfContentsText))
		self.tableOfContentsCheckBox.SetValue(config.conf["markdownForever"]["toc"])
		extratagsText = _("Enable e&xtra tags")
		self.extratagsCheckBox = sHelper.addItem(wx.CheckBox(self, label=extratagsText))
		self.extratagsCheckBox.SetValue(config.conf["markdownForever"]["extratags"])

		genMetadataText = _("Generate corresponding &metadata from HTML source")
		self.genMetadataCheckBox = sHelper.addItem(wx.CheckBox(self, label=genMetadataText))
		self.genMetadataCheckBox.SetValue(config.conf["markdownForever"]["genMetadata"])

		defaultActionIMText = _("Default action in interactive mode")
		self.defaultActionListBox = sHelper.addLabeledControl(defaultActionIMText, wx.Choice, choices=IM_actionLabels)
		self.defaultActionListBox.SetSelection(config.conf["markdownForever"]["IM_defaultAction"])
		idEngine = markdownEngines.index(markdownEngine)
		markdownEngineText = _("Markdown Engine")
		self.markdownEngineListBox = sHelper.addLabeledControl(markdownEngineText, wx.Choice, choices=markdownEngineLabels)
		self.markdownEngineListBox.SetSelection(idEngine)
		self.defaultPath = sHelper.addLabeledControl(_("Path"), wx.TextCtrl, value=config.conf["markdownForever"]["defaultPath"])
		manageHTMLTemplatesBtn = bHelper.addButton(self, label="%s..." % _("Manage HTML &templates"))
		manageHTMLTemplatesBtn.Bind(wx.EVT_BUTTON, self.onManageHTMLTemplates)
		sHelper.addItem(bHelper)

	def onManageHTMLTemplates(self, evt):
		manageHTMLTemplatesDialog = ManageHTMLTemplatesDlg(self)
		if manageHTMLTemplatesDialog.ShowModal() == wx.ID_OK:
			self.manageHTMLTemplatesBtn.SetFocus()

	def onOk(self, evt):
		defaultPath = self.defaultPath.GetValue()
		if not os.path.exists(realpath(defaultPath)): return self.defaultPath.SetFocus()
		config.conf["markdownForever"]["toc"] = self.tableOfContentsCheckBox.IsChecked()
		config.conf["markdownForever"]["extratags"] = self.extratagsCheckBox.IsChecked()
		config.conf["markdownForever"]["genMetadata"] = self.genMetadataCheckBox.IsChecked()
		config.conf["markdownForever"]["IM_defaultAction"] = self.defaultActionListBox.GetSelection()
		config.conf["markdownForever"]["markdownEngine"] = markdownEngines[self.markdownEngineListBox.GetSelection()]
		if defaultPath: config.conf["markdownForever"]["defaultPath"] = defaultPath
		super(SettingsDlg, self).onOk(evt)

class ManageHTMLTemplatesDlg(wx.Dialog):
	# Translators: This is the label for the Manage HTML templates dialog.
	def __init__(self, parent=None, title=_("Manage HTML templates")):
		super(ManageHTMLTemplatesDlg, self).__init__(parent, title=title)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		HTMLTemplate = config.conf["markdownForever"]["HTMLTemplate"]
		HTMLTemplates = config.conf["markdownForever"]["HTMLTemplates"].copy()
		if HTMLTemplate in HTMLTemplates: HTMLTemplateID = HTMLTemplates.index(HTMLTemplate+1)
		else: HTMLTemplateID = 0

		HTMLTemplatesTextChoices = [_("Default")]+list(HTMLTemplates.keys())
		HTMLTemplatesText = _("HTML templates list")
		self.HTMLTemplatesTextListBox = sHelper.addLabeledControl(HTMLTemplatesText, wx.Choice, choices=HTMLTemplatesTextChoices)
		self.HTMLTemplatesTextListBox.SetSelection(HTMLTemplateID)
		bHelper.addButton(parent=self, label="%s..." % _("&Edit")).Bind(wx.EVT_BUTTON, self.onEditClick)
		bHelper.addButton(parent=self, label="%s..." % _("&Add")).Bind(wx.EVT_BUTTON, self.onAddClick)
		bHelper.addButton(parent=self, label=_("&Remove")).Bind(wx.EVT_BUTTON, self.onRemoveClick)

		sHelper.addItem(bHelper)
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK|wx.CANCEL))
		mainSizer.Add(sHelper.sizer,border=20,flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		self.HTMLTemplatesTextListBox.SetFocus()

	def onEditClick(self, gesture):
		ui.message(_("Currently unavailable"))

	def onRemoveClick(self, gesture):
		ui.message(_("Currently unavailable"))

	def onAddClick(self, gesture):
		entryDialog = TemplateEntryDlg(self, title=_("Add template"))
		if entryDialog.ShowModal() == wx.ID_OK:
			entry = entryDialog.dictEntry

	def onOk(self, evt):
		self.Destroy()

class TemplateEntryDlg(wx.Dialog):
	# Translators: This is the label for the edit template entry dialog.
	def __init__(self, parent=None, title=_("Edit template")):
		super(TemplateEntryDlg, self).__init__(parent, title=title)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		templateNameText = _("Template &name")
		self.templateName = sHelper.addLabeledControl(templateNameText, wx.TextCtrl)
		templateContentText = _("Content")
		self.templateContent = sHelper.addLabeledControl(templateContentText, wx.TextCtrl, style=wx.TE_MULTILINE|wx.TE_PROCESS_TAB, size=(700, -1))
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK|wx.CANCEL))
		mainSizer.Add(sHelper.sizer,border=20,flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.Bind(wx.EVT_BUTTON,self.onOk,id=wx.ID_OK)
		self.templateName.SetFocus()

	def onOk(self, evt):
		super(TemplateEntryDlg, self).onOk(evt)
