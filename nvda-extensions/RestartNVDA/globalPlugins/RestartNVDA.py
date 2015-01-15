# -*- coding: utf-8 -*-
#globalPlugins/RestartNVDA.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2013 Nick Stockton <nstockton@gmail.com>

"""Global Plugin to provide a hotkey for immediately restarting NVDA.
"""


import core
import globalPluginHandler

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()

	def script_restart_nvda(self, gesture):
		core.restart()
	script_restart_nvda.__doc__=_("Restarts NVDA")

	__gestures = {
	"kb:nvda+control+shift+r" : "restart_nvda"
	}
