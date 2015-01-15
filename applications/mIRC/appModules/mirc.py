# -*- coding: utf-8 -*-
#appModules/mirc.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2010 James Teh <jamie@jantrid.net>
#Copyright (C) 2013 Nick Stockton <nstockton@gmail.com>

"""App module for mIRC
"""


import addonHandler
import appModuleHandler
import api
import config
import controlTypes
import oleacc
import speech
import textInfos
from NVDAObjects.window import Window, DisplayModelLiveText
from NVDAObjects.IAccessible import StaticText
from logHandler import log
from configobj import ConfigObj
from cStringIO import StringIO
from validate import Validator
from os.path import join as pathJoin

MIRC_CONFIG = None
MIRC_CONFIG_SPEC = """
[presentation]
reportDynamicContentChanges = boolean(default=True)
[reviewCursor]
followCaret = boolean(default=False)
[keyboard]
speechInterruptForCharacters = boolean(default=False)
speechInterruptForEnter = boolean(default=False)
"""

ORIGINAL_CONFIG = ConfigObj(indent_type="\t", default_encoding="utf-8", encoding="utf-8")
ORIGINAL_CONFIG.newlines = "\r\n"
ORIGINAL_CONFIG[u"presentation"] = {u"reportDynamicContentChanges": config.conf[u"presentation"][u"reportDynamicContentChanges"]}
ORIGINAL_CONFIG[u"reviewCursor"] = {u"followCaret": config.conf[u"reviewCursor"][u"followCaret"]}
ORIGINAL_CONFIG[u"keyboard"] = {
	u"speechInterruptForCharacters": config.conf[u"keyboard"][u"speechInterruptForCharacters"],
	u"speechInterruptForEnter": config.conf[u"keyboard"][u"speechInterruptForEnter"]
}


def loadMircConfig():
	global MIRC_CONFIG
	if not MIRC_CONFIG:
		path = pathJoin(addonHandler.getCodeAddon().path, "config.ini")
		MIRC_CONFIG = ConfigObj(path, configspec=StringIO(MIRC_CONFIG_SPEC), indent_type="\t", default_encoding="utf-8", encoding="utf-8", stringify=True)
		MIRC_CONFIG.newlines = "\r\n"
		val = Validator()
		result = MIRC_CONFIG.validate(val, preserve_errors=True, copy=True)
		if result != True:
			log.warning("Corrupted mIRC add-on configuration file: %s", result)

def saveMircConfig():
	global MIRC_CONFIG
	if not MIRC_CONFIG:
		raise RuntimeError("Failed to load configuration file from the mIRC add-on folder.")
	MIRC_CONFIG[u"presentation"][u"reportDynamicContentChanges"] = config.conf[u"presentation"][u"reportDynamicContentChanges"]
	MIRC_CONFIG[u"reviewCursor"][u"followCaret"] = config.conf[u"reviewCursor"][u"followCaret"]
	MIRC_CONFIG[u"keyboard"][u"speechInterruptForCharacters"] = config.conf[u"keyboard"][u"speechInterruptForCharacters"]
	MIRC_CONFIG[u"keyboard"][u"speechInterruptForEnter"] = config.conf[u"keyboard"][u"speechInterruptForEnter"]
	val = Validator()
	MIRC_CONFIG.validate(val, copy=True)
	MIRC_CONFIG.write()


class Input(Window):
	def event_gainFocus(self):
		super(Input, self).event_gainFocus()
		try: output = self.parent.parent.lastChild.firstChild
		except AttributeError: output = None
		if isinstance(output, DisplayModelLiveText):
			output.startMonitoring()
			api.setNavigatorObject(output)
			output.TextInfo.stripOuterWhitespace = True
			self._output = output
			if not MIRC_CONFIG:
				loadMircConfig()
			config.conf[u"presentation"][u"reportDynamicContentChanges"] = MIRC_CONFIG[u"presentation"][u"reportDynamicContentChanges"]
			config.conf[u"reviewCursor"][u"followCaret"] = MIRC_CONFIG[u"reviewCursor"][u"followCaret"]
			config.conf[u"keyboard"][u"speechInterruptForCharacters"] = MIRC_CONFIG[u"keyboard"][u"speechInterruptForCharacters"]
			config.conf[u"keyboard"][u"speechInterruptForEnter"] = MIRC_CONFIG[u"keyboard"][u"speechInterruptForEnter"]
		else:
			self._output = None

	def event_loseFocus(self):
		if self._output:
			self._output.stopMonitoring()
			if not MIRC_CONFIG:
				loadMircConfig()
			saveMircConfig()
			config.conf[u"presentation"][u"reportDynamicContentChanges"] = ORIGINAL_CONFIG[u"presentation"][u"reportDynamicContentChanges"]
			config.conf[u"reviewCursor"][u"followCaret"] = ORIGINAL_CONFIG[u"reviewCursor"][u"followCaret"]
			config.conf[u"keyboard"][u"speechInterruptForCharacters"] = ORIGINAL_CONFIG[u"keyboard"][u"speechInterruptForCharacters"]
			config.conf[u"keyboard"][u"speechInterruptForEnter"] = ORIGINAL_CONFIG[u"keyboard"][u"speechInterruptForEnter"]


class AppModule(appModuleHandler.AppModule):
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role == controlTypes.ROLE_WINDOW:
			return
		elif obj.windowClassName == "Static" and obj.windowControlID == 32918:
			clsList.remove(StaticText)
			clsList.insert(0, DisplayModelLiveText)
		elif obj.windowClassName == "RichEdit20W" and obj.windowControlID == 32921:
			clsList.insert(0, Input)

	def script_review_bottom(self,gesture):
		info=api.getReviewPosition().obj.makeTextInfo(textInfos.POSITION_LAST)
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
