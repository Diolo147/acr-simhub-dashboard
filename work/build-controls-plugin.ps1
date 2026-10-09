$ErrorActionPreference='Stop'
$projectRoot='I:\code\simhub-dashboard'
$simhubRoot='C:\Program Files (x86)\SimHub'
$pluginBuild=Join-Path $projectRoot 'build\ACRSettingsBridge'
New-Item -ItemType Directory -Path $pluginBuild -Force | Out-Null
$frameworkRoot='C:\Windows\Microsoft.NET\Framework64\v4.0.30319'
$wpfRoot=Join-Path $frameworkRoot 'WPF'
& (Join-Path $frameworkRoot 'csc.exe') /nologo /target:library /platform:anycpu /optimize+ /utf8output `
 "/out:$pluginBuild\ACR.SettingsBridge.dll" `
 "/reference:$simhubRoot\SimHub.Plugins.dll" "/reference:$simhubRoot\GameReaderCommon.dll" `
 "/reference:$simhubRoot\SimHub.Logging.dll" "/reference:$simhubRoot\log4net.dll" "/reference:$simhubRoot\Newtonsoft.Json.dll" `
 "/reference:$wpfRoot\PresentationCore.dll" "/reference:$wpfRoot\WindowsBase.dll" `
 "$projectRoot\src\plugin\ControlMemoryReader.cs" "$projectRoot\src\plugin\AutoControlMemoryReader.cs" "$projectRoot\src\plugin\ACRControlsPlugin.cs"
if($LASTEXITCODE -ne 0){throw 'Plugin compilation failed'}
Copy-Item -LiteralPath "$projectRoot\work\memory\auto-locator-profile.json" -Destination "$pluginBuild\auto-locator-profile.json" -Force
Get-Item -LiteralPath "$pluginBuild\ACR.SettingsBridge.dll" | Select-Object FullName,Length
