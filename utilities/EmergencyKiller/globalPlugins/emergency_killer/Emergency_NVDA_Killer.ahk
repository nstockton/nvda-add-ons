; A part of NonVisual Desktop Access (NVDA)
; This file is covered by the GNU General Public License.
; See the file COPYING for more details.
; Copyright (C) 2019 Nick Stockton <nstockton@gmail.com>

#NoEnv ; Recommended for performance and compatibility with future AutoHotkey releases.
#SingleInstance force ; Only one copy of this script should run at a time.
SendMode Input ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir% ; Ensures a consistent starting directory.

for i, param in A_Args
{
	if (param = "/exit")
	{
		ExitApp
	}
}

~lbutton:: ; Left button pressed. Pass it through.
left_down := true
keywait, lbutton
left_down := false
return

#if (left_down)
{
	rbutton:: ; Right button pressed. do *not* pass it through.
	try {
		SoundBeep, 500, 150
		Run open %A_ScriptDir%\kill_nvda.vbs
		; Run the program or programs provided on the command line.
		for i, param in A_Args
		{
			Run open %param%
		}
	} catch e {
		SoundBeep, 400, 100
		SoundBeep, 200, 100
		SoundBeep, 400, 100
		MsgBox Couldn't run kill_nvda.vbs.`nPlease make sure it's in the same directory as this script (%A_ScriptDir%).
	}
	return
	mbutton:: ; Middle button pressed, do *not* pass it through.
	try {
		SoundBeep, 500, 150
		Run open %A_ScriptDir%\kill_browser.vbs
	} catch e {
		SoundBeep, 400, 100
		SoundBeep, 200, 100
		SoundBeep, 400, 100
		MsgBox Couldn't run kill_browser.vbs.`nPlease make sure it's in the same directory as this script (%A_ScriptDir%).
	}
	return
}
