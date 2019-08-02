# nvda-markdownForever
A small NVDA add-on that provides preview of MarkDown or HTML contents in 
any textarea

* Authors: André-Abush Clause and contributors
* License: GNU General Public License, version 2
* Download [stable version][1]

## Usage
Gestures (in any textarea):

- *NVDA+ALT+k*: preview of MarkDown or HTML through _NVDA_.
- *NVDA+ALT+l*: preview of MarkDown or HTML through _your default browser_.
- *NVDA+ALT+j*: view *HTML source* from *Markdown* through _NVDA_.

Also, you can select text to convert.

*Notes*:

- you can remap these gestures in the input gestures configuration,
  under _MarkDown Forever_ section.
- the *preview in browser* is better than the *preview through NVDA* in
  some cases. Indeed, the preview through NVDA uses *an old version of
  Internet Explorer*. For this reason, some tags such as `<details>`
  are not supported.

## Included dependencies
- *markdown2*: <https://github.com/trentm/python-markdown2>

[1]: https://andreabc.net/projects/NVDA_addons/MarkdownForever/latest
