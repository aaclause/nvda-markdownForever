# -*- coding: UTF-8 -*-
import subprocess
import time

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.


# Since some strings in `addon_info` are translatable,
# we need to include them in the .po files.
# Gettext recognizes only strings given as parameters to the `_` function.
# To avoid initializing translations in this module we simply roll our own "fake" `_` function
# which returns whatever is given to it as an argument.
def _(arg):
	return arg


updateChannel = None
hashCommit = None
outBranchName = subprocess.check_output(
	["git", "branch", "--show-current"]).strip().decode()
out = subprocess.check_output(
	["git", "status", "--porcelain"]).strip().decode()
if not out.strip():
	label = subprocess.check_output(
		["git", "rev-parse", "--short", "HEAD"]).strip().decode()
	if label and len(label) == 7:
		hashCommit = label
if outBranchName.strip():
	updateChannel = "stable" if outBranchName in ["stable", "master"] else "dev"

# Add-on information variables
addon_info = {
	# for previously unpublished addons, please follow the community guidelines at:
	# https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
	# add-on Name, internal for nvda
	"addon_name" : "markdownForever",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown on installation and add-on information.
	"addon_summary" : _("Markdown Forever"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-ons manager
	"addon_description" : _("Full-featured Markdown and HTML converter for NVDA"),
	# version
	"addon_version": time.strftime("%y.%m.%d"),
	# Author(s)
	"addon_author" : "André <dev@andreabc.net>, Sof <hellosof@gmail.com> and other contributors",
	# URL for the add-on documentation support
	"addon_url": "https://andreabc.net/projects/NVDA_addons/markdownForever/",
	# URL for the add-on repository where the source code can be found
	"addon_sourceURL": "https://github.com/aaclause/nvda-markdownForever",
	# Documentation file name
	"addon_docFileName": None,
	# Minimum NVDA version supported (e.g. "2018.3.0", minor version is optional)
	"addon_minimumNVDAVersion": "2023.1",
	# Last NVDA version supported/tested (e.g. "2018.4.0", ideally more recent than minimum version)
	"addon_lastTestedNVDAVersion": "2024.1",
	# Add-on update channel (default is None, denoting stable releases,
	# and for development releases, use "dev".)
	# Do not change unless you know what you are doing!
	"addon_updateChannel": updateChannel,
	# Add-on license such as GPL 2
	"addon_license": "GPL v2",
	# URL for the license document the ad-on is licensed under
	"addon_licenseURL": "https://www.gnu.org/licenses/gpl-2.0.html",
}
if hashCommit:
	addon_info["addon_version"] += '-' + hashCommit

# Define the python files that are the sources of your add-on.
# You can either list every file (using ""/") as a path separator,
# or use glob expressions.
# For example to include all files with a ".py" extension from the "globalPlugins" dir of your add-on
# the list can be written as follows:
# pythonSources = ["addon/globalPlugins/*.py"]
# For more information on SCons Glob expressions please take a look at:
# https://scons.org/doc/production/HTML/scons-user/apd.html
pythonSources = ["addon/globalPlugins/markdownForever/*.py"]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []

# Base language for the NVDA add-on
# If your add-on is written in a language other than english, modify this variable.
# For example, set baseLanguage to "es" if your add-on is primarily written in spanish.
baseLanguage = "en"

# Markdown extensions for add-on documentation
# Most add-ons do not require additional Markdown extensions.
# If you need to add support for markup such as tables, fill out the below list.
# Extensions string must be of the form "markdown.extensions.extensionName"
# e.g. "markdown.extensions.tables" to add tables.
markdownExtensions = []
