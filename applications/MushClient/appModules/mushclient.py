# -*- coding: utf-8 -*-
#appModules/mushclient.py
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2014 Nick Stockton <nstockton@gmail.com>

"""App module for Mush Client
"""


# Built-in Python Modules
from cStringIO import StringIO
from os.path import join as pathJoin

# Built-in NVDA Modules
import addonHandler
import api
import appModuleHandler
import config
from configobj import ConfigObj
from logHandler import log
from NVDAObjects.IAccessible import ContentGenericClient
from NVDAObjects.window import Window, DisplayModelLiveText
import oleacc
import speech
import textInfos
from validate import Validator

MUSHCLIENT_CONFIG = None
MUSHCLIENT_CONFIG_SPEC = """
[presentation]
reportDynamicContentChanges = boolean(default=True)
[reviewCursor]
followCaret = boolean(default=False)
[keyboard]
speechInterruptForCharacters = boolean(default=False)
speechInterruptForEnter = boolean(default=True)
"""

ORIGINAL_CONFIG = ConfigObj(indent_type="\t", default_encoding="utf-8", encoding="utf-8")
ORIGINAL_CONFIG.newlines = "\r\n"
ORIGINAL_CONFIG[u"presentation"] = {u"reportDynamicContentChanges": config.conf[u"presentation"][u"reportDynamicContentChanges"]}
ORIGINAL_CONFIG[u"reviewCursor"] = {u"followCaret": config.conf[u"reviewCursor"][u"followCaret"]}
ORIGINAL_CONFIG[u"keyboard"] = {
	u"speechInterruptForCharacters": config.conf[u"keyboard"][u"speechInterruptForCharacters"],
	u"speechInterruptForEnter": config.conf[u"keyboard"][u"speechInterruptForEnter"]
}

def loadMushclientConfig():
	global MUSHCLIENT_CONFIG
	if not MUSHCLIENT_CONFIG:
		path = pathJoin(addonHandler.getCodeAddon().path, "config.ini")
		MUSHCLIENT_CONFIG = ConfigObj(path, configspec=StringIO(MUSHCLIENT_CONFIG_SPEC), indent_type="\t", default_encoding="utf-8", encoding="utf-8", stringify=True)
		MUSHCLIENT_CONFIG.newlines = "\r\n"
		val = Validator()
		result = MUSHCLIENT_CONFIG.validate(val, preserve_errors=True, copy=True)
		if result != True:
			log.warning("Corrupted MushClient add-on configuration file: %s", result)

def saveMushclientConfig():
	global MUSHCLIENT_CONFIG
	if not MUSHCLIENT_CONFIG:
		raise RuntimeError("Failed to load configuration file from the MushClient add-on folder.")
	MUSHCLIENT_CONFIG[u"presentation"][u"reportDynamicContentChanges"] = config.conf[u"presentation"][u"reportDynamicContentChanges"]
	MUSHCLIENT_CONFIG[u"reviewCursor"][u"followCaret"] = config.conf[u"reviewCursor"][u"followCaret"]
	MUSHCLIENT_CONFIG[u"keyboard"][u"speechInterruptForCharacters"] = config.conf[u"keyboard"][u"speechInterruptForCharacters"]
	MUSHCLIENT_CONFIG[u"keyboard"][u"speechInterruptForEnter"] = config.conf[u"keyboard"][u"speechInterruptForEnter"]
	val = Validator()
	MUSHCLIENT_CONFIG.validate(val, copy=True)
	MUSHCLIENT_CONFIG.write()


class Input(Window):
	def event_gainFocus(self):
		super(Input, self).event_gainFocus()
		try:
			output = self.parent.parent.parent.parent.firstChild.firstChild.firstChild.firstChild
		except AttributeError:
			output = None
		if isinstance(output, DisplayModelLiveText):
			output.startMonitoring()
			api.setNavigatorObject(output)
			output.TextInfo.stripOuterWhitespace = True
			self._output = output
			if not MUSHCLIENT_CONFIG:
				loadMushclientConfig()
			config.conf[u"presentation"][u"reportDynamicContentChanges"] = MUSHCLIENT_CONFIG[u"presentation"][u"reportDynamicContentChanges"]
			config.conf[u"reviewCursor"][u"followCaret"] = MUSHCLIENT_CONFIG[u"reviewCursor"][u"followCaret"]
			config.conf[u"keyboard"][u"speechInterruptForCharacters"] = MUSHCLIENT_CONFIG[u"keyboard"][u"speechInterruptForCharacters"]
			config.conf[u"keyboard"][u"speechInterruptForEnter"] = MUSHCLIENT_CONFIG[u"keyboard"][u"speechInterruptForEnter"]
		else:
			self._output = None

	def event_loseFocus(self):
		if self._output:
			self._output.stopMonitoring()
			if not MUSHCLIENT_CONFIG:
				loadMushclientConfig()
			saveMushclientConfig()
			config.conf[u"presentation"][u"reportDynamicContentChanges"] = ORIGINAL_CONFIG[u"presentation"][u"reportDynamicContentChanges"]
			config.conf[u"reviewCursor"][u"followCaret"] = ORIGINAL_CONFIG[u"reviewCursor"][u"followCaret"]
			config.conf[u"keyboard"][u"speechInterruptForCharacters"] = ORIGINAL_CONFIG[u"keyboard"][u"speechInterruptForCharacters"]
			config.conf[u"keyboard"][u"speechInterruptForEnter"] = ORIGINAL_CONFIG[u"keyboard"][u"speechInterruptForEnter"]


class AppModule(appModuleHandler.AppModule):
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.windowClassName == "AfxFrameOrView42s" and obj.windowControlID == 59648 and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CLIENT:
			try:
				clsList.remove(ContentGenericClient)
			except ValueError:
				pass
			clsList.insert(0, DisplayModelLiveText)
		elif  obj.windowClassName == "Edit" and obj.windowControlID == 59664:
			clsList.insert(0, Input)

	def script_review_bottom(self,gesture):
		info = api.getReviewPosition().obj.makeTextInfo(textInfos.POSITION_LAST)
		api.setReviewPosition(info.copy())
		info.expand(textInfos.UNIT_LINE)
		speech.speakTextInfo(info,unit=textInfos.UNIT_LINE,reason=speech.REASON_CARET)
	script_review_bottom.__doc__=_("Moves the review cursor to the bottom line of the current navigator object and speaks it")

	def script_toggle_interrupt_chars(self,gesture):
		setting = not config.conf[u"keyboard"][u"speechInterruptForCharacters"]
		config.conf[u"keyboard"][u"speechInterruptForCharacters"] = setting
		speech.speakMessage("Interrupt on character press {state}.".format(state = "off" if not setting else "on"))
	script_toggle_interrupt_chars.__doc__=_("Toggles the interrupting of speech when a character is pressed.")

	def script_toggle_interrupt_enter(self,gesture):
		setting = not config.conf[u"keyboard"][u"speechInterruptForEnter"]
		config.conf[u"keyboard"][u"speechInterruptForEnter"] = setting
		speech.speakMessage("Interrupt on enter press {state}.".format(state = "off" if not setting else "on"))
	script_toggle_interrupt_enter.__doc__=_("Toggles the interrupting of speech when the enter key is pressed.")

	__gestures = {
		"kb:NVDA+enter": "review_bottom",
		"kb:numpadEnter": "review_bottom",
		"kb:NVDA+8": "toggle_interrupt_chars",
		"kb:NVDA+9": "toggle_interrupt_enter",
	}
