param([string]$SamplePath='I:\code\simhub-dashboard\work\status-20261009-234214.json')
$ErrorActionPreference='Stop'
$projectRoot='I:\code\simhub-dashboard'
$simhubRoot='C:\Program Files (x86)\SimHub'
Set-Location $simhubRoot
[Reflection.Assembly]::LoadFrom("$simhubRoot\Newtonsoft.Json.dll")|Out-Null
[Reflection.Assembly]::LoadFrom("$projectRoot\build\ACRSettingsBridge\ACR.SettingsBridge.dll")|Out-Null
$sample=Get-Content -LiteralPath $SamplePath -Raw -Encoding UTF8|ConvertFrom-Json
$config="$projectRoot\build\ACRSettingsBridge\auto-locator-profile.json"
$reader=[ACR.NativeControls.AutoControlMemoryReader]::new($config)
try {
 $clock=[Diagnostics.Stopwatch]::StartNew()
 $value=$reader.Read([double]$sample.physics.rpm,[double]$sample.physics.fuel,$null)
 if(!$value.Valid){throw "Automatic locate failed: $($value.Status)"}
 $result=[ordered]@{pointer_size=[IntPtr]::Size;pid=$reader.ProcessId;object=$reader.ObjectAddress;locate_ms=$reader.LastLocateMs;total_ms=$clock.Elapsed.TotalMilliseconds;value=$value}
 $result|ConvertTo-Json -Depth 5
 $result|ConvertTo-Json -Depth 5|Set-Content -LiteralPath "$projectRoot\work\auto-reader-test-$([IntPtr]::Size).json" -Encoding UTF8
 $reader.ResetVehicle()
 if(!$reader.Read([double]$sample.physics.rpm,[double]$sample.physics.fuel,$null).Valid){throw 'Failed to relocate after vehicle reset'}
 if($reader.Read([double]$sample.physics.rpm,999.0,$null).Valid){throw 'Wrong vehicle telemetry accepted'}
} finally {$reader.Dispose()}
$bad=Get-Content -LiteralPath $config -Raw -Encoding UTF8|ConvertFrom-Json
$bad.sha256='0'*64
$badFile="$projectRoot\work\invalid-auto-version.json"
$bad|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $badFile -Encoding UTF8
$reader=[ACR.NativeControls.AutoControlMemoryReader]::new($badFile)
try {if($reader.Read([double]$sample.physics.rpm,[double]$sample.physics.fuel,$null).Valid){throw 'Wrong executable hash accepted'}}finally{$reader.Dispose()}
'PASS: automatic process/module/object resolution, vehicle reset, wrong vehicle and version rejection'
