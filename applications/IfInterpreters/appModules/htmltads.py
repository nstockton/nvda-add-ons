# -*- coding: utf-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2014 Nick Stockton <nstockton@gmail.com>
# Portions of This Work Copyright (C) 2006-2013 NV Access Limited

# Built-in NVDA Modules
import api
from NVDAObjects.behaviors import Terminal
from NVDAObjects.IAccessible import ContentGenericClient
from NVDAObjects.window import Window, DisplayModelEditableText, DisplayModelLiveText
import oleacc

# Local shared functions and classes
from ifcommon import *

CONFIG_FILE_NAME = "tads_config.ini"


class MyDisplayModelLiveText(GameDisplayModelLiveText):
	def event_textChange(self):
		super(MyDisplayModelLiveText, self).event_textChange()
		self.gotoPrompt()

	def _getTextLines(self):
		output = self.myGetTextLines(self)
		for child in self.parent.previous.firstChild.children[:-1]:
			output.extend(self.myGetTextLines(child))
		parent = self.parent.next
		while parent:
			if parent.windowClassName == "TADS_Window":
				if parent.firstChild.displayText:
					child = parent.firstChild
				else:
					child = parent
				output.extend(self.myGetTextLines(child))
			parent = parent.next
		return (output, [])


class IO(Window):
	def event_gainFocus(self):
		super(IO, self).event_gainFocus()
		if not ADDON_CONFIG:
			loadAddonConfig(CONFIG_FILE_NAME)
		self.startMonitoring()
		self.TextInfo.stripOuterWhitespace = True
		self.gotoPrompt()

	def event_loseFocus(self):
		self.stopMonitoring()
		if not ADDON_CONFIG:
			loadAddonConfig(CONFIG_FILE_NAME)
		saveAddonConfig()


class AppModule(GameAppModule):
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.windowClassName == "TADS_Window" and obj.windowControlID == 0 and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CLIENT:
			try:
				clsList.remove(DisplayModelEditableText)
			except ValueError:
				pass
			try:
				clsList.remove(ContentGenericClient)
			except ValueError:
				pass
			try:
				if obj.parent.previous.firstChild.windowClassName == "msctls_statusbar32":
					clsList[0:0] = (IO, Terminal, MyDisplayModelLiveText)
				else:
					clsList.insert(0, DisplayModelLiveText)
			except ValueError:
				pass
