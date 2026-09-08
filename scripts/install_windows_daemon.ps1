param(
    [string]$PythonExe = "python",
    [string]$ProjectDir = (Resolve-Path "$PSScriptRoot\..").Path
)

$TaskName = "DeskPilotAgent"
$Command = "cd /d `"$ProjectDir`" && $PythonExe -m deskpilot daemon --execute"

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $Command"
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Runs DeskPilot local AI agent after Windows logon" -Force
Write-Host "Installed Windows scheduled task: $TaskName"
