# -*- coding: UTF-8 -*-
#appModules/btsync
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
# Copyright (C) 2014 Nick Stockton <nstockton@gmail.com>

"""App Module for BTSync
"""


import api
import controlTypes
import winUser
from keyboardHandler import KeyboardInputGesture
from NVDAObjects.IAccessible import IAccessible


class BTSyncSetup1(IAccessible):
	"""Custom class for the first BTSync setup screen"""

	standardSetup = 1761
	iHaveASecret = 1762
	enterSecretHere = 1763
	iHaveReadAndAgree = 1734
	skipButton = 1586
	nextButton = 1587

	def leftMouseClick(self, obj, twice=False):
		# Store the current X-Y position of the mouse pointer.
		oldX, oldY = winUser.getCursorPos()
		# Move the mouse pointer to the location of obj.
		api.moveMouseToNVDAObject(obj)
		# Perform a left mouse click.
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN, 0, 0, None, None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP, 0, 0, None, None)
		if twice:
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN, 0, 0, None, None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP, 0, 0, None, None)
		# Move the mouse pointer to it's original X-Y position.
		winUser.setCursorPos(oldX, oldY)

	def script_leftArrowPressed(self, gesture):
		# What to do when left arrow is pressed.
		if self.windowControlID in [self.standardSetup, self.iHaveASecret, self.iHaveReadAndAgree, self.nextButton]:
			return
		# Send the gesture through to the application.
		gesture.send()

	def script_rightArrowPressed(self, gesture):
		# What to do when right arrow is pressed.
		if self.windowControlID in [self.standardSetup, self.iHaveASecret, self.iHaveReadAndAgree, self.skipButton]:
			return
		# Send the gesture through to the application.
		gesture.send()

	def script_upArrowPressed(self, gesture):
		# What to do when up arrow is pressed.
		try:
			if self.windowControlID == self.iHaveASecret:
				return self.leftMouseClick(self.parent.previous.firstChild)
			elif self.windowControlID in [self.standardSetup, self.iHaveReadAndAgree, self.skipButton, self.nextButton]:
				return
		except AttributeError:
			pass
		# Send the gesture through to the application.
		gesture.send()

	def script_downArrowPressed(self, gesture):
		# What to do when down arrow is pressed.
		try:
			if self.windowControlID == self.standardSetup:
				return self.leftMouseClick(self.parent.next.firstChild)
			elif self.windowControlID in [self.iHaveASecret, self.iHaveReadAndAgree, self.skipButton, self.nextButton]:
				return
		except AttributeError:
			pass
		# Send the gesture through to the application.
		gesture.send()

	def script_shiftTabPressed(self, gesture):
		# What to do when shift+tab is pressed.
		try:
			if self.windowControlID==self.standardSetup or self.windowControlID==self.iHaveASecret:
				checkBox = self.parent.parent.lastChild.previous.firstChild
				if not controlTypes.STATE_CHECKED in checkBox.states:
					self.leftMouseClick(checkBox, twice=True)
				else:
					KeyboardInputGesture.fromName("leftArrow").send()
				return
			elif self.windowControlID==self.iHaveReadAndAgree:
				if self.parent.previous.firstChild.windowControlID == self.enterSecretHere:
					self.leftMouseClick(self.parent.previous.firstChild)
				else:
					self.leftMouseClick(self.parent.previous.previous.firstChild)
				return
			elif self.windowControlID==self.enterSecretHere:
				return self.leftMouseClick(self.parent.previous.firstChild)
			elif self.windowControlID == self.nextButton:
				return self.leftMouseClick(self.parent.parent.firstChild.firstChild.lastChild.previous.firstChild, twice=True)
		except AttributeError:
			pass
		# Send the gesture through to the application.
		gesture.send()

	def script_tabPressed(self, gesture):
		# What to do when tab is pressed.
		try:
			if self.windowControlID == self.iHaveASecret:
				return self.leftMouseClick(self.parent.next.firstChild)
			elif self.windowControlID == self.standardSetup:
				return self.leftMouseClick(self.parent.next.next.firstChild, twice=True)
			elif self.windowControlID == self.enterSecretHere:
				return self.leftMouseClick(self.parent.next.firstChild, twice=True)
			elif self.windowControlID == self.skipButton:
				obj = self.parent.parent.firstChild.firstChild.firstChild.next.next.next.firstChild
				if not controlTypes.STATE_CHECKED in obj.states:
					obj = obj.parent.previous.firstChild
				return self.leftMouseClick(obj)
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
		for gesture, func in gestures.items():
			self.bindGesture(gesture, func)
		if self.windowControlID == self.enterSecretHere:
			self.name = self.appModule.labels.get(self.enterSecretHere)
		else:
			self.bindGesture("kb:leftArrow", "leftArrowPressed")
			self.bindGesture("kb:rightArrow", "rightArrowPressed")
