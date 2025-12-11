Set WshShell = CreateObject("WScript.Shell")
' REPLACE THE PATH BELOW with the actual path to your Jarvis.bat file
WshShell.Run chr(34) & "C:\Users\Akhil\Desktop\Jarvis.bat" & chr(34), 0
Set WshShell = Nothing