# NVDA-MarkdownForever
A small NVDA add-on that converts Markdown or HTML contents easily

* Authors: André-Abush Clause and contributors
* License: GNU General Public License, version 2
* Download [stable version][1]
* Download [development version][2]
* GitHub repository: [andre9642/NVDA-markdownForever][3]

## Commands
- *NVDA+ALT+,*: interactive mode.
- *NVDA+ALT+b*: Markdown to HTML conversion. The result is displayed in your default browser.
- *NVDA+ALT+n*: Markdown to HTML conversion. The result is displayed in a virtual buffer of NVDA.
- *NVDA+ALT+k*: HTML to markdown conversion. The result is displayed in a virtual buffer of NVDA.
- *NVDA+ALT+l*: Markdown to HTML source conversion. The result is displayed in a virtual buffer of NVDA.
- *NVDA+SHIFT+h*: copy the HTML generated to the clipboard from a Markdown content. One press: copy as *plain text* (HTML source). Two quick presses: copy as *formatted HTML*.

### Notes

* The *formatted HTML* can be pasted in applications like Microsoft Word, Wordpad, Thunderbird, some rich-text field in web page, etc.. 
  However it can't be pasted in text editor such as Notepad, Notepad++, etc..
* You can remap these gestures in the input gestures configuration, under _MarkDown Forever_ section.
* It is recommended to favor the display in browser instead of the virtual buffer of NVDA.
  Some tags such as `<details>` are not supported by the render of virtual buffer.

## Included dependencies
- *markdown2*: <https://github.com/trentm/python-markdown2>
- *html2markdown*: <https://github.com/dlon/html2markdown>
- *html2text*: <https://pypi.org/project/html2text/>
- *PyYAML*: <https://pypi.org/project/PyYAML/>

[1]: https://andreabc.net/projects/NVDA_addons/MarkdownForever/latest
[2]: https://andreabc.net/projects/NVDA_addons/MarkdownForever/latest?channel=dev
[3]: https://github.com/Andre9642/nvda-markdownForever
