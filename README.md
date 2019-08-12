# nvda-markdownForever
A small NVDA add-on that converts MarkDown or HTML contents easily

* Authors: André-Abush Clause and contributors
* License: GNU General Public License, version 2
* Download [stable version][1]

## Commands
- *NVDA+ALT+b*: Markdown to HTML conversion. The result is displayed in your default browser.
- *NVDA+ALT+n*: Markdown to HTML conversion. The result is displayed in a virtual buffer of NVDA.
- *NVDA+ALT+k*: HTML to markdown conversion
- *NVDA+ALT+l*: MarkDown to HTML source conversion. The result is displayed in a virtual buffer of NVDA.
- *NVDA+SHIFT+h*: copy the HTML generated to the clipboard from a Markdown content. One press: copy as *plain text* (HTML source). Two quick presses: copy as *formatted HTML*.

*Notes*:
* The *formatted HTML* can be pasted in applications like Microsoft Word, Wordpad, Thunderbird, some rich-text field in web page, etc.. However it can't be pasted in text editor such as Notepad, Notepad++, etc..
* You can remap these gestures in the input gestures configuration, under _MarkDown Forever_ section.
* You should favor the display in browser instead of the virtual  buffer of NVDA. Some tags such as `<details>` are not supported by the render of virtual buffer.

## Included dependencies
- *markdown2*: <https://github.com/trentm/python-markdown2>
- *html2markdown*: <https://pypi.org/project/html2markdown/>

[1]: https://andreabc.net/projects/NVDA_addons/MarkdownForever/latest
