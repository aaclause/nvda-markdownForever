# coding: UTF-8
import gui, wx
import random
import addonHandler
addonHandler.initTranslation()

from .common import *
from . import HTTPServer

class GeneralDlg(gui.settingsDialogs.SettingsPanel):
	title = _("General")

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		tableOfContentsText = _("&Generate a table of contents")
		markdownEngine = config.conf["markdownForever"]["markdownEngine"]
		self.tableOfContentsCheckBox = sHelper.addItem(wx.CheckBox(self, label=tableOfContentsText))
		self.tableOfContentsCheckBox.SetValue(config.conf["markdownForever"]["toc"])

		numberHeadingsText = _("Try to automatically &number headings")
		self.numberHeadingsCheckBox = sHelper.addItem(wx.CheckBox(self, label=numberHeadingsText))
		self.numberHeadingsCheckBox.SetValue(config.conf["markdownForever"]["autonumber-headings"])

		extratagsText = _("Enable e&xtra tags")
		self.extratagsCheckBox = sHelper.addItem(wx.CheckBox(self, label=extratagsText))
		self.extratagsCheckBox.SetValue(config.conf["markdownForever"]["extratags"])

		genMetadataText = _("Generate corresponding &metadata from HTML source")
		self.genMetadataCheckBox = sHelper.addItem(wx.CheckBox(self, label=genMetadataText))
		self.genMetadataCheckBox.SetValue(config.conf["markdownForever"]["genMetadata"])

		defaultActionIMText = _("Default action in interactive mode")
		self.defaultActionListBox = sHelper.addLabeledControl(defaultActionIMText, wx.Choice, choices=IM_actionLabels)
		self.defaultActionListBox.SetSelection(list(IM_actions.values()).index(config.conf["markdownForever"]["IM_defaultAction"]))
		idEngine = markdownEngines.index(markdownEngine)
		markdownEngineText = _("Markdown Engine")
		self.markdownEngineListBox = sHelper.addLabeledControl(markdownEngineText, wx.Choice, choices=markdownEngineLabels)
		self.markdownEngineListBox.SetSelection(idEngine)
		self.markdown2Extras = label = _("Preferred &input tables")
		label = _("Markdo&wn2 extras")
		choices = [f"{k}: {v}" for k, v in EXTRAS.items()]
		self.markdown2Extras = sHelper.addLabeledControl(label, gui.nvdaControls.CustomCheckListBox, choices=choices)
		self.markdown2Extras.CheckedItems = getMarkdown2Extras(True)
		self.markdown2Extras.Select(0)
		self.defaultPath = sHelper.addLabeledControl(_("Path"), wx.TextCtrl, value=config.conf["markdownForever"]["defaultPath"])

	def onManageHTMLTemplates(self, evt):
		manageHTMLTemplatesDialog = ManageHTMLTemplatesDlg(self)
		if manageHTMLTemplatesDialog.ShowModal() == wx.ID_OK:
			self.manageHTMLTemplatesBtn.SetFocus()

	def onSave(self):
		defaultPath = self.defaultPath.GetValue()
		if not os.path.exists(realpath(defaultPath)): return self.defaultPath.SetFocus()
		config.conf["markdownForever"]["toc"] = self.tableOfContentsCheckBox.IsChecked()
		config.conf["markdownForever"]["autonumber-headings"] = self.numberHeadingsCheckBox.IsChecked()
		config.conf["markdownForever"]["extratags"] = self.extratagsCheckBox.IsChecked()
		config.conf["markdownForever"]["genMetadata"] = self.genMetadataCheckBox.IsChecked()
		config.conf["markdownForever"]["IM_defaultAction"] = list(IM_actions.values())[self.defaultActionListBox.GetSelection()]
		config.conf["markdownForever"]["markdownEngine"] = markdownEngines[self.markdownEngineListBox.GetSelection()]
		if defaultPath: config.conf["markdownForever"]["defaultPath"] = defaultPath
		config.conf["markdownForever"]["markdown2Extras"] = ','.join(getMarkdown2ExtrasFromIndexes(self.markdown2Extras.CheckedItems))

