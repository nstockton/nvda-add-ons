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
		setting = not config.conf[u"documentFormatting"][u"reportLineIndentation"]
		config.conf[u"documentFormatting"][u"reportLineIndentation"] = setting
		speech.speakMessage("Report line indentation {state}.".format(state = "off" if not setting else "on"))
	script_toggle_report_line_indentation.__doc__=_("Toggle the speaking of line indentation.")

	__gestures = {
		"kb:nvda+shift+i" : "toggle_report_line_indentation"
	}
