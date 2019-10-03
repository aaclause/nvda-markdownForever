# coding: UTF-8
# winClipboard
# A small module for Windows that copies to clipboard as formatted HTML or plaint text
# Author: André-Abush Clause <dev@andreabc.net>
# Version: 2019-10-03

# Main references:
# - Clipboard: https://docs.microsoft.com/en-us/windows/win32/dataxchg/clipboard
# - HTML Clipboard Format: https://docs.microsoft.com/en-us/windows/win32/dataxchg/html-clipboard-format
# - How To Add HTML Code to the Clipboard by Using Visual C++: https://support.microsoft.com/en-us/help/274308/how-to-add-html-code-to-the-clipboard-by-using-visual-c

import sys
import ctypes
import ctypes.wintypes
import string

isPy3 = True if sys.version_info >= (3, 0) else False

# BOOL OpenClipboard(HWND hWndNewOwner);
OpenClipboard = ctypes.windll.user32.OpenClipboard
OpenClipboard.argtypes = (ctypes.wintypes.HANDLE,)
OpenClipboard.restype = ctypes.wintypes.BOOL

# BOOL EmptyClipboard();
EmptyClipboard = ctypes.windll.user32.EmptyClipboard
EmptyClipboard.restype = ctypes.wintypes.BOOL

# UINT EnumClipboardFormats(UINT format);
EnumClipboardFormats = ctypes.windll.user32.EnumClipboardFormats
EnumClipboardFormats.argtypes = (ctypes.wintypes.UINT,)
EnumClipboardFormats.restype = ctypes.wintypes.UINT

# HANDLE GetClipboardData(UINT uFormat);
GetClipboardData = ctypes.windll.user32.GetClipboardData
GetClipboardData.argtypes = (ctypes.wintypes.UINT,)
GetClipboardData.restype = ctypes.wintypes.HANDLE

# UINT RegisterClipboardFormatW(LPCWSTR lpszFormat);
RegisterClipboardFormat = ctypes.windll.user32.RegisterClipboardFormatW
RegisterClipboardFormat.argtypes = (ctypes.wintypes.LPWSTR,)
RegisterClipboardFormat.restype = ctypes.wintypes.UINT

# HANDLE SetClipboardData(UINT uFormat, HANDLE hMem);
SetClipboardData = ctypes.windll.user32.SetClipboardData
SetClipboardData.argtypes = ctypes.wintypes.UINT, ctypes.wintypes.HANDLE
SetClipboardData.restype = ctypes.wintypes.HANDLE

# BOOL CloseClipboard();
CloseClipboard = ctypes.windll.user32.CloseClipboard
CloseClipboard.restype = ctypes.wintypes.BOOL

# DECLSPEC_ALLOCATOR HGLOBAL GlobalAlloc(UINT	uFlags,SIZE_T dwBytes);
GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
GlobalAlloc.argtypes = ctypes.wintypes.UINT, ctypes.c_ssize_t
GlobalAlloc.restype = ctypes.wintypes.HANDLE

# LPVOID GlobalLock(HGLOBAL hMem);
GlobalLock = ctypes.windll.kernel32.GlobalLock
GlobalLock.argtypes = ctypes.wintypes.HGLOBAL,
GlobalLock.restype = ctypes.wintypes.LPVOID

# BOOL GlobalUnlock(HGLOBAL hMem);
GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
GlobalUnlock.argtypes = ctypes.wintypes.HGLOBAL,
GlobalUnlock.restype = ctypes.wintypes.BOOL

# SIZE_T GlobalSize(HGLOBAL hMem);
GlobalSize = ctypes.windll.kernel32.GlobalSize
GlobalSize.argtypes = ctypes.wintypes.HGLOBAL,
GlobalSize.restype = ctypes.c_size_t

# void *memmove(void *dest, const void *src, size_t count);
memmove = ctypes.memmove
memmove.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)
memmove.restype = ctypes.c_void_p

