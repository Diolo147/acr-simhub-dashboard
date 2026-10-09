param([string]$OutputPath='C:\Users\dxd\Documents\Codex\2026-09-28\new-chat\outputs\ACR Rally 21x9.simhubdash')
Set-Location 'C:\Program Files (x86)\SimHub'
$a=[Reflection.Assembly]::LoadFrom((Join-Path (Get-Location) 'SimHub.Plugins.dll'))
$s=[Activator]::CreateInstance($a.GetType('SimHub.Plugins.OutputPlugins.GraphicalDash.GraphicalDashPluginSettings'))
$t=$a.GetType('SimHub.Plugins.OutputPlugins.GraphicalDash.GraphicalDashItem')
$item=[Activator]::CreateInstance($t,[object[]]@('C:\Program Files (x86)\SimHub\DashTemplates\ACR Rally 21x9\ACR Rally 21x9.djson',$s))
try {$ts=$a.GetTypes()} catch {$ts=$_.Exception.InnerException.Types}
$method=$null
foreach($type in $ts) {
 if($null -eq $type){continue}
 foreach($m in $type.GetMethods([Reflection.BindingFlags]'Public,NonPublic,Static,DeclaredOnly')) {
  if($m.Name -eq 'Export' -and $m.ToString() -like '*GraphicalDashItem*') {$method=$m;break}
 }
 if($method){break}
}
if(!$method){throw 'Native export API not found'}
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($OutputPath)) | Out-Null
$method.Invoke($null,[object[]]@($item,$OutputPath,$false)) | Out-Null
Get-Item -LiteralPath $OutputPath | Select-Object FullName,Length
