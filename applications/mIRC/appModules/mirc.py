﻿# -*- coding: utf-8 -*-
#appModules/mirc.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2010 James Teh <jamie@jantrid.net>
#Copyright (C) 2016 Nick Stockton <nstockton@gmail.com>

"""App module for mIRC
"""


# Built-in Python Modules
try:
	from cStringIO import StringIO
except ImportError:
	# Python3
	from io import StringIO
import os.path

# Built-in NVDA Modules
import addonHandler
import appModuleHandler
import api
import oleacc
import config
from configobj import ConfigObj
import controlTypes
from logHandler import log
import nvdaBuiltin.appModules.mirc
import NVDAObjects.IAccessible
import speech
import textInfos
import ui
try:
	from validate import Validator
except ImportError:
	# NVDA >= 2019.3.0.
	from configobj.validate import Validator

# Initialize translations
addonHandler.initTranslation()

# Script category for mIRC gestures.
# Translators: The name of the mIRC gestures category.
SCRCAT_MIRC = _("mIRC")


try:
	REASON_CARET = controlTypes.REASON_CARET
except AttributeError:
	# NVDA >= 2021.1.0.
	REASON_CARET = controlTypes.OutputReason.CARET


class AppModule(nvdaBuiltin.appModules.mirc.AppModule):
	mircConfig = None
	originalConfig = {}

	def event_NVDAObject_init(self, obj):
		if isinstance(obj, NVDAObjects.IAccessible.IAccessible) and obj.windowClassName == "Static" and obj.windowControlID == 32918 and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_STATICTEXT:
			api.setNavigatorObject(obj)

	def event_appModule_gainFocus(self):
		if self.mircConfig is not None:
			# Don't clobber the already loaded config.
			return
		# Save original NVDA settings.
		self.originalConfig["reportDynamicContentChanges"] = config.conf["presentation"]["reportDynamicContentChanges"]
		self.originalConfig["followCaret"] = config.conf["reviewCursor"]["followCaret"]
		self.originalConfig["speechInterruptForCharacters"] = config.conf["keyboard"]["speechInterruptForCharacters"]
		self.originalConfig["speechInterruptForEnter"] = config.conf["keyboard"]["speechInterruptForEnter"]
		# Define default values in case the configuration file doesn't exist.
		configSpec = "\n".join((
			"[presentation]",
			"reportDynamicContentChanges = boolean(default=True)",
			"[reviewCursor]",
			"followCaret = boolean(default=False)",
			"[keyboard]",
			"speechInterruptForCharacters = boolean(default=False)",
			"speechInterruptForEnter = boolean(default=True)"
		))
		# Load and validate the NVDA configuration file for mIRC.
		path = os.path.join(addonHandler.getCodeAddon().path, "config.ini")
		try:
			self.mircConfig = ConfigObj(path, configspec=StringIO(configSpec), indent_type="\t", default_encoding="utf-8", encoding="utf-8", stringify=True)
			self.mircConfig.newlines = "\r\n"
			val = Validator()
			result = self.mircConfig.validate(val, preserve_errors=True, copy=True)
			if not result:
				log.warning("Corrupted mIRC add-on configuration file: %s", result)
				self.mircConfig = None
				return
		except Exception:
			log.warning("Unable to load the mIRC add-on configuration file: %s", path)
			self.mircConfig = None
			return
		# Update NVDA settings from the mIRC configuration.
		config.conf["presentation"]["reportDynamicContentChanges"] = self.mircConfig["presentation"]["reportDynamicContentChanges"]
		config.conf["reviewCursor"]["followCaret"] = self.mircConfig["reviewCursor"]["followCaret"]
		config.conf["keyboard"]["speechInterruptForCharacters"] = self.mircConfig["keyboard"]["speechInterruptForCharacters"]
		config.conf["keyboard"]["speechInterruptForEnter"] = self.mircConfig["keyboard"]["speechInterruptForEnter"]

	def event_appModule_loseFocus(self):
		if self.mircConfig is None:
			# Don't save what isn't there.
			return
		# Save the NVDA settings for mIRC.
		self.mircConfig["presentation"]["reportDynamicContentChanges"] = config.conf["presentation"]["reportDynamicContentChanges"]
		self.mircConfig["reviewCursor"]["followCaret"] = config.conf["reviewCursor"]["followCaret"]
		self.mircConfig["keyboard"]["speechInterruptForCharacters"] = config.conf["keyboard"]["speechInterruptForCharacters"]
		self.mircConfig["keyboard"]["speechInterruptForEnter"] = config.conf["keyboard"]["speechInterruptForEnter"]
		val = Validator()
		result = self.mircConfig.validate(val, preserve_errors=True, copy=True)
		if not result:
			log.warning("Corrupted mIRC add-on configuration in memory: %s", result)
			self.mircConfig = None
			return
		self.mircConfig.write()
		self.mircConfig = None
		# Restore the original NVDA settings.
		config.conf["presentation"]["reportDynamicContentChanges"] = self.originalConfig["reportDynamicContentChanges"]
		config.conf["reviewCursor"]["followCaret"] = self.originalConfig["followCaret"]
		config.conf["keyboard"]["speechInterruptForCharacters"] = self.originalConfig["speechInterruptForCharacters"]
		config.conf["keyboard"]["speechInterruptForEnter"] = self.originalConfig["speechInterruptForEnter"]

	def script_review_bottom(self, gesture):
		info = api.getReviewPosition().obj.makeTextInfo(textInfos.POSITION_LAST)
		api.setReviewPosition(info)
		info.expand(textInfos.UNIT_LINE)
		speech.cancelSpeech()
		speech.speakTextInfo(info, unit=textInfos.UNIT_LINE, reason=REASON_CARET)
	# Translators: Input help mode message for the review_bottom gesture.
	script_review_bottom.__doc__ = _("Moves the review cursor to the bottom line of the current navigator object and speaks it")
	script_review_bottom.category = SCRCAT_MIRC

	def script_toggle_interrupt_chars(self, gesture):
		value = not config.conf[u"keyboard"][u"speechInterruptForCharacters"]
		config.conf[u"keyboard"][u"speechInterruptForCharacters"] = value
		speech.cancelSpeech()
		# Translators: Indicates that NVDA will interrupt on character press.
		enabled = _("Interrupt on character press on.")
		# Translators: Indicates that NVDA will *not* interrupt on character press.
		disabled = _("Interrupt on character press off.")
		ui.message(enabled if value else disabled)
	# Translators: Input help mode message for the toggle_interrupt_chars gesture.
	script_toggle_interrupt_chars.__doc__ = _("Toggles the interrupting of speech when a character is pressed.")
	script_toggle_interrupt_chars.category = SCRCAT_MIRC

	def script_toggle_interrupt_enter(self, gesture):
		value = not config.conf[u"keyboard"][u"speechInterruptForEnter"]
		config.conf[u"keyboard"][u"speechInterruptForEnter"] = value
		speech.cancelSpeech()
		# Translators: Indicates that NVDA will interrupt on enter press.
		enabled = _("Interrupt on enter press on.")
		# Translators: Indicates that NVDA will *not* interrupt on enter press.
		disabled = _("Interrupt on enter press off.")
		ui.message(enabled if value else disabled)
	# Translators: Input help mode message for the toggle_interrupt_enter gesture.
	script_toggle_interrupt_enter.__doc__ = _("Toggles the interrupting of speech when the enter key is pressed.")
	script_toggle_interrupt_enter.category = SCRCAT_MIRC

	__gestures = {
		"kb:NVDA+enter": "review_bottom",
		"kb:numpadEnter": "review_bottom",
		"kb:NVDA+8": "toggle_interrupt_chars",
		"kb:NVDA+9": "toggle_interrupt_enter"
	}
