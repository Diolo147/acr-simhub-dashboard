"""Prepare an explicit publication manifest without uploading local work wholesale."""
from pathlib import Path
import json, shutil, hashlib
root=Path(__file__).resolve().parents[1]
out=Path(r'C:\Users\dxd\Documents\Codex\2026-09-28\new-chat\outputs')
fixture_dir=root/'work/fixtures';fixture_dir.mkdir(exist_ok=True)
catalog=json.loads((root/'work/live-catalog.json').read_text(encoding='utf-8'))
catalog['properties']=[p for p in catalog['properties'] if p['name'].startswith('DataCorePlugin.') or p['name'].startswith('ACRControlsPlugin.')]
(fixture_dir/'live-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
scripts=['verify-bindings.cjs','build-controls-plugin.ps1','test-auto-controls-reader.ps1','validate-native.ps1','export-native.ps1','render-native.ps1','prepare-live-preview.cjs','prepare-github-publication.py']
evidence=['component_samples.json','current-status-preview.json','controls-bridge-live.json','auto-reader-test-4.json','auto-reader-test-8.json','auto-reconnect-evidence.json','status-support-report.json']
memory=['auto-locator-profile.json','object-locator-20261009-235349.json','restart-polo-20261010-000950.json']
docs=['README.md','ROADMAP.md','AGENTS.md','PROJECT_STATUS.md','FIELD_MAP.md','使用说明.md','校准说明.md','遥测支持调查.md','ABS-TCS插件说明.md','内部内存读取说明.md','.gitignore']
dist=root/'dist';dist.mkdir(exist_ok=True)
for name in ['ACR Rally 21x9.simhubdash','ACR Settings Bridge.zip']:shutil.copy2(out/name,dist/name)
ignore=['/backups/','__pycache__/','*.pyc','*.npz','*.dmp','/work/*','!/work/fixtures/']
ignore += ['!/work/'+name for name in scripts+evidence]
ignore += ['!/work/memory/','/work/memory/*']+['!/work/memory/'+name for name in memory]
ignore += ['/build/ACRSettingsBridge/session-profile.json']
(root/'.gitignore').write_text('\n'.join(ignore)+'\n',encoding='utf-8')
members=[root/name for name in docs]+[p for p in (root/'src').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
members += [p for p in (root/'build/ACR Rally 21x9').rglob('*') if p.is_file()]
members += [root/'build/ACRSettingsBridge'/name for name in ['ACR.SettingsBridge.dll','auto-locator-profile.json']]
members += [root/'work'/name for name in scripts+evidence]+[root/'work/memory'/name for name in memory]+[fixture_dir/'live-catalog.json']+list(dist.iterdir())
files=[]
for p in sorted(set(members)):
 assert p.is_file(), str(p)
 b=p.read_bytes();files.append({'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(root/'work/github-publication-manifest.json').write_text(json.dumps({'repository':'Diolo147/acr-simhub-dashboard','files':files},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':len(files),'bytes':sum(x['bytes'] for x in files),'fixture_properties':len(catalog['properties'])}))
