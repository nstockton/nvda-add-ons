# -*- coding: utf-8 -*-
#globalPlugins/toggleReportIndentation.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2013 Nick Stockton <nstockton@gmail.com>

"""Global Plugin to provide a hotkey for toggling the speak line indentation setting of NVDA.
"""


import addonHandler
import globalPluginHandler
import config
import speech


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def script_toggle_report_line_indentation(self, gesture):
		value = config.conf[u"documentFormatting"][u"reportLineIndentation"]
		if isinstance(value, bool):
			value = not value
		elif value % 2:
			value -= 1
		else:
			value += 1
		config.conf[u"documentFormatting"][u"reportLineIndentation"] = value
		speech.speakMessage("Report line indentation {state}.".format(state = "on" if value is True or value % 2 else "off"))
	script_toggle_report_line_indentation.__doc__=_("Toggle the speaking of line indentation.")

	__gestures = {
		"kb:nvda+shift+i" : "toggle_report_line_indentation"
	}
