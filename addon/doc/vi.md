---
author:
- Sof &lt;<hellosof@gmail.com>&gt;
autonumber-headings: 1
css:
- style.css
date: Thứ ba, 19/05/2020
extratags: 1
extratags-back: 0
filename: doc_vi
include-after:
- '%addonDir%/doc/dependencies.md'
keywords: tài liệu, MarkdownForever, NVDA add-on, tiếng Việt
lang: vi
langd: vi
subtitle: Bộ chuyển đổi Markdown và HTML đầy đủ tính năng cho NVDA
template: default
title: Tài liệu hướng dẫn sử dụng MarkdownForever %addonVersion%
toc: 1
...

**Mục lục**
%toc%

## Giới thiệu

MarkdownForever là một add-on nhỏ cho NVDA, dùng để chuyển đổi nội dung Markdown hay HTML một cách dễ dàng. Chỉ việc viết hoặc cho hiển thị bất cứ nội dung nào ở định dạng Markdown hay HTML và bấm một phím tắt đơn giản để chuyển đổi hoặc xem trước kết quả một cách nhanh chóng bất cứ lúc nào, hoàn toàn đúng như khi nó hiển thị trên trang web của bạn, hay dạng mã nguồn HTML, sẵn sàng để dán ở bất cứ nơi nào có hỗ trợ HTML.

MarkdownForever có thể:

* Chuyển đổi Markdown qua HTML
* Chuyển đổi markdown qua mã nguồn HTML
* Chuyển đổi HTML qua Markdown
* Chuyển đổi Markdown qua định dạng HTML

## Nhưng Markdown là gì?

Theo Wikipedia,
> Markdown là một ngôn ngữ đánh dấu với cú pháp văn bản thô, được thiết kế để có thể dễ dàng chuyển thành HTML và nhiều định dạng khác sử dụng một công cụ cùng tên. Nó thường được dùng để tạo các tập tin readme, viết tin nhắn trên các diễn đàn, và tạo văn bản có định dạng bằng một trình biên tập văn bản thô.

