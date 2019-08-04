# nvda-markdownForever
A small NVDA add-on that provides preview of MarkDown or HTML contents in 
any textarea. Also, you can select text to convert.

* Authors: André-Abush Clause and contributors
* License: GNU General Public License, version 2
* Download [stable version][1]

## Commands
- *NVDA+ALT+b*: Markdown to HTML conversion. The result is displayed in your default browser.
- *NVDA+ALT+n*: Markdown to HTML conversion. The result is displayed in a virtual buffer of NVDA.
- *NVDA+ALT+k*: HTML to markdown conversion
- *NVDA+ALT+l*: Show the HTML source from Markdown.
- *NVDA+SHIFT+h*: Copy the result to the clipboard from Markdown. One press: copy the HTML source. Two quick presses: copy the formatted HTML.

*Note*: you can remap these gestures in the input gestures configuration,
        under _MarkDown Forever_ section.

## Included dependencies
- *markdown2*: <https://github.com/trentm/python-markdown2>
* *html2markdown*: <https://pypi.org/project/html2markdown/>
- *HtmlClipboard*: <http://code.activestate.com/recipes/474121-getting-html-from-the-windows-clipboard/>

[1]: https://andreabc.net/projects/NVDA_addons/MarkdownForever/latest
