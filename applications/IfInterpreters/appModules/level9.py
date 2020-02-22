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

CONFIG_FILE_NAME = "level9_config.ini"


class MyDisplayModelLiveText(GameDisplayModelLiveText):
	def event_textChange(self):
		super(MyDisplayModelLiveText, self).event_textChange()
		self.gotoPrompt()


class IO(Window):
	def event_gainFocus(self):
		super(IO, self).event_gainFocus()
		if not ADDON_CONFIG:
			loadAddonConfig(CONFIG_FILE_NAME)
		self.startMonitoring()
		self.TextInfo.stripOuterWhitespace = True
		self.gotoPrompt()
		self.prompts = [
			">",
			"What next?",
			"What now?",
			"What gnow?",
			"Thy command, Sire?",
			"Really stop?",
			"Really restart?",
			"Another game?",
			"Would you like to play again?",
			"Please type RESTART, OOPS, RESTORE or RAM RESTORE:",
			"Thy game is over. Enter oops, ram restore, restore or restart.",
			"Thy life is at an end. Type OOPS, RAM RESTORE, RESTORE or RESTART.",
			"The adventure is over. Prithee type Restart or Restore:",
		]

	def event_loseFocus(self):
		self.stopMonitoring()
		if not ADDON_CONFIG:
			loadAddonConfig(CONFIG_FILE_NAME)
		saveAddonConfig()


class AppModule(GameAppModule):
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.windowClassName == "Level9" and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CLIENT:
			try:
				clsList.remove(DisplayModelEditableText)
			except ValueError:
				pass
			clsList[0:0] = (IO, Terminal, MyDisplayModelLiveText)