class ManageHTMLTemplatesDlg(gui.settingsDialogs.SettingsPanel):

	title = _("HTML Templates")

	def makeSettings(self, settingsSizer):
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)

		HTMLTemplatesText = _("HTML templates &list")
		self.HTMLTemplatesListBox = sHelper.addLabeledControl(HTMLTemplatesText, wx.Choice, choices=getHTMLTemplates())
		self.HTMLTemplatesListBox.SetSelection(getDefaultHTMLTemplateID())
		self.HTMLTemplatesListBox.Bind(wx.EVT_CHOICE, self.onHTMLTemplatesListBox)

		self.defaultTemplateBtn = bHelper.addButton(self, label="%s..." % _("Set as &default template"))
		self.defaultTemplateBtn.Bind(wx.EVT_BUTTON, self.onSetDefaultTemplateBtn)
		bHelper.addButton(parent=self, label="%s..." % _("&Edit")).Bind(wx.EVT_BUTTON, self.onEditClick)
		bHelper.addButton(parent=self, label="%s..." % _("&Add")).Bind(wx.EVT_BUTTON, self.onAddClick)
		self.removeBtn = bHelper.addButton(parent=self, label=_("&Remove"))
		self.removeBtn.Bind(wx.EVT_BUTTON, self.onRemoveClick)
		self.onHTMLTemplatesListBox()

		sHelper.addItem(bHelper)

	def refreshTemplatesList(self, name=None):
		self.HTMLTemplatesListBox.Set(getHTMLTemplates())
		self.HTMLTemplatesListBox.SetSelection(getDefaultHTMLTemplateID(name))

	def onHTMLTemplatesListBox(self, evt=None):
		templateID = self.HTMLTemplatesListBox.GetSelection()
		HTMLTemplate = getHTMLTemplateFromID(templateID)
		if templateID in [0, 1]: self.removeBtn.Disable()
		else: self.removeBtn.Enable()
		if HTMLTemplate != config.conf["markdownForever"]["HTMLTemplate"]:
			self.defaultTemplateBtn.Enable()
		else: self.defaultTemplateBtn.Disable()

	def onSetDefaultTemplateBtn(self, evt=None):
		templateID = self.HTMLTemplatesListBox.GetSelection()
		HTMLTemplate = getHTMLTemplateFromID(templateID)
		config.conf["markdownForever"]["HTMLTemplate"] = HTMLTemplate
		self.onHTMLTemplatesListBox()
		self.HTMLTemplatesListBox.SetFocus()

	def onEditClick(self, gesture):
		editIndex = self.HTMLTemplatesListBox.GetSelection()
		if editIndex < 0: return
		entryDialog = TemplateEntryDlg(self)
		templateName = getHTMLTemplates()[editIndex]
		entryDialog.templateName.SetValue(templateName if editIndex else "default")
		templateEntry = getHTMLTemplate(templateName if editIndex else "default")
		entryDialog.templateDescription.SetValue(templateEntry["description"])
		entryDialog.templateContent.SetValue(templateEntry["content"])
		if entryDialog.ShowModal() == wx.ID_OK:
			templateName = entryDialog.templateEntry["name"]
			templateDescription = entryDialog.templateEntry["description"]
			fp = "%s/%s.tpl" % (configDir, templateName)
			config.conf["markdownForever"]["HTMLTemplates"][templateName] = templateDescription
			with open(fp, "w") as writeFile:
				json.dump(entryDialog.templateEntry, writeFile, indent=4)
			self.refreshTemplatesList(templateName)
		entryDialog.Destroy()

	def onRemoveClick(self, gesture):
		removeIndex = self.HTMLTemplatesListBox.GetSelection()
		if removeIndex < 1: return
		templateName = getHTMLTemplates()[removeIndex]
		choice = gui.messageBox(_("Are you sure to want to delete the '%s' template?") % templateName, '%s – %s' % (addonSummary, _("Confirmation")), wx.YES_NO|wx.ICON_QUESTION)
		if choice == wx.NO: return
		if config.conf["markdownForever"]["HTMLTemplate"] == templateName:
			config.conf["markdownForever"]["HTMLTemplate"] = "default"
		config.conf["markdownForever"]["HTMLTemplates"] = {k: v for k, v in config.conf["markdownForever"]["HTMLTemplates"].copy().items() if k != templateName}
		fp = "%s/%s.tpl" % (configDir, templateName)
		if os.path.exists(fp): os.remove(fp)
		self.refreshTemplatesList()
		self.HTMLTemplatesListBox.SetSelection(removeIndex-1)
		self.HTMLTemplatesListBox.SetFocus()

	def onAddClick(self, gesture):
		entryDialog = TemplateEntryDlg(self, title=_("Add template"))
		entryDialog.templateContent.SetValue(getHTMLTemplate("default")["content"])
		if entryDialog.ShowModal() == wx.ID_OK:
			templateName = entryDialog.templateEntry["name"]
			templateDescription = entryDialog.templateEntry["description"]
			fp = "%s/%s.tpl" % (configDir, templateName)
			config.conf["markdownForever"]["HTMLTemplates"][templateName] = templateDescription
			with open(fp, "w") as writeFile:
				json.dump(entryDialog.templateEntry, writeFile, indent=4)
			self.refreshTemplatesList(self.refreshTemplatesList(templateName))
		entryDialog.Destroy()

	def onSave(self):
		pass

class TemplateEntryDlg(wx.Dialog):
	# Translators: This is the label for the edit template entry dialog.
	def __init__(self, parent=None, title=_("Edit template")):
		super(TemplateEntryDlg, self).__init__(parent, title=title)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		templateNameText = _("&Name")
		self.templateName = sHelper.addLabeledControl(templateNameText, wx.TextCtrl)
		templateDescriptionText = _("&Description")
		self.templateDescription = sHelper.addLabeledControl(templateDescriptionText, wx.TextCtrl, style=wx.TE_MULTILINE, size=(700, -1))
		templateContentText = _("&Content")
		self.templateContent = sHelper.addLabeledControl(templateContentText, wx.TextCtrl, style=wx.TE_MULTILINE, size=(700, -1))
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK|wx.CANCEL))
		mainSizer.Add(sHelper.sizer,border=20,flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.Bind(wx.EVT_BUTTON,self.onOk,id=wx.ID_OK)
		self.templateName.SetFocus()

	def onOk(self, evt):
		templateName = self.templateName.GetValue()
		templateDescription = self.templateDescription.GetValue()
		templateContent = self.templateContent.GetValue()
		pattern = "^[a-z0-9_-]{%d,%d}$" % (minCharTemplateName, maxCharTemplateName)
		if templateName == "default" or not re.match(pattern, templateName):
			letters = "a-z"
			digits = "0-9"
			hyphen = '-'
			underscore = '_'
			msg = _(f"Wrong value for template name field. Field must contain only letters in lowercase ({letters}), digits ({digits}), hyphen ({hyphen}) or underscore ({underscore}). A maximum of {maxCharTemplateName} characters. The following name is not allowed: \"default\".")
			gui.messageBox(msg, addonSummary, wx.OK|wx.ICON_ERROR)
			self.templateName.SetFocus()
			return
		if not templateContent.strip():
			msg = _("Content field empty.")
			gui.messageBox(msg, addonSummary, wx.OK|wx.ICON_ERROR)
			self.templateContent.SetFocus()
			return

		mustPresent = ["lang", "head", "header", "body"]
		notPresent = [tag for tag in mustPresent if "{%s}" % tag not in templateContent]
		if notPresent:
			missingFields = ", ".join(mustPresent)
			eg = "{%s}" random.choice(mustPresent)
			msg = _(f"Content field invalid. The following required tags are missing: {missingFields}. Each tag must be surrounded by braces. E.g.: {eg}.")
			gui.messageBox(msg, addonSummary, wx.OK|wx.ICON_ERROR)
			self.templateContent.SetFocus()
			return
		self.templateEntry = {
			"name": templateName,
			"description": templateDescription,
			"content": templateContent
		}
		evt.Skip()

class WebServerDlg(gui.settingsDialogs.SettingsPanel):

	title = _("Web server")

	def makeSettings(self, settingsSizer):
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		self.host = sHelper.addLabeledControl(_("Host"), wx.TextCtrl, value=config.conf["markdownForever"]["HTTPServer"]["host"])
		self.port = sHelper.addLabeledControl(_("Port"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=1, max=65535, initial=int(config.conf["markdownForever"]["HTTPServer"]["port"]))
		self.defaultEncoding = sHelper.addLabeledControl(_("Default encoding"), wx.TextCtrl, value=config.conf["markdownForever"]["HTTPServer"]["defaultEncoding"])
		rootFoldersText = _("Root folders")
		self.rootFoldersListBox = sHelper.addLabeledControl(rootFoldersText, wx.Choice, choices=self.getRootFolders())
		HTTPServer.stop()

	def getRootFolders(self):
		out = []
		for k, v in config.conf["markdownForever"]["HTTPServer"]["rootDirs"].copy():
			out.append(v)
		return out

	def onSave(self):
		host = self.host.GetValue()
		port = self.port.GetValue()
		defaultEncoding = self.defaultEncoding.GetValue()
		if host: config.conf["markdownForever"]["HTTPServer"]["host"] = host
		if port: config.conf["markdownForever"]["HTTPServer"]["port"] = port
		if defaultEncoding: config.conf["markdownForever"]["HTTPServer"]["defaultEncoding"] = defaultEncoding

class AddonSettingsDialog(gui.settingsDialogs.MultiCategorySettingsDialog):
	categoryClasses=[
		GeneralDlg,
		ManageHTMLTemplatesDlg,
		WebServerDlg,
	]

	def __init__(self, parent, initialCategory=None):
		# Translators: title of add-on parameters dialog.
		dialogTitle = _("Settings")
		self.title = "%s - %s" % (addonSummary, dialogTitle)
		super(AddonSettingsDialog,self).__init__(parent, initialCategory)