CF_UNICODETEXT = 13
CF_HTML = RegisterClipboardFormat("HTML Format")
formats = [CF_UNICODETEXT,	CF_HTML]
WCHAR_ENCODING = "utf_16_le"
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040

unicode_type = type(u'')

HTMLHeadersClip = (
	"Version:0.9\r\n"
	"StartHTML:{StartHT}\r\n"
	"EndHTML:{EndHTML}\r\n"
	"StartFragment:{StartFr}\r\n"
	"EndFragment:{EndFrag}\r\n"
)
StartFragment = "<!--StartFragment-->"
EndFragment = "<!--EndFragment-->"
HTMLTemplate = (
	"<!DOCTYPE html>\r\n"
	"<html>\r\n"
	"<head>\r\n"
	"<title>HTML Document</title>\r\n"
	"<meta charset=\"UTF-8\" />\r\n"
	"</head>\r\n"
	"<body>\r\n"
	+StartFragment+
	"{BodyHTML}"
	+EndFragment+
	"</body>\r\n"
	"</html>"
)

def get(format=CF_UNICODETEXT, html=False):
	if format==CF_UNICODETEXT and html: format = CF_HTML
	data = None
	if not OpenClipboard(None): raise WinError()
	handle = GetClipboardData(format)
	hData = GlobalLock(handle)
	size = GlobalSize(handle)
	if hData and size:
		raw_data = ctypes.create_string_buffer(size)
		memmove(raw_data, hData, size)
		if format == CF_HTML:
			if isPy3: data = raw_data.raw.decode().rstrip(u'\0')
			else: data = raw_data.raw.decode("UTF-8").rstrip(u'\0')
			startPos = data.index(StartFragment)+len(StartFragment)
			endPos = data.rfind(EndFragment)
			data = data[startPos:endPos]
		else:
			if isPy3: data = raw_data.raw.decode(WCHAR_ENCODING, errors="surrogatepass").rstrip(u'\0')
			else: data = raw_data.raw.decode(WCHAR_ENCODING).rstrip(u'\0').encode("UTF-8")
	GlobalUnlock(handle)
	CloseClipboard()
	return data

def copy(data, format=CF_UNICODETEXT, html=False):
	if format==CF_UNICODETEXT and html: format = CF_HTML
	if format not in formats: raise ValueError("Format %s not supported" % format)
	if not isinstance(data, unicode_type): s = data.decode("UTF-8")
	if format == CF_HTML:
		if not isPy3: data = data.encode("UTF-8")
		data = HTMLHeadersClip+HTMLTemplate.replace("{BodyHTML}", data)
		data = data.replace("{StartHT}", "%.9d" % data.index("<!DOCTYPE html>"))
		data = data.replace("{EndHTML}", "%.9d" % len(data))
		data = data.replace("{StartFr}", "%.9d" % data.index(StartFragment))
		data = data.replace("{EndFrag}", "%.9d" % data.index(EndFragment))
		data = data.encode() if isPy3 else bytes(data)
		bufLen = len(data)
	elif format == CF_UNICODETEXT:
		if isPy3: bufLen = len(data.encode(WCHAR_ENCODING, errors="surrogatepass"))+2
		else:
			try: data = data.encode(WCHAR_ENCODING, errors="surrogatepass")
			except UnicodeDecodeError: data = data.decode("UTF-8").encode(WCHAR_ENCODING, errors="surrogatepass")
			bufLen = len(data)+2
	if not OpenClipboard(None): raise WinError()
	if not EmptyClipboard(): raise WinError()
	# Allocate global memory
	hData = GlobalAlloc(GMEM_MOVEABLE|GMEM_ZEROINIT, bufLen)
	# Acquire a lock to the global memory receiving a local memory address
	ptr = GlobalLock(hData)
	if not memmove(ptr, data, bufLen): raise WinError()
	GlobalUnlock(hData)
	if not SetClipboardData(format, hData): raise WinError()
	CloseClipboard()
