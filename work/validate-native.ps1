Set-Location 'C:\Program Files (x86)\SimHub'
$a=[Reflection.Assembly]::LoadFrom((Join-Path (Get-Location) 'SimHub.Plugins.dll'))
[Reflection.Assembly]::LoadFrom((Join-Path (Get-Location) 'Newtonsoft.Json.dll'))|Out-Null
$t=$a.GetType('SimHub.Plugins.OutputPlugins.GraphicalDash.Dashboard')
try { $json=[IO.File]::ReadAllText('I:\code\simhub-dashboard\build\ACR Rally 21x9\ACR Rally 21x9.djson');$settings=New-Object Newtonsoft.Json.JsonSerializerSettings;$settings.TypeNameHandling=3;$o=[Newtonsoft.Json.JsonConvert]::DeserializeObject($json,$t,$settings);'OK '+$o.Screens.Count } catch { $_.Exception.ToString() }
