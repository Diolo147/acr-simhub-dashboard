param([int]$RenderWidth=2560,[int]$RenderHeight=1080,[string]$OutputPath='C:\Users\dxd\Documents\Codex\2026-09-28\new-chat\outputs\ACR Rally 21x9-preview.png')
$ErrorActionPreference='Stop'
try {
Set-Location 'C:\Program Files (x86)\SimHub'
[Environment]::CurrentDirectory='C:\Program Files (x86)\SimHub'
Add-Type -AssemblyName PresentationFramework,PresentationCore,WindowsBase
foreach($name in 'System.Windows.Interactivity.dll','MahApps.Metro.dll','MahApps.Metro.IconPacks.Core.dll','MahApps.Metro.IconPacks.FontAwesome.dll','MahApps.Metro.IconPacks.Material.dll') {
 [Reflection.Assembly]::LoadFrom((Join-Path (Get-Location) $name)) | Out-Null
}
$a=[Reflection.Assembly]::LoadFrom((Join-Path (Get-Location) 'SimHub.Plugins.dll'))
[Reflection.Assembly]::LoadFrom((Join-Path (Get-Location) 'Newtonsoft.Json.dll'))|Out-Null
$settings=New-Object Newtonsoft.Json.JsonSerializerSettings
$settings.TypeNameHandling=3
$t=$a.GetType('SimHub.Plugins.OutputPlugins.GraphicalDash.Dashboard')
$o=[Newtonsoft.Json.JsonConvert]::DeserializeObject([IO.File]::ReadAllText('I:\code\simhub-dashboard\work\preview.djson'),$t,$settings)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::OpenRead('I:\code\simhub-dashboard\build\ACR Rally 21x9\ACR Rally 21x9.djson.ressources')
foreach($im in $o.Images) {
 $entry=$zip.GetEntry($im.Name+$im.Extension)
 if(!$entry){continue}
 $stream=$entry.Open();$bytes=New-Object IO.MemoryStream;$stream.CopyTo($bytes);$stream.Dispose()
 $im.Data=$bytes.ToArray();$bytes.Position=0
 $bitmap=New-Object Windows.Media.Imaging.BitmapImage
 $bitmap.BeginInit();$bitmap.CacheOption=[Windows.Media.Imaging.BitmapCacheOption]::OnLoad;$bitmap.StreamSource=$bytes;$bitmap.EndInit();$bitmap.Freeze()
 $im.Image=$bitmap;$bytes.Dispose()
}
$zip.Dispose()
$editor=[Activator]::CreateInstance($a.GetType('SimHub.Plugins.OutputPlugins.GraphicalDash.EditorModel'))
$editor.Dashboard=$o;$o.Editor=$editor
function SetOwner($items) { foreach($item in $items) { $item.Owner=$o; if($item.Childrens){SetOwner $item.Childrens} } }
foreach($screen in $o.Screens) { $screen.Owner=$o;SetOwner $screen.Items }
$hostControl=[Activator]::CreateInstance($a.GetType('SimHub.Plugins.OutputPlugins.GraphicalDash.DashHostRendering'))
$hostControl.DataContext=$editor
$hostControl.Width=$RenderWidth;$hostControl.Height=$RenderHeight
$hostControl.ShownScreen=$o.Screens[0]
$hostControl.ApplyTemplate() | Out-Null
[Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([Action]{},[Windows.Threading.DispatcherPriority]::ContextIdle)
$hostControl.Measure([Windows.Size]::new($RenderWidth,$RenderHeight))
$hostControl.Arrange([Windows.Rect]::new(0,0,$RenderWidth,$RenderHeight))
$hostControl.UpdateLayout()
$a.GetType('SimHub.Plugins.OutputPlugins.GraphicalDash.ImageCapturer').GetMethod('SaveToPng',[type[]]@([Windows.FrameworkElement],[string])).Invoke($null,[object[]]@($hostControl,$OutputPath)) | Out-Null
'Native preview saved'
} catch { $_.Exception.ToString();exit 1 }
