' A part of NonVisual Desktop Access (NVDA)
' This file is covered by the GNU General Public License.
' See the file COPYING for more details.
' Copyright (C) 2019 Nick Stockton <nstockton@gmail.com>

On Error Resume Next

Set objWMIService = GetObject("winmgmts:" & "{impersonationLevel=impersonate}!\\.\root\cimv2")
Set colProcessList = objWMIService.ExecQuery("Select * from Win32_Process Where Name = 'nvda.exe' or Name = 'nvda_eoaProxy.exe' or Name = 'nvdaHelperRemoteLoader.exe' or Name = 'nvda_noUIAccess.exe' or Name = 'nvda_slave.exe' or Name = 'nvda_uiAccess.exe'")

For Each objProcess in colProcessList
	objProcess.Terminate(1)
Next

WScript.Sleep 100 ' Wait for 100 MilliSeconds.
Wscript.exit
