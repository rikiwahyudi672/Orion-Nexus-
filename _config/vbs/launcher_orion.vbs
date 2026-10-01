Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "E:\Project Software\Orion"
WshShell.Run "python run_discord.py", 1, False
