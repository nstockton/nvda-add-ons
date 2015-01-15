# -*- coding: utf-8 -*-
#globalPlugins/MaximizeVolume.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2013 Nick Stockton <nstockton@gmail.com>

"""Global Plugin to provide a hotkey for unmuting and maximizing the system volume.
"""


import comtypes.client
import winsound
from win32con import VK_VOLUME_UP

import globalPluginHandler

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def script_raiseVolume(self, gesture):
		shell = comtypes.client.CreateObject("WScript.Shell")
		for count in xrange(50):
			shell.SendKeys(chr(VK_VOLUME_UP))
		for frequency in xrange(200, 1400, 200):
			winsound.Beep(frequency,100)
	script_raiseVolume.__doc__ = _("Unmute and raise the system volume to maximum.")

	__gestures={
		"kb:control+shift+NVDA+v": "raiseVolume",
	}
