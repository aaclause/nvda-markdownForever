# coding: UTF-8
import json
import locale
import re
import os
import ssl
import sys
import time

import addonHandler
addonHandler.initTranslation()
import api
import config
import globalVars
import languageHandler
import textInfos
import treeInterceptorHandler
from urllib.request import Request, urlopen
import versionInfo
import ui
from logHandler import log

IM_actions = {
	"saveResultAs": 0,
	"saveSourceAs": 4,
	"browser": 1,
	"virtualBuffer": 2,
	"copyToClip": 3,
}
IM_actionLabels = [
	_("Save the result as"),
	_("Save the source as"),
	_("Show in browser"),
	_("Show in virtual buffer"),
	_("Copy to clipboard")
]
markdownEngines = ["html2text", "html2markdown"]
markdownEngineLabels = [
	_("html2text: turn HTML into equivalent Markdown-structured text"),
	_("html2markdown: conservatively convert html to markdown"),
]

baseDir = os.path.dirname(__file__)
libs = os.path.join(baseDir, "lib")
sys.path.append(libs)
import html2markdown
import html2text
import markdown2
import winClipboard
import yaml
from bs4 import BeautifulSoup
from . import virtualDocuments
sys.path.remove(libs)

_addonDir = os.path.join(baseDir, "..", "..")
addonInfos = addonHandler.Addon(_addonDir).manifest
addonSummary = addonInfos["summary"]
addonVersion = addonInfos["version"]
configDir = "%s/markdownForever" % globalVars.appArgs.configPath
defaultLanguage = languageHandler.getLanguage()
internalAutoNumber = r"\!"
internalTocTag = f":\\tableOfContent:{time.time()}/!$£:"
curDir = os.path.dirname(__file__)
addonPath = '\\'.join(curDir.split('\\')[0:-2])
pathPattern = r"^(?:%|[a-zA-Z]:[\\/])[^:*?\"<>|]+\.html?$"
URLPattern = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
minCharTemplateName = 1
maxCharTemplateName = 28

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

def getWindowTitle():
	obj=api.getForegroundObject()
	title = obj.name
	if not isinstance(title, str) or not title or title.isspace():
		title = obj.appModule.appName if obj.appModule else None
		if not isinstance(title, str) or not title or title.isspace():
			title = _("No title")
	return title

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
			enc_ = j.headers.get_content_charset("UTF-8")
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
		except BaseException as e: err = str(e).strip()
	if not text: err = _("No text")
	return text, err

def getMetadataAndTextForMarkDown():
	startTime = time.time()
	res = virtualDocuments.isVirtualDocument()
	if res: text, err = virtualDocuments.getAllHTML()
	else: text, err = getText()
	if err:
		ui.message(err)
		return None, None
	metadata, text = extractMetadata(text)
	if res:
		metadata["title"] = getWindowTitle()
		metadata["timeGen"] = "%.3f s" % (time.time()-startTime)
	return metadata, text

