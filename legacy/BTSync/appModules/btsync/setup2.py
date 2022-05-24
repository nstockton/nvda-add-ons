# -*- coding: UTF-8 -*-
#appModules/btsync
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
# Copyright (C) 2014 Nick Stockton <nstockton@gmail.com>

"""App Module for BTSync
"""


import time
from NVDAObjects.IAccessible import IAccessible


class BTSyncSetup2(IAccessible):
	"""Custom class for the second BTSync setup screen"""

	chooseAnyFolder = 1768
	browseButton = 1586
	skipButton = 1586
	nextButton = 1587
	backButton = 1588

	def focusObj(self, obj):
		obj.setFocus()
		time.sleep(0.05)
		obj.setFocus()

	def script_leftArrowPressed(self, gesture):
		# What to do when left arrow is pressed.
		try:
			if self.windowControlID==self.nextButton or (self.windowControlID==self.browseButton and self.parent.previous.firstChild.windowControlID==self.chooseAnyFolder):
				return
		except AttributeError:
			pass
		# Send the gesture through to the application.
		gesture.send()

	def script_rightArrowPressed(self, gesture):
		# What to do when right arrow is pressed.
		try:
			if self.windowControlID==self.backButton or (self.windowControlID==self.browseButton and self.parent.previous.firstChild.windowControlID==self.chooseAnyFolder):
				return
		except AttributeError:
			pass
		# Send the gesture through to the application.
		gesture.send()

	def script_upArrowPressed(self, gesture):
		# What to do when up arrow is pressed.
		if self.windowControlID in [self.skipButton, self.nextButton, self.backButton]:
			return
		# Send the gesture through to the application.
		gesture.send()

	def script_downArrowPressed(self, gesture):
		# What to do when down arrow is pressed.
		if self.windowControlID in [self.skipButton, self.nextButton, self.backButton]:
			return
		# Send the gesture through to the application.
		gesture.send()

	def script_shiftTabPressed(self, gesture):
		# What to do when shift+tab is pressed.
		try:
			if self.windowControlID == self.nextButton:
				return self.focusObj(self.parent.parent.firstChild.firstChild.lastChild.previous.firstChild)
			elif self.windowControlID==self.browseButton and self.parent.previous.firstChild.windowControlID==self.chooseAnyFolder:
				return self.focusObj(self.parent.previous.firstChild)
		except AttributeError:
			pass
		# Send the gesture through to the application.
		gesture.send()

	def script_tabPressed(self, gesture):
		# What to do when tab is pressed.
		try:
			if self.windowControlID == self.chooseAnyFolder:
				return self.focusObj(self.parent.next.firstChild)
			elif self.windowControlID==self.backButton:
				return self.focusObj(self.parent.parent.firstChild.firstChild.firstChild.next.next.firstChild)
		except AttributeError:
			pass
		# Send the gesture through to the application.
		gesture.send()

	def initOverlayClass(self):
		gestures = {
			"kb:upArrow": "upArrowPressed",
			"kb:downArrow": "downArrowPressed",
			"kb:shift+tab": "shiftTabPressed",
			"kb:tab": "tabPressed",
		}
		for gesture, func in gestures.items():
			self.bindGesture(gesture, func)
		if self.windowControlID != self.chooseAnyFolder:
			self.bindGesture("kb:leftArrow", "leftArrowPressed")
			self.bindGesture("kb:rightArrow", "rightArrowPressed")
