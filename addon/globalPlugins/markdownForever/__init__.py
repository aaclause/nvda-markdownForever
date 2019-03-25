# -*- coding: utf-8 -*-
"""
Markdown Forever

A small NVDA add-on that provides preview of MarkDown or HTML contents in any textarea
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

import markdown2


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


def convert(text, save=False):
    html = markdown2.markdown(text, extras=["footnotes", "tables", "toc"])
    if html.toc_html:
        html.toc_html = "<h1>%s</h1>" % (
            _("Table of contents")
        ) + html.toc_html
    if not html.toc_html:
        html.toc_html = ''
    if save:
        fp = os.path.dirname(__file__).decode("mbcs") + r"\\tmp.html"
        useTemplateHTML = not re.search("</html>", html, re.IGNORECASE)
        body = html.toc_html + html
        title = _("Conversion (%s)") % time.strftime("%X %x")
        if useTemplateHTML:
            body = template_HTML.format(title=title, body=body)
        f = open(fp, "w")
        f.write(body.encode("UTF-8"))
        f.close()
        os.startfile(fp)
    else:
        ui.browseableMessage(
            html.toc_html + html,
            _("Preview of MarkDown or HTML"),
            True
        )


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    scriptCategory = _("Markdown Forever")

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
        "kb:nvda+alt+k": "showViaNVDA",
        "kb:nvda+alt+l": "showInBrowser"
    }
