# coding: utf-8
"""
Markdown Forever

A small NVDA add-on that provides preview of MarkDown or HTML contents in any textarea

Copyright 2019 André-Abush Clause, released under GPL.
GitHub: https://github.com/andre9642/nvda-markdownForever/
"""

from __future__ import unicode_literals
import os
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

import markdown2
import htmlClipboard

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
    toc = (res.toc_html.encode("UTF-8") if res.toc_html else '')
    if toc != '':
        toc = ("<h1>%s</h1>" % _("Table of contents")) + toc
    return res.encode("UTF-8"), toc

def copyToClipAsHTML():
    body, toc = md2HTML(getText())
    htmlClipboard.PutHtml(body)
    if htmlClipboard.GetHtml() == body: ui.message(_("Result copied in clipboard"))
    else: ui.message(_("An error occurred"))

def convert(text, save=False):
    body, toc = md2HTML(text)
    if save:
        fp = os.path.dirname(__file__).decode("mbcs") + r"\\tmp.html"
        useTemplateHTML = not re.search("</html>", body, re.IGNORECASE)
        title = _("Conversion (%s)") % time.strftime("%X %x")
        if useTemplateHTML:
            body = template_HTML.format(title=title, body=(toc+body))
        f = open(fp, "w")
        f.write(body.encode("UTF-8"))
        f.close()
        os.startfile(fp)
    else:
        ui.browseableMessage(
            (toc + body),
            _("Preview of MarkDown or HTML"),
            True
        )

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    scriptCategory = _("Markdown Forever")
    
    def script_copyToClipAsHTML(self, gesture):
        copyToClipAsHTML()
    script_copyToClipAsHTML.__doc__ = _("Copy the result to clipboard as HTML")

    def script_showViaNVDA(self, gesture):
        text = getText()
        convert(text)
    script_showViaNVDA.__doc__ = _("Preview of MarkDown or HTML trough NVDA")

    def script_showInBrowser(self, gesture):
        text = getText()
        convert(text, True)

    script_showInBrowser.__doc__ = _(
        "Preview of MarkDown or HTML trough your default browser")

    __gestures = {
        "kb:nvda+alt+j": "copyToClipAsHTML",
        "kb:nvda+alt+k": "showViaNVDA",
        "kb:nvda+alt+l": "showInBrowser"
    }
    
