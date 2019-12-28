# coding: utf-8
from __future__ import unicode_literals
import addonHandler
addonHandler.initTranslation()
import api
import controlTypes
from logHandler import log

def escape(text):
	chars = {
		"&": "&amp;",
		'"': "&quot;",
		"'": "&apos;",
		"<": "&lt;",
		">": "&gt;",
	}
	return "".join(chars.get(c,c) for c in text)

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
		if tag == 'a': out.append('\n<a href="%s">' % (obj.value if obj.value else '#'))
		else: out.append("\n<%s>" % tag)
	if controlTypes.STATE_CHECKED in obj.states: out.append("✓")
	elif controlTypes.STATE_CHECKABLE in obj.states: out.append("◻")
	if controlTypes.STATE_HALFCHECKED in obj.states: out.append("<->")
	if obj.children:
		for child in obj.children: out.append(getHTML(child, tag))
	elif previousTag != "li" or (previousTag == "li" and obj.name not in ["• "]):
		if obj.name and (obj.parent.role != controlTypes.ROLE_LABEL or (obj.parent.role == controlTypes.ROLE_LABEL and obj.parent.name != obj.name)): out.append(obj.name)
	if obj.role == controlTypes.ROLE_EDITABLETEXT:
		out.append("………")
		if obj.value:
			beg = "<pre>" if controlTypes.STATE_MULTILINE in obj.states else '<code>'
			end = "</pre>" if controlTypes.STATE_MULTILINE in obj.states else '</code>'
			out.append(beg + escape(obj.value) + end)
	if tag: out.append("</%s>\n" % tag)
	return ' '.join(out)

def getAllHTML():
	if not isVirtualDocument(): return _("Invalid document"), True
	obj = api.getReviewPosition().obj
	return ''.join(getHTML(obj.rootNVDAObject)), False

