# -*- coding: utf-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2019 Nick Stockton <nstockton@gmail.com>

import os
import sys

from globalPluginHandler import GlobalPlugin
import addonHandler
import shellapi
import winUser

addonHandler.initTranslation()


class GlobalPlugin(GlobalPlugin):
	scriptCategory = _("Emergency Killer")

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		self._path = os.path.abspath(os.path.dirname(__file__))
		shellapi.ShellExecute(None, "open", os.path.join(self._path, "Emergency_NVDA_Killer.exe"), f"\"{sys.argv[0]}\"", self._path, winUser.SW_SHOWNORMAL)

	def terminate(self):
		shellapi.ShellExecute(None, "open", os.path.join(self._path, "Emergency_NVDA_Killer.exe"), "/exit", self._path, winUser.SW_SHOWNORMAL)
