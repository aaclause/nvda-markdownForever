# MarkdownForever: full-featured Markdown and HTML converter for NVDA

## Introduction

MarkdownForever is a small NVDA add-on that converts Markdown or HTML contents
easily. Just write or display any text in Markdown or HTML format and press a
simple shortcut to instantly convert or preview the result at any time,
exactly as it will look like in your final webpage, or in HTML source code,
ready to be pasted in any text area supporting HTML.

MarkdownForever can:

  * Convert Markdown to HTML
  * Convert markdown to HTML source code
  * Convert HTML to Markdown
  * Convert Markdown to formatted HTML

## But what on Earth this Markdown thing is?

According to Wikipedia,

> Markdown is a lightweight markup language with plain text formatting syntax.
> Its design allows it to be converted to many output formats, but the
> original tool by the same name only supports HTML. Markdown is often used to
> format readme files, for writing messages in online discussion forums, and
> to create rich text using a plain text editor.

You can learn more about Markdown by reading the [full article on
Wikipedia.](https://en.wikipedia.org/wiki/Markdown)

So, instead of writing your web documents using HTML with risk of making
mistakes, you will use easy to memorize tags and your work will be done in no
time. With Markdown, you will be able to do more or less the things HTML can
do: headings, ordered (numbered) or unordered (buleted) lists, links, and even
tables.

For example, if you want to make a first level heading, you will write one
hash sign (#), followed by the name of your heading, with or without a space
between them:

> `#This is an example of a first level heading`

which will appear as follow in your final HTML document:

> # \\!This is an example of a first level heading

For a second level heading, you will use Two hash signs, three for a third
level one, Etc.

Now, let's make an unordered list of items. To do so, you can prefix all items
of your list by an asterisk (*). Here is an example:

>     * Orange
>     * Sugar
>     * Milk
which will appear as:

>   * Orange
>   * Sugar
>   * Milk

You can also make a link by enclosing the title of the link in square brackets
([]), followed by the URL enclosed in parentheses without any spaces. For
example:

    
    
    [Click here to visit NVAccess's website](https://www.nvaccess.org)
    

which will give you:

[Click here to visit NVAccess's website](https://www.nvaccess.org)

You can even put `*some text in italic*` by enclosing it in asterisks, or
`**write text in bold**` by surrounding it with two asterisks... Possibilities
are numerous. Just check this [Markdown Cheat
Sheet](https://www.markdownguide.org/cheat-sheet/) for more tags and details.

## Converting Markdown to HTML

This feature allows you to convert any markdown text displayed on the screen
to HTML, showing you the way your Markdown will look in the final HTML
document. This can be a document you have written in Markdown format, a .md
file you already have on your hard drive or a Markdown text found on a web
page. By default, MarkdownForever converts all the currently displayed text,
but you can also select only a specific part to be converted.

You can use the following commands:

  * _NVDA+ALT+b_ : The result is displayed as web page in your default web browser.
  * _NVDA+ALT+n_ : The result is displayed as a web page in a virtual buffer of NVDA.

Please note that it is recommended to favor the display in browser instead of
the virtual buffer of NVDA. Some tags, particularly HTML5 tags such as
`<details>,` are not supported by the render of virtual buffer.

## Converting Markdown to HtML source code

This converts Markdown text to pure HTML language. Once done, you'll be able
to copy and paste it in an HTML file, in a forum post, or any text area on the
web where HTML code is supported.

The following commands are available:

  * _NVDA+ALT+l_ : The result is displayed in a virtual buffer of NVDA.
  * _NVDA+Ctrl+h_ : Copy the HTML source code to the clipboard.

## Converting HTML to Markdown

This feature attempts to produce a Markdown text from an HTML source content.
As usual, this works on the entire text displayed on the screen or on a
specificly selected part. The following commands are available:

  * _NVDA+Alt+k_ : Displays the result in a virtual buffer of NVDA.
  * _NVDA+Shift+g_ : Copy the result in the clipboard.

You can also convert an HTML web page to Markdown by simply selecting its URL.
However, you must first ensure that the HTML2Text conversion engine is
properly set as the default one in MarkdownForever's settings, located in the
Settings sub menu of NVDA.

## Converting Markdown to Formatted HtML

This function converts your Markdown content to formatted HTML and copy it to
the clipboard. Formatted HTML will look like any web page displayed by your
browser, with clickable links, headings etc. This can only be generated from a
Markdown content. It doesn't work with HTML source code. To perform this
action, press NVDA+Shift+h.

Please note that the _formatted HTML_ can be pasted in applications like
Microsoft Word, Wordpad, Thunderbird, some rich-text field in web page, etc.
However it can't be pasted in text editor such as Notepad, Notepad++, etc.

## Interactive Mode

The interactive mode is a function which presents all MarkdownForever's
features in a convenient dialog box, which offers you even more handy extras.
To open the Interactive Mode, Press NVDA+CTRL+i. Here is a description of the
screen in Tab order:

  * "Convert to": This first combo box allows you to choose the conversion direction: HTML, HTML source or Markdown. Use the up and down arrow keys to select.
  * "Generate a table of contents": This checkbox will allow you to generate or not an index of the chapters of your final HTML document with clickable links leading to each chapter. The status of this option can also be set as default in MarkdownForever settings.
  * "Enable Extra Tags": If this is checked, it enables the possibility to use special tags in your Markdown content to automatically insert things like the actual date or time. The status of this option can also be set as default in MarkdownForever settings.
  * "Title": You can input the title of your HTML document here, which will be visible in the internet browser.
  * "Generate corresponding metadata from HTML source": When converting an HTML source file to Markdown, it attempts to guess the metadata from the source code (title, lang, filename etc) and generate the metadata block for you. This option is only available for HTML to Markdown conversion.
  * "Show in Virtual Buffer": This button will open your converted content in a virtual buffer of NVDA.
  * "Show in Browser": This will display your converted content in your default internet browser.
  * "Copy to Clipboard": This will place your converted content in your Windows clipboard, ready to be pasted.
  * "Save As": This will prompt you to save your converted document on your hard drive through a standard Save As windows dialog box. A default Save location can also be set in MarkdownForever settings.

## Optional Metadata block

The metadata block allows you to set specific parameters for a particular
document, independent of the default settings. This must be placed at the very
beginning of the document and must begin with three dashes ("---") and end
with three periods ("...") or three dashes ("---"). Each entry must be
inputted in the following form: key: "value" (the value must be enclosed in
quotes). An empty line must be present after the metadata block.

### List of supported metadata

  * title: to indicate the title of the HTML document. In Interactive Mode, the title field will be automatically filled using the value of this key.
  * lang: to specify the main language of the document. If necessary, use span/div tags with the lang attribute to indicate language changes, internal to the document.
  * toc: to indicate whether or not a table of contents should be generated. Possible values: true (1) or false (0).
  * filename: to indicate the name of the output file when saving.
  * path: to specify the directory where the document should be generated. The environment variables %userprofile%, %appdata% and %tmp% are supported.
  * extratags: to specify whether or not extra-tags should be interpreted. Possible values: true (1) or false (0).

### Metadata usage example

>     ---
>     path: "%userprofile%/desktop"
>     filename: test
>     title: "a simple title"
>     toc: 0
>     lang: en
>     ---
>  
>     Hello World! <span lang="fr">Bonjour tout le monde!</span> <span lang="es">buenos días!</span>

In the example above, the text will be voiced in three languages, assuming
that the voice synthesizer you are using supports automatic language switching
and the corresponding checkbox is ticked in NVDA speech settings. It will
sound as follows:

> Hello World! Bonjour tout le monde! buenos días!

## Extra-tags

Extra-tags are special placeholders that you can put in your Markdown content
to automatically add system info like current date or time, which will be
rendered in clear text in your HTML document.

### Supported extra-tags

**In the Markdown content** | **Explanation** | **Result in the browser**  
---|---|---  
`%date%` | Current date | 05/11/2019  
`%time%` | Current time | 00:23:25  
`%now%` | Current date / time | 05/11/2019 00:23:25  
`%day%` | Current day (long format) | mardi  
`%dday%` | Current day (decimal format) | 05  
`%month%` | Month (long format) | novembre  
`%dmonth%` | Current month (decimal format) | 11  
`%year%` | Current year (2 digits) | 19  
`%Year%` | Current year (4 digits) | 2019  
`%toc%` | Table of contents at cursor's position (if enabled through metadata or default settings) | N/A  
  
## MarkdownForever's default settings

They can be reached from the NVDA menu -> Settings MarkdownForever -> Settings
and will let you configure and set as default various settings related to the
conversion process already mentionned above:

  * "Generate a table of contents": This checkbox will allow you to generate or not an index of the chapters of your final HTML document with clickable links leading to each chapter. This behavior can also be set on a per-document basis using the "toc" key within the optional metadata block and placed anywhere in the document using the corresponding extra-tag.
  * "Enable Extra Tags": If this is checked, it enables the possibility to use special tags in your Markdown content to automatically insert things like the actual date or time. This behavior can also be set on a per-document basis using the extratags key within the optional metadata block.
  * "Generate corresponding metadata for HTML source": When converting an HTML source file to Markdown, it attempts to guess the metadata from the source code (title, lang, filename etc) and generate the metadata block for you.
  * "Default action in Interactive mode": This allows to choose the default action which will be performed when pressing the Enter key in Interactive mode: Show the generated content in your browser, in a virtual buffer or put it in the clipboard.
  * "Markdown engine": MarkdownForever allows you to choose between tow conversion engines, [HTML2Text](https://pypi.org/project/html2text/) and [HTML2Markdown.](https://pypi.org/project/html2markdown/) Just experiment and choose the one you prefer, according to your needs or the produced result.
  * "Path": Here you can set a default save location on your hard drive for your converted documents. it comes in handy if you always use the same folder to store all your work.
  * " Manage HTML templates": This will open a dialog box allowing to add, edit and delete HTML templates. With templates, you will be able to customize visual aspects of your generated HTML documents using CSS (cascading styles sheets), the language responsible for page styling. This will let you change colors, layout or add images to your productions and build a template for every specific need. There are of course many tutorials to learn CSS available on the web and [this one](https://www.htmldog.com/guides/css/beginner/) can be a good starting point.

## Commands summary

  * _NVDA+CTRL+i_ : Interactive mode.
  * _NVDA+ALT+b_ : Markdown to HTML conversion. The result is displayed in your default browser.
  * _NVDA+ALT+n_ : Markdown to HTML conversion. The result is displayed in a virtual buffer of NVDA.
  * _NVDA+ALT+k_ : HTML to markdown conversion. The result is displayed in a virtual buffer of NVDA.
  * _NVDA+ALT+l_ : Markdown to HTML source conversion. The result is displayed in a virtual buffer of NVDA.
  * _NVDA+SHIFT+g_ : HTML to Markdown conversion. The result is copied to clipboard.
  * _NVDA+SHIFT+h_ : Markdown to formatted HTML conversion: The result is copied to the clipboard.
  * _NVDA+CTRL+h_ : Markdown to HTML source conversion. The result is copied to the clipboard.

## Add-on Information

  * Authors: André <[dev@andreabc.net](mailto:dev@andreabc.net)>, Sof <[hellosof@gmail.com](mailto:hellosof@gmail.com)> and other contributors
  * License: GNU General Public License, version 2
  * Download [stable version](https://andreabc.net/projects/NVDA_addons/markdownForever.nvda-addon)
  * Download [development version](https://andreabc.net/projects/NVDA_addons/markdownForever.nvda-addon?channel=dev)
  * GitHub repository: [andre9642/NVDA-markdownForever](https://github.com/Andre9642/nvda-markdownForever)
  * **Included dependencies** : 
    * [Markdown2](https://github.com/trentm/python-markdown2)
    * [HTML2Markdown](https://github.com/dlon/html2markdown)
    * [HTML2Text](https://pypi.org/project/html2text/)
    * [PyYAML](https://pypi.org/project/PyYAML/)
    * [WinClipboard](https://github.com/andre9642/python-winClipboard)