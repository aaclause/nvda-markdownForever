# nvda-markdownForever
A small NVDA add-on that provides preview of MarkDown or HTML contents in 
any textarea

* Authors: André-Abush Clause and contributors
* License: GNU General Public License, version 2
* Download [stable version][1]

## Usage
In any textarea, press:

- *NVDA+ALT+k* for preview of MarkDown or HTML trough _NVDA_.
- *NVDA+ALT+l* for preview of MarkDown or HTML trough _your default browser_.

Also, you can select text to convert.

*Notes*:

- you can remap these gestures in the input gestures configuration,
  under -- MarkDown Forever -- section.
- the *preview in browser* is better than the *preview trough NVDA* in
  some cases. Indeed, the preview trough NVDA uses *an old version of
  Internet Explorer*. For this reason, some tags such as `<details>`
  are not supported.

## Included dependencies
- *markdown2*: <https://github.com/trentm/python-markdown2>
- *HtmlClipboard*: <http://code.activestate.com/recipes/474121-getting-html-from-the-windows-clipboard/>

[1]: https://andreabc.net/projects/NVDA_addons/MarkdownForever/latest
