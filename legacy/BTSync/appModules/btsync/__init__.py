# -*- coding: UTF-8 -*-
#appModules/btsync
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
# Copyright (C) 2014 Nick Stockton <nstockton@gmail.com>

"""App Module for BTSync
"""


import api
import appModuleHandler
import controlTypes
import oleacc
import windowUtils
import winUser
from NVDAObjects.IAccessible import getNVDAObjectFromEvent, IAccessible
from NVDAObjects.window import Window

from setup1 import BTSyncSetup1
from setup2 import BTSyncSetup2
from setup3 import BTSyncSetup3


class DuplicateFocusListView(IAccessible):
	"""A list view which annoyingly fires focus events every second, even when a menu is open."""
	# This class was copied from the uTorrent module in the NVDA source.
	# Copyright (C) 2010 James Teh <jamie@jantrid.net>

	def _get_shouldAllowIAccessibleFocusEvent(self):
		# Stop annoying duplicate focus events, which are fired even if a menu is open.
		focus = api.getFocusObject()
		focusRole = focus.role
		focusStates = focus.states
		if (self == focus or (focusRole == controlTypes.ROLE_MENUITEM and controlTypes.STATE_FOCUSED in focusStates) or (focusRole == controlTypes.ROLE_POPUPMENU and controlTypes.STATE_INVISIBLE not in focusStates)):
			return False
		return super(DuplicateFocusListView, self).shouldAllowIAccessibleFocusEvent


class BTSyncTabItem(IAccessible):
	"""Custom class for tab control items"""

	def script_tabPressed(self, gesture):
		# What to do when tab or shift+tab is pressed.
		try:
			if self.IAccessibleChildID == 3:
				# Set focus to the active transfers list view if the Transfers tab is selected and tab/shift+tab is then pressed.  We need to do this twice.
				obj = self.parent.parent.previous.firstChild.firstChild.firstChild
				obj.setFocus()
				obj.setFocus()
				# We don't need to do anything else in this case, so return.
				return
		except:
			pass
		# Send the gesture through to the application.
		gesture.send()

	__gestures = {
		"kb:shift+tab": "tabPressed",
		"kb:tab": "tabPressed",
	}


class BTSyncTransfersListView(DuplicateFocusListView):
	"""Custom class for the transfers list view"""

	def script_tabPressed(self, gesture):
		# What to do when tab or shift+tab is pressed.
		try:
			# Set focus to the transfers tab item.
			obj = getNVDAObjectFromEvent(self.appModule.getTabControlHandle(), winUser.OBJID_CLIENT, 0)
			if not obj or obj.IAccessibleRole!=oleacc.ROLE_SYSTEM_PAGETABLIST:
				return
			for child in obj.children:
				# Find the child (tab) that is currently selected, but only if it doesn't already have focus.
				if controlTypes.STATE_SELECTED in child.states and not child.hasFocus:
					# The selected child (tab) was found.  Set focus to it, and break out of the loop as looping through subsequent child objects is now pointless.
					child.setFocus()
					break
		except:
			pass

	__gestures = {
		"kb:shift+tab": "tabPressed",
		"kb:tab": "tabPressed",
	}


class AppModule(appModuleHandler.AppModule):
	labels = {}

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role == controlTypes.ROLE_WINDOW:
			# We don't need these.
			return
		if obj.windowClassName=="#32770" and obj.IAccessibleRole==oleacc.ROLE_SYSTEM_DIALOG:
			# Change the role so NVDA doesn't announce 'Dialog' when the user enters the transfers tab.
			obj.role = controlTypes.ROLE_PROPERTYPAGE
		if obj.windowClassName=="Edit" and obj.IAccessibleRole==oleacc.ROLE_SYSTEM_TEXT:
			# Some of the edit boxes aren't being named correctly or at all.  We therefore name them manually.
			try:
				if obj.windowControlID in [1718, 1514, 1740, 1720]:
					obj.name = obj.parent.previous.previous.firstChild.name
				elif obj.windowControlID == 1750:
					obj.name = obj.parent.previous.previous.previous.firstChild.name
			except AttributeError:
				pass
		if isinstance(obj, Window) and obj.windowClassName == "SysListView32":
			if obj.windowControlID == 1722:
				clsList.insert(0, BTSyncTransfersListView)
			else:
				clsList.insert(0, DuplicateFocusListView)
		if obj.windowClassName=="SysTabControl32" and obj.windowControlID==1723 and obj.IAccessibleRole==oleacc.ROLE_SYSTEM_PAGETAB:
			clsList.insert(0, BTSyncTabItem)
		# If we aren't in the installer, return as there are control properties in the installer that conflict with ones in the main program.
		if self.getTabControlHandle():
			return
		if obj.windowClassName == "Button":
			if obj.IAccessibleRole == oleacc.ROLE_SYSTEM_CHECKBUTTON:
				if obj.windowControlID==BTSyncSetup1.iHaveReadAndAgree:
					try:
						obj.name = obj.parent.next.firstChild.name
					except AttributeError:
						pass
					clsList.insert(0, BTSyncSetup1)
			elif obj.IAccessibleRole == oleacc.ROLE_SYSTEM_RADIOBUTTON:
				if obj.windowControlID in [BTSyncSetup1.standardSetup, BTSyncSetup1.iHaveASecret]:
					clsList.insert(0, BTSyncSetup1)
			elif obj.IAccessibleRole == oleacc.ROLE_SYSTEM_PUSHBUTTON:
				if obj.windowControlID in [BTSyncSetup1.skipButton, BTSyncSetup1.nextButton, BTSyncSetup2.backButton]:
					try:
						if obj.parent.previous.firstChild.windowControlID==BTSyncSetup2.chooseAnyFolder or obj.parent.parent.firstChild.firstChild.firstChild.next.next.firstChild.windowControlID==BTSyncSetup2.chooseAnyFolder:
							clsList.insert(0, BTSyncSetup2)
						elif obj.parent.parent.firstChild.firstChild.lastChild.previous.firstChild.windowControlID == BTSyncSetup1.iHaveReadAndAgree:
							clsList.insert(0, BTSyncSetup1)
						elif obj.parent.parent.firstChild.firstChild.lastChild.previous.firstChild.windowControlID == BTSyncSetup3.copyButton:
							clsList.insert(0, BTSyncSetup3)
					except AttributeError:
						pass
				elif obj.windowControlID == BTSyncSetup3.copyButton:
					clsList.insert(0, BTSyncSetup3)
		if obj.windowClassName == "Edit" and obj.IAccessibleRole == oleacc.ROLE_SYSTEM_TEXT:
			if obj.windowControlID == BTSyncSetup1.enterSecretHere:
				if obj.displayText and not self.labels.get(BTSyncSetup1.enterSecretHere):
					self.labels[BTSyncSetup1.enterSecretHere] = obj.displayText
				clsList.insert(0, BTSyncSetup1)
			elif obj.windowControlID == BTSyncSetup2.chooseAnyFolder:
				clsList.insert(0, BTSyncSetup2)
			elif obj.windowControlID == BTSyncSetup3.ThisIsASecret:
				clsList.insert(0, BTSyncSetup3)

	def getTabControlHandle(self):
		try:
			return windowUtils.findDescendantWindow(api.getForegroundObject().windowHandle, visible=True, controlID=1723, className="SysTabControl32")
		except LookupError:
			return None
