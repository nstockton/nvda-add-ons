# -*- coding: utf-8 -*-
#appModules/jmc.py
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Nick Stockton <nstockton@gmail.com>

"""App module for JMC
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
import api
import appModuleHandler
import config
from configobj import ConfigObj
import controlTypes
from logHandler import log
from NVDAObjects.IAccessible import getNVDAObjectFromEvent, ContentGenericClient, IAccessible
from NVDAObjects.window import Window, DisplayModelLiveText
import oleacc
import speech
import textInfos
import ui
try:
	from validate import Validator
except ImportError:
	# NVDA >= 2019.3.0.
	from configobj.validate import Validator
import windowUtils
import winUser

# Initialize translations
addonHandler.initTranslation()

# Script category for JMC gestures.
# Translators: The name of the JMC gestures category.
SCRCAT_JMC = _("JMC")


class Input(Window):
	def event_gainFocus(self):
		super(Input, self).event_gainFocus()
		try:
			hwnd = windowUtils.findDescendantWindow(parent=api.getForegroundObject().windowHandle, visible=True, controlID=59648, className="AfxFrameOrView42u")
		except LookupError:
			try:
				hwnd = windowUtils.findDescendantWindow(parent=api.getForegroundObject().windowHandle, visible=True, controlID=59648, className="AfxFrameOrView42")
			except LookupError:
				hwnd = None
		output = None if hwnd is None else getNVDAObjectFromEvent(hwnd=hwnd, objectID=winUser.OBJID_CLIENT, childID=0)
		if isinstance(output, DisplayModelLiveText):
			output.startMonitoring()
			api.setNavigatorObject(output)
			output.TextInfo.stripOuterWhitespace = True
			self._output = output
		else:
			self._output = None

	def event_loseFocus(self):
		if self._output:
			self._output.stopMonitoring()


class AppModule(appModuleHandler.AppModule):
	jmcConfig = None
	originalConfig = {}

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if isinstance(obj, IAccessible) and obj.windowClassName in ("AfxFrameOrView42u", "AfxFrameOrView42") and obj.windowControlID == 59648 and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CLIENT:
			try:
				clsList.remove(ContentGenericClient)
			except ValueError:
				pass
			clsList.insert(0, DisplayModelLiveText)
		elif  isinstance(obj, IAccessible) and obj.windowClassName == "Edit" and obj.windowControlID == 1000 and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_TEXT:
			clsList.insert(0, Input)

	def event_appModule_gainFocus(self):
		if self.jmcConfig is not None:
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
			"speechInterruptForCharacters = boolean(default=True)",
			"speechInterruptForEnter = boolean(default=True)"
		))
		# Load and validate the NVDA configuration file for JMC.
		path = os.path.join(addonHandler.getCodeAddon().path, "config.ini")
		try:
			self.jmcConfig = ConfigObj(path, configspec=StringIO(configSpec), indent_type="\t", default_encoding="utf-8", encoding="utf-8", stringify=True)
			self.jmcConfig.newlines = "\r\n"
			val = Validator()
			result = self.jmcConfig.validate(val, preserve_errors=True, copy=True)
			if not result:
				log.warning("Corrupted JMC add-on configuration file: %s", result)
				self.jmcConfig = None
				return
		except Exception:
			log.warning("Unable to load the JMC add-on configuration file: %s", path)
			self.jmcConfig = None
			return
		# Update NVDA settings from the JMC configuration.
		config.conf["presentation"]["reportDynamicContentChanges"] = self.jmcConfig["presentation"]["reportDynamicContentChanges"]
		config.conf["reviewCursor"]["followCaret"] = self.jmcConfig["reviewCursor"]["followCaret"]
		config.conf["keyboard"]["speechInterruptForCharacters"] = self.jmcConfig["keyboard"]["speechInterruptForCharacters"]
		config.conf["keyboard"]["speechInterruptForEnter"] = self.jmcConfig["keyboard"]["speechInterruptForEnter"]

	def event_appModule_loseFocus(self):
		if self.jmcConfig is None:
			# Don't save what isn't there.
			return
		# Save the NVDA settings for JMC.
		self.jmcConfig["presentation"]["reportDynamicContentChanges"] = config.conf["presentation"]["reportDynamicContentChanges"]
		self.jmcConfig["reviewCursor"]["followCaret"] = config.conf["reviewCursor"]["followCaret"]
		self.jmcConfig["keyboard"]["speechInterruptForCharacters"] = config.conf["keyboard"]["speechInterruptForCharacters"]
		self.jmcConfig["keyboard"]["speechInterruptForEnter"] = config.conf["keyboard"]["speechInterruptForEnter"]
		val = Validator()
		result = self.jmcConfig.validate(val, preserve_errors=True, copy=True)
		if not result:
			log.warning("Corrupted JMC add-on configuration in memory: %s", result)
			self.jmcConfig = None
			return
		self.jmcConfig.write()
		self.jmcConfig = None
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
		speech.speakTextInfo(info, unit=textInfos.UNIT_LINE, reason=controlTypes.REASON_CARET)
	# Translators: Input help mode message for the review_bottom gesture.
	script_review_bottom.__doc__ = _("Moves the review cursor to the bottom line of the current navigator object and speaks it")
	script_review_bottom.category = SCRCAT_JMC

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
	script_toggle_interrupt_chars.category = SCRCAT_JMC

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
	script_toggle_interrupt_enter.__doc__=_("Toggles the interrupting of speech when the enter key is pressed.")
	script_toggle_interrupt_enter.category = SCRCAT_JMC

	__gestures = {
		"kb:NVDA+enter": "review_bottom",
		"kb:NVDA+8": "toggle_interrupt_chars",
		"kb:NVDA+9": "toggle_interrupt_enter"
	}
