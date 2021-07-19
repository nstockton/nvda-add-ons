# -*- coding: utf-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Nick Stockton <nstockton@gmail.com>
# Portions of This Work Copyright (C) 2006-2013 NV Access Limited

# Built-in NVDA modules
import api
import controlTypes
from NVDAObjects.behaviors import Terminal
from NVDAObjects.IAccessible import ContentGenericClient
from NVDAObjects.window import Window, DisplayModelEditableText, DisplayModelLiveText
import oleacc
from speech import speakText, speakTextInfo

# Local shared functions and classes
from .ifcommon import *

CONFIG_FILE_NAME = "winglk_config.ini"


try:
	REASON_CARET = controlTypes.REASON_CARET
except AttributeError:
	# NVDA >= 2021.1.0.
	REASON_CARET = controlTypes.OutputReason.CARET


class MyDisplayModelLiveText(GameDisplayModelLiveText):
	def event_textChange(self):
		super(MyDisplayModelLiveText, self).event_textChange()
		self.gotoPrompt()
		if self.appModule.appName == "heglk":
			for child in self.parent.parent.children:
				try:
					info=child.makeTextInfo(textInfos.POSITION_SELECTION)
					info.expand(textInfos.UNIT_LINE)
					if info.text.strip():
						speakTextInfo(info, unit=textInfos.UNIT_LINE, reason=REASON_CARET)
				except:
					pass

	def _getTextLines(self):
		parent = self.parent.parent.firstChild
		mainLines = self.myGetTextLines(parent.firstChild)
		otherLines = []
		parent = parent.next
		while parent:
			if parent.firstChild.displayText:
				child = parent.firstChild
			else:
				child = parent
			otherLines.extend(self.myGetTextLines(child))
			parent = parent.next
		return (mainLines, otherLines)


class IO(Window):
	def event_gainFocus(self):
		super(IO, self).event_gainFocus()
		try:
			output = self.parent.lastChild.firstChild.firstChild
		except AttributeError:
			output = None
		try:
			output = self.parent.lastChild.firstChild.firstChild.firstChild.firstChild
		except AttributeError:
			pass
		if isinstance(output, (Terminal, MyDisplayModelLiveText)):
			if not ADDON_CONFIG:
				loadAddonConfig(CONFIG_FILE_NAME)
			output.startMonitoring()
			api.setNavigatorObject(output)
			output.TextInfo.stripOuterWhitespace = True
			if output.appModule.appName != "heglk":
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
		if (obj.windowClassName.startswith("Afx:60CF0000:0:") or obj.windowClassName.startswith("Afx:10000000:0:")) and obj.windowControlID != 59648 and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CLIENT:
			try:
				clsList.remove(DisplayModelEditableText)
			except ValueError:
				pass
			try:
				clsList.remove(ContentGenericClient)
			except ValueError:
				pass
			clsList[0:0] = (Terminal, MyDisplayModelLiveText)
		elif obj.windowClassName in ("Afx:60CF0000:0", "Afx:10000000:0") and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CLIENT:
			clsList.insert(0, IO)
