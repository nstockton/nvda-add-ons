# -*- coding: utf-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Nick Stockton <nstockton@gmail.com>
# Portions of This Work Copyright (C) 2006-2013 NV Access Limited

# Built-in NVDA Modules
import addonHandler
import api
from NVDAObjects.behaviors import Terminal
from NVDAObjects.IAccessible import ContentGenericClient
from NVDAObjects.window import Window, DisplayModelLiveText
import oleacc
from speech import speakText

# Local shared functions and classes
from .ifcommon import *

CONFIG_FILE_NAME = "frotz_config.ini"


class MyDisplayModelLiveText(GameDisplayModelLiveText):
	def event_textChange(self):
		super(MyDisplayModelLiveText, self).event_textChange()
		self.gotoPrompt()


class IO(Window):
	def event_gainFocus(self):
		super(IO, self).event_gainFocus()
		try:
			output = self.parent.lastChild.lastChild.firstChild
		except AttributeError:
			output = None
		if isinstance(output, (Terminal, MyDisplayModelLiveText)):
			if not ADDON_CONFIG:
				loadAddonConfig(CONFIG_FILE_NAME)
			output.startMonitoring()
			api.setNavigatorObject(output)
			output.TextInfo.stripOuterWhitespace = True
			output.informStyleHelp = True
			output.gotoPrompt()
			mainLines, otherLines = output._getTextLines()
			for line in mainLines + otherLines:
				speakText(line)
			self._output = output
		else:
			self._output = None

	def event_loseFocus(self):
		if self._output:
			self._output.stopMonitoring()
			if not ADDON_CONFIG:
				loadAddonConfig(CONFIG_FILE_NAME)
			saveAddonConfig()


class AppModule(GameAppModule):
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if (obj.windowClassName.startswith("Afx:004D0000:20") or obj.windowClassName.startswith("Afx:00400000:20")) and obj.windowControlID == 59648 and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CLIENT:
			try:
				clsList.remove(ContentGenericClient)
			except ValueError:
				pass
			clsList[0:0] = (Terminal, MyDisplayModelLiveText)
		elif obj.windowClassName in ("Afx:004D0000:0", "Afx:00400000:0") and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CLIENT:
			clsList.insert(0, IO)