def escapeHTML(text):
	chars = {
		"&": "&amp;",
		'"': "&quot;",
		"'": "&apos;",
		"<": "&lt;",
		">": "&gt;",
	}
	return "".join(chars.get(c,c) for c in text)

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
	f.write(content.encode())
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
	return str(soup)

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
			except (ValueError, yaml.parser.ParserError, yaml.scanner.ScannerError) as err:
				metadataBlock = text[0:end+3]
				text = text[end+3:].strip()
				text = f"! {err}\n\n```\n{metadataBlock}\n```\n\n{text}"
	if not isinstance(metadata, dict): metadata = {}
	HTMLHead = [
		'<meta name="generator" content="MarkdownForever" />',
		'<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes" />'
	]
	HTMLHeader = []
	metadata = {k.lower(): v for k, v in metadata.items()}
	if "language" in metadata.keys(): metadata["lang"] = metadata.pop("language")
	if "authors" in metadata.keys(): metadata["author"] = metadata.pop("authors")
	if not "template" in metadata.keys() or metadata["template"] not in (list(config.conf["markdownForever"]["HTMLTemplates"].copy().keys())+["default", "minimal"]): metadata["template"] = config.conf["markdownForever"]["HTMLTemplate"]
	if not "autonumber-headings" in metadata.keys() or not isinstance(metadata["autonumber-headings"], (int, bool)): metadata["autonumber-headings"] = config.conf["markdownForever"]["autonumber-headings"]
	if not "title" in metadata.keys() or not isinstance(metadata["title"], (str, str)): metadata["title"] = _("No title")
	if not "subtitle" in metadata.keys() or not isinstance(metadata["subtitle"], (str, str)): metadata["subtitle"] = ""
	metadata["title"] = str(processExtraTags(BeautifulSoup(metadata["title"], "html.parser"))[-1].text)
	if not "toc" in metadata.keys() or not isinstance(metadata["toc"], (int, bool)): metadata["toc"] = config.conf["markdownForever"]["toc"]
	if not "extratags" in metadata.keys() or not isinstance(metadata["extratags"], (int, bool)): metadata["extratags"] = config.conf["markdownForever"]["extratags"]
	if not "extratags-back" in metadata.keys() or not isinstance(metadata["extratags-back"], (int, bool)): metadata["extratags-back"] = config.conf["markdownForever"]["extratags-back"]
	if not "detectExtratags" in metadata.keys() or not isinstance(metadata["detectExtratags"], (int, bool)): metadata["detectExtratags"] = config.conf["markdownForever"]["detectExtratags"]
	if not "genMetadata" in metadata.keys() or not isinstance(metadata["genMetadata"], (int, bool)): metadata["genMetadata"] = config.conf["markdownForever"]["genMetadata"]
	if not "lang" in metadata.keys() or not isinstance(metadata["lang"], (str, str)): metadata["lang"] = defaultLanguage
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
		if isinstance(metadata["author"], (str, str)): metadata["author"] = [metadata["author"]]
		for author in metadata["author"]:
			HTMLHeader.append('<p class="author">%s</p>' % md2HTML(author, toc=False)[0])
			author_ = str(processExtraTags(BeautifulSoup(author, "html.parser"))[-1].text)
			HTMLHead.append('<meta name="author" content="%s" />' % author_)
	if "css" in metadata.keys():
		if isinstance(metadata["css"], (str, str)): metadata["css"] = [metadata["css"]]
		for css in metadata["css"]: HTMLHead.append('<link rel="stylesheet" href="%s" />' % css)
	if "date" in metadata.keys():
		HTMLHeader.append('<p class="date">%s</p>' % metadata["date"])
		HTMLHead.append('<meta name="dcterms.date" content="%s" />' % metadata["date"])
	metadata["HTMLHead"] = '\n'.join(HTMLHead)
	if not HTMLHeader: HTMLHeader = ""
	else: metadata["HTMLHeader"] = '\n'.join(HTMLHeader)
	return metadata, text

def getHTMLTemplate(name=None):
	if not name: name = config.conf["markdownForever"]["HTMLTemplate"]
	name = name.lower()
	if name == "minimal":
		return {
			"name": "minimal",
			"description": "",
			"content": "{body}"
		}
	HTMLTemplateDir = realpath(f"{configDir}/{name}.tpl")
	if name != "default" and os.path.isfile(HTMLTemplateDir): fp = HTMLTemplateDir
	else: fp = os.path.join(curDir, "res", "default.tpl")
	with open(fp, "r") as readFile:
		templateEntry = json.load(readFile)
	return templateEntry

def getHTMLTemplates():
	HTMLTemplates = config.conf["markdownForever"]["HTMLTemplates"].copy()
	return [_("Minimal: just the HTML from your Markdown"), _("Default: A minimal template provided by the add-on")]+list(HTMLTemplates.keys())