Bạn có thể tìm hiểu thêm về Markdown bằng cách đọc [bài viết đầy đủ trên Wikipedia.](https://vi.wikipedia.org/wiki/Markdown)

Như vậy, thay vì viết tài liệu web bằng HTML với nguy cơ bị lỗi, bạn sẽ dùng các thẻ dễ nhớ hơn và công việc của bạn sẽ hoàn thành nhanh chóng. Với Markdown, bạn sẽ làm được nhiều hoặc ít hơn những gì  HTML có thể làm: tiêu đề, danh sách có thứ tự (số đếm) hoặc không thứ tự (buleted), liên kết, thậm chí là bảng biểu.

Ví dụ, muốn làm tiêu đề cấp 1, bạn sẽ viết một dấu thăng (#), sau đó là tên của tiêu đề, có hoặc không có khoảng trắng giữa chúng:

> `#Đây là ví dụ về tiêu đề cấp 1`

sẽ hiển thị trong tài liệu HTML của bạn như sau:

> <h1>\!Đây là ví dụ về tiêu đề cấp 1</h1>

Với tiêu đề cấp 2, bạn sẽ dùng hai dấu thăng, ba dấu cho tiêu đề cấp 3, v...v...
 
Bây giờ, hãy làm một danh sách không thứ tự. để làm điều này, bạn có thể thêm dấu sao (*) vào trước mỗi thành phần trong danh sách. Xem ví dụ sau:

<blockquote>
```
* Cam
* Đường
* Sữa
```
</blockquote>

Sẽ hiển thị:

> * Cam
> * Đường
> * Sữa

Bạn cũng có thể tạo một liên kết bằng cách đặt tiêu đề của liên kết đó trong cặp dấu ngoặc vuông ([]). Sau đó, đặt đường dẫn liên kết trong cặp dấu ngoặc tròn và không có khoảng trắng. Ví dụ:

    [Bấm vào đây để mở trang web của  NVAccess](https://www.nvaccess.org)

sẽ cho ra:

[Bấm vào đây để mở trang web của  NVAccess](https://www.nvaccess.org)
 
Thậm chí, bạn có thể `*in nghiêng một đoạn văn bản*` bằng cách đặt nó trong hai dấu sao, hoặc `**in đậm văn bản**` bằng cách đặt nó vào hai cặp dấu sao... Còn nhiều cái khác nữa. Xem [Bài viết sau](https://www.markdownguide.org/cheat-sheet/) để biết thêm chi tiết.

## Chuyển đổi Markdown qua HTML

Tính năng này cho phép bạn chuyển nội dung markdown hiển thị trên màn hình thành HTML, hiển thị như cách mà nội dung  Markdown của bạn sẽ thể hiện ở tài liệu HTML. Đây có thể là một tài liệu được viết ở định dạng Markdown, một tập tin .md có sẵn trên ổ cứng hoặc một nội dung Markdown tìm thấy trên một trang web. Mặc định, MarkdownForever sẽ chuyển tất cả nội dung đang hiển thị, nhưng bạn cũng có thể chọn một đoạn nhất định để chuyển đổi.

Bạn có thể dùng các phím lệnh sau:

- *NVDA+ALT+b*: kết quả hiển thị như trang web trên trình duyệt web mặc định của bạn.
- *NVDA+ALT+n*: kết quả hiển thị như trang web  trên màn hình ảo của NVDA.

Xin lưu ý rằng lựa chọn hiển thị trên trình duyệt được khuyên dùng thay cho việc hiển thị trên màn hình ảo của NVDA. Một số thẻ, cụ thể là thẻ  HTML5 như `<details>,` chưa được hỗ trợ trên màn hình ảo.

## Chuyển đổi Markdown thành mã nguồn HtML

Tính năng này chuyển đổi nội dung Markdown thành ngôn ngữ HTML thuần túy. Khi hoàn tất, bạn có thể chép và dán vào tập tin HTML, vào bài viết trên diễn đàn, hoặc mỗi vùng nhập liệu trên web có hỗ trợ mã HTML.

Sử dụng các phím lệnh sau:

- *NVDA+ALT+l*: kết quả hiển thị trên màn hình ảo của NVDA.
- *NVDA+Ctrl+h*: Chép mã nguồn HTML vào bộ nhớ tạm.

## Chuyển đổi HTML qua Markdown

Tính năng này nỗ lực tạo ra một văn bản Markdown từ nguồn nội dung HTML. Thông thường, nó xử lý toàn bộ nội dung hiển thị trên màn hình hoặc một đoạn nào đó được chọn. Sử dụng các phím lệnh sau:

- *NVDA+Alt+k*: hiển thị kết quả trên màn hình ảo của NVDA.
- *NVDA+Shift+g*: chép kết quả vào bộ nhớ tạm.

Bạn cũng có thể chuyển đổi một trang  HTML thành Markdown bằng cách đơn giản là chọn đường dẫn của nó. Tuy nhiên, bạn phải chắc chắn là bộ chuyển đổi HTML2Text phải được chọn làm mặc định trong [Cài đặt của MarkdownForever,](#markdownforevers-default-settings) trong phần tùy chỉnh của NVDA.
 
## Chuyển đổi Markdown thành định dạng HtML

Chức năng này chuyển đổi nội dung Markdown của bạn thành định dạng HTML và chép nó vào bộ nhớ tạm. Định dạng HTML sẽ giống như mọi trang web hiển thị trên trình duyệt của bạn, với các liên kết có thể click, tiêu đề, v...v... Điều này chỉ có thể thực hiện được từ nội dung Markdown chứ không làm được với mã nguồn HTML. Để làm điều này, bấm NVDA+Shift+h.

Lưu ý rằng *định dạng HTML* có thể dán vào các ứng dụng như Microsoft Word, Wordpad, Thunderbird, vài ô nhập liệu trên web page, v...v... Tuy nhiên, không thể dán nó vào các trình soạn thảo như Notepad, Notepad++, v...v...

## Chế độ tương tác

Chế độ tương tác là một chức năng dùng để trình bày tất cả tính năng của MarkdownForever trong một hộp thoại, cung cấp cho bạn các tính năng bổ sung tiện lợi hơn. Để mở chế độ này, bấm NVDA+CTRL+i.
Sau đây là mô tả màn hình của tính năng, căn cứ theo cách duyệt bằng Tab:

* "Chuyển đổi qua": hộp xổ đầu tiên này cho phép bạn chọn cách chuyển đổi: HTML, Mã nguồn HTML hoặc Markdown. Dùng các phím mũi tên lên xuống để chọn.
* "Tạo mục lục": Hộp kiểm này sẽ cho phép bạn chọn tạo hay không tạo mục lục của các chương trong tài liệu  HTML của bạn với liên kết có thể click để đi đến chương đó. Trạng thái của tùy chọn này cũng có thể thiết lập mặc định trong [Cài đặt MarkdownForever.](#markdownforevers-default-settings)
* "Nỗ lực đánh số tự động cho tiêu đề": nếu chọn, Markdown Forever sẽ nỗ lực thêm số vào trước mỗi tiêu đề (hay chương), tùy theo cấp độ của mỗi tiêu đề. Ví dụ: "1." cho tiêu đề cấp 1, "1.1." cho tiêu đề cấp 2, v...v... 
* "Bật các thẻ bổ sung": Nếu chọn, sẽ cho phép sử dụng [các thẻ đặc biệt](#extra-tags) trong nội dung Markdown của bạn để tự chèn những thứ như ngày giờ hiện tại. Trạng thái của tùy chọn này cũng có thể thiết lập mặc định trong [Cài đặt MarkdownForever.](#markdownforevers-default-settings)
* "Cho phép dịch ngược các thẻ bổ sung": tùy chọn này sẽ thể hiện có hay không việc [các thẻ bổ sung](#extra-tags) sẽ được trả lại nguyễn mẫu của nó (ví dụ: %date%) khi chuyển đổi nội dung HTML được tạo bởi Markdown Forever trở về Markdown. 
* "Tên": bạn có thể điền	 tên cho tài liệu HTML của bạn ở đây, và nó sẽ hiển thị trên trình duyệt.
* "Khối siêu dữ liệu tương ứng": ô có thuộc tính chỉ đọc này hiển thị 
* "Tạo siêu dữ liệu tương ứng từ mã nguồn HTML": khi chuyển đổi một  tập tin mã nguồn HTML qua Markdown, nó nỗ lực đoán siêu dữ liệu từ mã nguồn (title - tên, lang - ngôn ngữ, filename -tên tập tin, v...v...) và tạo ra [khối siêu dữ liệu](#optionnal-metadata-block) cho bạn. Tùy chọn này chỉ có khi chuyển đổi HTML thành Markdown.
* "Hiển thị trên màn hình ảo": nút này sẽ hiện nội dugn đã chuyển đổi của bạn trên màn hình ảo của NVDA.
* "Hiển thị trên trình duyệt": hiển thị nội dung đã chuyển đổi của bạn trên trình duyệt mặc định.
* "Chép vào bộ nhớ tạm": chép nội dung đã chuyển đổi của bạn vào bộ nhớ tạm của Windows, sẵn sàng để dán.
* "Lưu kết quả": sẽ yêu cầu bạn lưu tài liệu đã chuyển đổi vào ổ cứng thông qua một hộp thoại lưu tiêu chuẩn của Windows. Bạn cũng có thể thiết lập nơi lưu mặc định trong [Cài đặt MarkdownForever.](#markdownforevers-default-settings)

## Tùy chọn khối siêu dữ liệu

Khối siêu dữ liệu cho phép bạn thiết lập vài tham số nhất định cho một tài liệu cụ thể, độc lập với [các thiết lập mặc định.](#markdownforevers-default-settings) Chúng phải được đặt ở đầu tài liệu và phải bắt đầu với ba dấu trừ ("---") và kết thúc với ba dấu chấm ("...") hoặc ba dấu trừ ("---"). Mỗi thành phần phải được nhập theo mẫu: khóa: "giá trị" (giá trị phải được đặt trong dấu ngoặc kép). Phải đặt một dòng trắng tiếp sau khối siêu dữ liệu.

### Danh sách siêu dữ liệu được hỗ trợ

* author (hoặc authors): ghi ra tên của một hay nhiều tác giả cho tài liệu (xem ví dụ bên dưới). Thông tin này sẽ được thêm vào phần đầu của tập tin HTML. Khóa này không phân biệt chữ hoa / thường.
* autonumber-headings: xác định có hay không có việc tự đánh số cho tiêu đề. Có các giá trị: true (1) tức là có hoặc false (0) tức là không.
* css (hoặc CSS): chỉ ra một hoặc nhiều  tập tin CSS để  trình bày tài liệu của bạn (xem ví dụ bên dưới). Khóa này không phân biệt chữ hoa / thường.
* date: ghi ra ngày tháng cho tài liệu của bạn. Thông tin này sẽ được thêm vào phần đầu của tập tin HTML.
* extratags: chỉ định có hay không việc thông dịch [các thẻ bổ sung](#extra-tags). Có các giá trị: true (1) tức là có hoặc false (0) tức là không.
* extratags-back: xác định có hay không việc dịch ngược  [các thẻ bổ sung](#extra-tags) về nguyên mẫu của nó (ví dụ: %date%) khi chuyển đổi một nội dung HTML được tạo bởi Markdown Forever về Markdown. Có các giá trị: true (1) tức là có hoặc false (0) tức là không.
* filename: quy định tên của tập tin khi lưu lại.
* keywords: quy định các từ khóa liên quan đến những chủ đề được nói đến trong tài liệu của bạn.
* lang: quy định ngôn ngữ chính cho tài liệu. Nếu cần, hãy dùng các thẻ span/div với thuộc tính lang để xác định các thay đổi ngôn ngữ, ngay bên trong tài liệu.
* mathjax: xác định có hay không việc  chuyển đổi các công thức toán viết bằng [LaTeX](https://en.wikipedia.org/wiki/LaTeX). Có các giá trị: true (1) tức là có hoặc false (0) tức là không. Yêu cầu có kết nối mạng và bạn phải mở kết quả được chuyển đội trên trình duyệt để hiển thị nó một cách chính xác, vì nội dung LaTeX đã thông dịch không thể xuất ra màn hình ảo của NVDA.
[Bấm vào đây để biết thêm thông tin về MathJax.](http://docs.mathjax.org/en/latest/)
* path: chỉ ra thư mục để lưu tài liệu. Có hỗ trợ các biến môi trường %userprofile%, %appdata% và %tmp%.
* subtitle:  ghi ra tên phụ cho tài liệu HtML của bạn. Thông tin này sẽ được thêm vào phần đầu của tập tin HTML.
* title: ghi ra tên của tài liệu HTML. Trong chế độ tương tác, ô tên sẽ được điền tự động bằng giá trị của khóa này.
* toc: xác định có hay không việc tạo mục lục. Có các giá trị: true (1) tức là có hoặc false (0) tức là không.

### Ví dụ về việc dùng siêu dữ liệu
<blockquote>
```
---
title: "Đặt một tên đơn giản"
date: 2019-11-08
subtitle: "Điền tên phụ cho tài liệu của bạn"
lang: vi
author:
- John Doe
- David Murphy
CSS:
- %userprofile%/document/main.css
- %userprofile%/document/custom.css
keywords: NVDA, Markdown, HTML
filename: test
path: "%userprofile%/desktop"
toc: 0
autonumber-headings: 1
mathjax: 0
---

Chào thế giới! <span lang="en"Hello world!</span> <span lang="fr">Bonjour le monde !</span> <span lang="es">¡Hola mundo!</span>
```
</blockquote>

Trong ví dụ ở trên, nội dugn sẽ được đọc thành tiếng của bốn ngôn ngữ, xem như bộ đọc bạn đang dùng có hỗ trợ tự chuyển ngôn ngữ và đã đánh dấu tùy chọn tương ứng trong cài đặt tiếng nói của  NVDA. Nó sẽ đọc như sau:

Chào thế giới! <span lang="en"Hello world!</span> <span lang="fr">Bonjour le monde !</span> <span lang="es">¡Hola mundo!</span>

## Các thẻ bổ sung

Thẻ bổ sung là những bộ giữ chỗ đặc biệt mà bạn có thể đặt vào nội dung Markdown của mình để tự thêm các thông tin hệ thống như ngày giờ hiện tại, sẽ được tạo ra ở dạng văn bản trong tài liệu HTML của bạn.

### Các thẻ bổ sung được hỗ trợ

| **In the Markdown content** | **Explanation** | **Result in the browser** |
| :----------: | :----------: | :----------: |
| `%date%` | Current date | %date% |
| `%time%` | Current time | %time% |
| `%now%` | Current date / time | %now% |
| `%day%` | Current day (long format) | %day% |
| `%dday%` | Current day (decimal format) | %dday% |
| `%month%` | Month (long format) | %month% |
| `%dmonth%` | Current month (decimal format) | %dmonth% |
| `%year%` | Current year (2 digits) | %year% |
| `%Year%` | Current year (4 digits) | %Year% |
| `%toc%` | Table of contents at cursor's position (if enabled through metadata or default settings) | N/A |

## MarkdownForever's default settings

They can be reached from the NVDA menu -> Settings MarkdownForever -> Settings and will let you configure and set as default various settings related to the conversion process already mentionned above:

* "Generate a table of contents": This checkbox will allow you to generate or not an index of the chapters of your final HTML document with clickable links leading to each chapter. This behavior can also be set on a per-document basis using the "toc" key within the [optional metadata block](#optional-metadata-block) and placed anywhere in the document using the corresponding [extra-tag.](#extra-tags)
* "Enable Extra Tags": If this is checked, it enables the possibility to use [special tags](#extra-tags) in your Markdown content to automatically insert things like the actual date or time. This behavior can also be set on a per-document basis using the extratags key within the [optional metadata block.](#optional-metadata-block)
* "Generate corresponding metadata for HTML source": When converting an HTML source file to Markdown, it attempts to guess the metadata from the source code (title, lang, filename etc) and generate the [metadata block](#optionnal-metadata-block) for you.
* "Default action in Interactive mode": This allows to choose the default action which will be performed when pressing the Enter key in [Interactive mode:](#interactive-mode) Show the generated content in your browser, in a virtual buffer or put it in the clipboard.
* "Markdown engine": MarkdownForever allows you to choose between tow conversion engines, [HTML2Text](https://pypi.org/project/html2text/) and [HTML2Markdown.](https://pypi.org/project/html2markdown/) Just experiment and choose the one you prefer, according to your needs or the produced result.
* "Markdown2 extras": see <https://github.com/trentm/python-markdown2/wiki/Extras>.
* "Path": Here you can set a default save location on your hard drive for your converted documents. it comes in handy if you always use the same folder to store all your work.
* "Manage HTML templates": This will open a dialog box allowing to add, edit and delete HTML templates. With templates, you will be able to customize visual aspects of your generated HTML documents using CSS (cascading styles sheets), the language responsible for page styling. This will let you change colors, layout or add images to your productions and build a template for every specific need. There are of course many tutorials to learn CSS available on the web and [this one](https://www.htmldog.com/guides/css/beginner/) can be a good starting point.

## Commands summary

- *NVDA+CTRL+i*: Interactive mode.
- *NVDA+ALT+b*: Markdown to HTML conversion. The result is displayed in your default browser.
- *NVDA+ALT+n*: Markdown to HTML conversion. The result is displayed in a virtual buffer of NVDA.
- *NVDA+ALT+k*: HTML to markdown conversion. The result is displayed in a virtual buffer of NVDA.
- *NVDA+ALT+l*: Markdown to HTML source conversion. The result is displayed in a virtual buffer of NVDA.
- *NVDA+SHIFT+g*: HTML to Markdown conversion. The result is copied to clipboard.
- *NVDA+SHIFT+h*: Markdown to formatted HTML conversion: The result is copied to the clipboard.
- *NVDA+CTRL+h*: Markdown to HTML source conversion. The result is copied to the clipboard.

## Add-on Information

* Authors:
	- André &lt;<dev@andreabc.net>&gt;: creator and main maintainer of the add-on.
	- Sof &lt;<hellosof@gmail.com>&gt;: English and French documentation, various suggestions.
	- Victor Cai: Chinese localization.
	- Çağrı Dogan: Turkish localization.
	- Rémy Ruiz &lt;<remyruiz@gmail.com>&gt;: Spanish localization.
	- And much more!
* License: GNU General Public License, version 2
* Download [stable version](https://andreabc.net/projects/NVDA_addons/markdownForever.nvda-addon)
* Download [development version](https://andreabc.net/projects/NVDA_addons/markdownForever.nvda-addon?channel=dev)
* GitHub repository: [andre9642/NVDA-markdownForever](https://github.com/Andre9642/nvda-markdownForever)
* **Included dependencies**: