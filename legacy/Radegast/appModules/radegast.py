# -*- coding: UTF-8 -*-
#appModules/radegast.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2014 Nick Stockton <nstockton@gmail.com>

"""App Module for radegast
"""


import addonHandler
import api
import appModuleHandler
import controlTypes
import oleacc
import re
import ui
import winUser
import windowUtils
from configobj import ConfigObj
from cStringIO import StringIO
from logHandler import log
from NVDAObjects.window import edit
from NVDAObjects.IAccessible import getNVDAObjectFromEvent
from os.path import join as joinPath
from validate import Validator

TIMESTAMPREGEX = re.compile(ur"^(\d+-\d+-\d+ \[\d+:\d+:\d+\]|\[\d+:\d+\]) ")

CONFIG_FILE_NAME = "radegast_config.ini"
ADDON_CONFIG = None

ADDON_CONFIG_SPEC = """
useTimeStamps = boolean(default=True)
"""


def loadAddonConfig(fileName):
	global ADDON_CONFIG
	if not ADDON_CONFIG:
		path = joinPath(addonHandler.getCodeAddon().path, fileName)
		ADDON_CONFIG = ConfigObj(path, configspec=StringIO(ADDON_CONFIG_SPEC), default_encoding="utf-8", encoding="utf-8", stringify=True)
		ADDON_CONFIG.newlines = "\n"
		val = Validator()
		result = ADDON_CONFIG.validate(val, preserve_errors=True, copy=True)
		if result != True:
			log.warning("Corrupted add-on configuration file: %s", result)

def saveAddonConfig():
	global ADDON_CONFIG
	if not ADDON_CONFIG:
		raise RuntimeError("Failed to load configuration file from the add-on folder.")
	val = Validator()
	ADDON_CONFIG.validate(val, copy=True)
	ADDON_CONFIG.write()


class HistoryText(edit.Edit):
	info = {}

	def isVisible(self):
		try:
			return windowUtils.findDescendantWindow(api.getForegroundObject().windowHandle, visible=True, controlID=self.windowControlID, className=self.appModule.historyWindowClassName) == self.windowHandle
		except LookupError:
			return False

	def getInfo(self, key):
		return self.info[self.windowControlID].get(key)

	def setInfo(self, **kwargs):
		if not self.windowControlID in self.info:
			self.info[self.windowControlID] = kwargs
		else:
			self.info[self.windowControlID].update(kwargs)

	def isSilent(self):
		return self.getInfo("silent")

	def getLines(self):
		if ADDON_CONFIG[u"useTimeStamps"]:
			return [line for line in self.windowText.splitlines() if line.strip()]
		else:
			return [TIMESTAMPREGEX.sub("", line) for line in self.windowText.splitlines() if line.strip()]

	def event_valueChange(self):
		oldVal = self.getInfo("lenOldLines")
		newLines = self.getLines()
		for line in newLines[oldVal:]:
			oldVal += 1
			if self.isSilent() or self.appModule.isSilent:
				continue
			elif self.getInfo("name") and not self.isVisible():
				ui.message("%s %s" % (self.getInfo("name"), line))
			else:
				ui.message(line)
		self.setInfo(lenOldLines=oldVal)

	def initOverlayClass(self):
		if not self.windowControlID in self.info:
			newLines = self.getLines()
			lenNewLines = len(newLines)
			if lenNewLines>1 and newLines[-2]=="====":
				lenNewLines -= 1
			self.setInfo(lenOldLines=lenNewLines, name=None, linePos=0, startMark=None, silent=False)
		if not self.getInfo("name") and self.isVisible():
			checkedTab = self.appModule.getCheckedTab()
			if checkedTab.name:
				self.setInfo(name=checkedTab.name)


class AppModule(appModuleHandler.AppModule):
	historyWindowClassName = "WindowsForms10.RichEdit20W.app.0.33c0d9d"
	isSilent = False
	tabsObj = None

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		if not ADDON_CONFIG:
			loadAddonConfig(CONFIG_FILE_NAME)

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.windowClassName==self.historyWindowClassName and obj.IAccessibleRole==oleacc.ROLE_SYSTEM_TEXT and controlTypes.STATE_READONLY in obj.states:
			clsList.insert(0, HistoryText)
		elif obj.windowClassName=="WindowsForms10.Window.8.app.0.33c0d9d" and obj.IAccessibleRole==oleacc.ROLE_SYSTEM_PUSHBUTTON and obj.name=="Chat" and obj.parent.windowClassName=="WindowsForms10.Window.8.app.0.33c0d9d" and obj.parent.IAccessibleRole==oleacc.ROLE_SYSTEM_TOOLBAR and obj.parent.name=="toolStrip1":
			self.tabsObj = obj.parent

	def getCheckedTab(self):
		try:
			if not self.tabsObj:
				self.tabsObj = api.getForegroundObject().parent.lastChild.lastChild.firstChild.firstChild.firstChild.firstChild.firstChild.firstChild.firstChild.lastChild.previous.firstChild.firstChild.firstChild
			checkedItems = [child for child in self.tabsObj.children if child.name and controlTypes.STATE_CHECKED in child.states]
			return None if not checkedItems else checkedItems[0]
		except AttributeError:
			return None

	def getHistoryObj(self):
		try:
			return getNVDAObjectFromEvent(windowUtils.findDescendantWindow(api.getForegroundObject().windowHandle, visible=True, className=self.historyWindowClassName), winUser.OBJID_CLIENT, 0)
		except LookupError:
			ui.message("No history window found.")
			return None

	def script_reviewUp(self,gesture):
		obj = self.getHistoryObj()
		if not obj:
			return
		historyLines = obj.getLines()
		linePos = obj.getInfo("linePos")
		if linePos >= len(historyLines):
			linePos = 0
		elif linePos > 0:
			linePos -= 1
		else:
			ui.message("Top:")
		obj.setInfo(linePos=linePos)
		if not historyLines:
			return ui.message("History empty.")
		ui.message(historyLines[linePos])
	script_reviewUp.__doc__=_("Review the previous history item.")

	def script_reviewDown(self,gesture):
		obj = self.getHistoryObj()
		if not obj:
			return
		historyLines = obj.getLines()
		linePos = obj.getInfo("linePos")
		if linePos >= len(historyLines):
			linePos = 0
		elif linePos+1 < len(historyLines):
			linePos += 1
		else:
			ui.message("Bottom:")
		obj.setInfo(linePos=linePos)
		if not historyLines:
			return ui.message("History empty.")
		ui.message(historyLines[linePos])
	script_reviewDown.__doc__=_("Review the next history item.")

	def script_reviewTop(self,gesture):
		obj = self.getHistoryObj()
		if not obj:
			return
		historyLines = obj.getLines()
		obj.setInfo(linePos=0)
		ui.message("Top:")
		if not historyLines:
			return ui.message("History empty.")
		ui.message(historyLines[0])
	script_reviewTop.__doc__=_("Set the review position to the first item in the history list.")

	def script_reviewBottom(self,gesture):
		obj = self.getHistoryObj()
		if not obj:
			return
		historyLines = obj.getLines()
		ui.message("Bottom:")
		if not historyLines:
			obj.setInfo(linePos=0)
			return ui.message("History empty.")
		obj.setInfo(linePos=len(historyLines) - 1)
		ui.message(historyLines[-1])
	script_reviewBottom.__doc__=_("Set the review position to the last item in the history list.")

	def script_startSelection(self,gesture):
		obj = self.getHistoryObj()
		if not obj:
			return
		historyLines = obj.getLines()
		if not historyLines:
			return ui.message("History empty.")
		linePos = obj.getInfo("linePos")
		if linePos < len(historyLines):
			obj.setInfo(startMark=linePos)
			ui.message("Start marked.")
		ui.message(historyLines[linePos])
	script_startSelection.__doc__=_("Mark the current review position in the history list as the start of a selection to be copied.")

	def script_copySelection(self,gesture):
		obj = self.getHistoryObj()
		if not obj:
			return
		historyLines = obj.getLines()
		if not historyLines:
			return ui.message("History empty.")
		linePos = obj.getInfo("linePos")
		startMark = obj.getInfo("startMark")
		if startMark==None or linePos>=len(historyLines):
			ui.message("No start marker set.")
		elif api.copyToClip("\r\n".join(historyLines[startMark:linePos+1])):
			obj.setInfo(startMark=None)
			ui.message("Selection copied.")
	script_copySelection.__doc__=_("Copy the history lines from the location of the start marker up to and including the last reviewed line to the clipboard.")

	def script_toggleTimeStamps(self,gesture):
		global ADDON_CONFIG
		ADDON_CONFIG[u"useTimeStamps"] = ADDON_CONFIG[u"useTimeStamps"] != True
		saveAddonConfig()
		ui.message("Time Stamps %s." % ("enabled" if ADDON_CONFIG[u"useTimeStamps"] else "disabled"))
	script_toggleTimeStamps.__doc__=_("Toggle the speaking of time stamps in history windows.")

	def script_toggleSilenceAll(self,gesture):
		self.isSilent = self.isSilent != True
		ui.message("Speech %s for all history windows." % ("enabled" if not self.isSilent else "disabled"))
	script_toggleSilenceAll.__doc__=_("Toggle automatic speaking of incoming text for all history windows.")

	def script_toggleSilenceWindow(self,gesture):
		obj = self.getHistoryObj()
		if not obj:
			return
		isSilent = obj.isSilent() != True
		obj.setInfo(silent=isSilent)
		ui.message("Speech %s for current history window." % ("enabled" if not isSilent else "disabled"))
	script_toggleSilenceWindow.__doc__=_("Toggle automatic speaking of incoming text for the current window.")

	__gestures = {
		"kb:NVDA+pageUp": "reviewUp",
		"kb:NVDA+pageDown": "reviewDown",
		"kb:control+NVDA+pageUp": "reviewTop",
		"kb:control+NVDA+pageDown": "reviewBottom",
		"kb:shift+NVDA+pageUp": "startSelection",
		"kb:shift+NVDA+pageDown": "copySelection",
		"kb:control+shift+NVDA+s": "toggleTimeStamps",
		"kb:f6": "toggleSilenceAll",
		"kb:shift+f6": "toggleSilenceWindow",
	}