def getDefaultHTMLTemplateID(name=None):
	if not name: name = config.conf["markdownForever"]["HTMLTemplate"]
	if name == "minimal": return 0
	elif name == "default": return 1
	else:
		HTMLTemplates = getHTMLTemplates()[2:]
		if name in HTMLTemplates: HTMLTemplateID = HTMLTemplates.index(name)
		else: HTMLTemplateID = 1
		return HTMLTemplateID

def getHTMLTemplateFromID(idTemplate):
	if idTemplate == 0: return "minimal"
	elif idTemplate == 1: return "default"
	else: return getHTMLTemplates()[templateID]

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
							newContent = str(match.string).replace(toSearch, '<%s class="extratag_%s">%s</%s>' % (tag, toSearch, replaceBy, tag))
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
		current = '.'.join([str(k) for k in l])
		current = re.sub(r"^(0\.)+(.+)$", r"\2", current)
		match.string.replaceWith("%s. %s" % (current, match.string))
		previousHeadingLevel = currentHeadingLevel
	return soup

def getMetadataBlock(metadata, ignore=[]):
	ignore_ = ["HTMLHead", "HTMLHeader", "genMetadata", "detectExtratags"]
	metadata = {k: v for k, v in metadata.items() if ((isinstance(v, str) and v) or not isinstance(v, str)) and k not in (ignore + ignore_)}
	dmp = yaml.dump(metadata, encoding="UTF-8", allow_unicode=True, explicit_start=True, explicit_end=True)
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

def convertToHTML(text, metadata, save=False, src=False, useTemplateHTML=True, display=True, fp=''):
	toc = metadata["toc"]
	title = metadata["title"]
	lang = metadata["lang"]
	extratags = metadata["extratags"]
	HTMLHeader = metadata["HTMLHeader"]
	HTMLHead = metadata["HTMLHead"]
	body, toc = md2HTML(text, toc, metadata["autonumber-headings"])
	content = BeautifulSoup(body, "html.parser")
	if metadata["autonumber-headings"]:
		content = applyAutoNumberHeadings(content)
	if extratags:
		ok, content = processExtraTags(content, lang=metadata["langd"] if "langd" in metadata.keys() else '', allowBacktranslate=metadata["extratags-back"])
		if not ok: return wx.CallAfter(gui.messageBox, content, addonSummary, wx.OK|wx.ICON_ERROR)
	content = str(content.prettify()) if save else str(content)
	if toc:
		if internalTocTag not in content:
			pre = '<h1 id="toc-heading">%s</h1>' % _("Table of contents")
			content = pre + internalTocTag + content
		content = content.replace(internalTocTag, toc)
	else: content = content.replace(internalTocTag, "%toc%")
	if useTemplateHTML: useTemplateHTML = not re.search("</html>", body, re.IGNORECASE)
	if not title.strip(): title = _("Markdown to HTML conversion") + (" (%s)" % time.strftime("%X %x"))
	if useTemplateHTML:
		body = content
		content = getHTMLTemplate(metadata["template"])["content"]
		content = content.replace("{lang}", lang, 1)
		content = content.replace("{head}", HTMLHead, 1)
		content = content.replace("{header}", HTMLHeader, 1)
		content = content.replace("{body}", body, 1)
	if save:
		metadata["path"] = realpath(metadata["path"])
		if not os.path.exists(metadata["path"]): fp = os.path.dirname(__file__) + r"\\tmp.html"
		if not fp: fp = os.path.join(metadata["path"], "%s.html" % metadata["filename"])
		writeFile(fp, content)
		if display: os.startfile(realpath(fp))
	else:
		if lang != defaultLanguage: content = "<div lang=\"%s\">%s</div>" % (lang, content)
		if display:
			title = f"{title} — %s" % (_("Markdown to HTML conversion (preview)") if not src else _("Markdown to HTML source conversion"))
			if src: content = f"<pre>{escapeHTML(content)}</pre>"
			ui.browseableMessage(content, title, True)
		else:
			return content

