# coding: utf-8
from __future__ import unicode_literals
import addonHandler
addonHandler.initTranslation()
import api
from logHandler import log

def isVirtualDocument():
	obj = api.getReviewPosition().obj
	return hasattr(obj, "rootNVDAObject")

def getHTML(obj, previousTag=None):
	if not obj: return ''
	out = []
	tag = None
	if hasattr(obj, "IA2Attributes") and "tag" in obj.IA2Attributes.keys(): tag = obj.IA2Attributes["tag"]
	elif hasattr(obj, "HTMLNodeName"): tag = obj.HTMLNodeName.lower()
	if tag:
		if tag == 'a': out.append('\n<a href="%s">' % obj.value)
		else: out.append("\n<%s>" % tag)
	if obj.children:
		for child in obj.children:
			out.append(getHTML(child, tag))
	elif previousTag != "li" or (previousTag == "li" and obj.name not in ["• "]):
		out_ = ""
		if obj.name: out_ += obj.name
		out.append(out_)
	if tag: out.append("</%s>\n" % tag)
	return ' '.join(out)

def getAllHTML():
	if not isVirtualDocument(): return _("Invalid document"), True
	obj = api.getReviewPosition().obj
	return ''.join(getHTML(obj.rootNVDAObject)), False

