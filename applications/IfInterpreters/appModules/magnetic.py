# -*- coding: utf-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Nick Stockton <nstockton@gmail.com>
# Portions of This Work Copyright (C) 2006-2013 NV Access Limited

# Built-in NVDA Modules
import api
from NVDAObjects.behaviors import Terminal
from NVDAObjects.window import Window, DisplayModelEditableText, DisplayModelLiveText
import oleacc

# Local shared functions and classes
from .ifcommon import *

CONFIG_FILE_NAME = "magnetic_config.ini"


class MyDisplayModelLiveText(GameDisplayModelLiveText):
	def event_textChange(self):
		super(MyDisplayModelLiveText, self).event_textChange()
		self.gotoPrompt()

	def _getTextLines(self):
		output = self.myGetTextLines(self)
		obj = self.parent.next.next.firstChild
		if obj.windowClassName == "msctls_statusbar32" and obj.windowControlID == 59393 and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_STATUSBAR:
			for child in obj.children:
				if child and child.windowText != "Windows Magnetic":
					output.extend(self.myGetTextLines(child))
		return (output, [])


class IO(Window):
	def event_gainFocus(self):
		super(IO, self).event_gainFocus()
		if not ADDON_CONFIG:
			loadAddonConfig(CONFIG_FILE_NAME)
		self.startMonitoring()
		self.TextInfo.stripOuterWhitespace = True

	def event_loseFocus(self):
		self.stopMonitoring()
		if not ADDON_CONFIG:
			loadAddonConfig(CONFIG_FILE_NAME)
		saveAddonConfig()


class AppModule(GameAppModule):
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.windowClassName == "AfxFrameOrView70s" and obj.windowControlID == 59648 and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CLIENT:
			try:
				clsList.remove(DisplayModelEditableText)
			except ValueError:
				pass
			clsList[0:0] = (IO, Terminal, MyDisplayModelLiveText)
