// Dashboard-local, ES5-compatible helpers. No shared mutable global state.
// Normalized SimHub fields are preferred; raw units are converted explicitly.
function acrProp(name) { try { return $prop(name); } catch(e) { return null; } }
function acrNum(name) { var v=acrProp(name); return v===null || v===undefined || v==='' || !isFinite(Number(v)) ? null : Number(v); }
function acrD(name) { return acrNum('DataCorePlugin.GameData.'+name); }
function acrR(name) { return acrNum('DataCorePlugin.GameRawData.Physics.'+name); }
function acrClamp(v,a,b) { return Math.max(a,Math.min(b,v)); }
function acrState() {
 var now=Date.now(), running=acrNum('DataCorePlugin.GameRunning')===1 && String(acrProp('DataCorePlugin.CurrentGame')).toLowerCase()==='assettocorsarally';
 var id=acrR('PacketId'), paused=acrNum('DataCorePlugin.GamePaused')===1;
 var key=String(acrProp('DataCorePlugin.GameData.CarModel')||'')+'|'+String(acrProp('DataCorePlugin.GameData.TrackName')||'');
 var s=root.acrSession;
 if(!s || !running || s.key!==key || (id!==null && s.id!==null && id<s.id)) {
  s={key:key,id:id,changed:now,last:now,elapsed:0,peak:0,started:false}; root.acrSession=s;
 }
 if(id!==s.id) { s.id=id;s.changed=now; }
 var valid=running && id!==null && (id>0 || acrD('Rpms')>0 || acrR('WheelsPressure01')>0);
 var fresh=valid && now-s.changed<3000;
 var active=fresh && !paused, speed=acrD('SpeedKmh');
 if(active && speed!==null && speed>1) s.started=true;
 if(active && s.started) s.elapsed+=Math.min(250,Math.max(0,now-s.last));
 if(active && speed!==null) s.peak=Math.max(s.peak,speed);
 s.last=now;
 return {running:running,valid:valid,live:active,paused:paused,stale:valid&&!fresh,elapsed:s.elapsed,peak:s.peak};
}
function acrValue(key) {
 var state=acrState(); if(!state.valid || state.stale) return null;
 var v,u;
 if(key==='rpm') return acrD('Rpms');
 if(key==='speed') return acrD('SpeedKmh');
 if(key==='gear') return acrProp('DataCorePlugin.GameData.Gear');
 if(key==='throttle'||key==='brake'||key==='clutch') return acrD(key.charAt(0).toUpperCase()+key.slice(1));
 if(key==='water') {v=acrD('WaterTemperature');u=String(acrProp('DataCorePlugin.GameData.TemperatureUnit'));return v!==null&&(v!==0||acrR('waterTemperature')>0)?(u.toLowerCase().indexOf('fahren')>=0?(v-32)*5/9:v):null;}
 if(key==='fuel') return acrD('Fuel');
 if(key==='air'||key==='road') {v=acrR(key==='air'?'AirTemp':'RoadTemp');return v===null||v<100||v>500?null:v-273.15;}
 if(key==='fuelPercent') {v=acrD('MaxFuel');var f=acrD('Fuel');return v>0&&f!==null ? f/v*100:null;}
 if(key==='bias') {v=acrD('BrakeBias');return v>0 ? (v<=1?v*100:v):null;}
 if(key==='maxrpm') {v=acrD('CarSettings_MaxRPM'); if(v>1000)return v;v=acrNum('DataCorePlugin.GameRawData.StaticInfo.MaxRpm');return v>1000?v:null;}
 if(key==='steer') {v=acrR('SteerAngle');return ACR_VERIFIED.steer&&v!==null ? v*ACR_VERIFIED.steerScale : null;}
 if(key==='gx'||key==='gy') {v=acrR(key==='gx'?'AccG01':'AccG03');return ACR_VERIFIED.g&&v!==null ? (key==='gx'?-v:v):null;}
 var m=/^(pressure|brakeTemp|tyreTemp|load|susp|slip)([1-4])$/.exec(key);
 if(m) {
  var i=Number(m[2]), suffix=['FrontLeft','FrontRight','RearLeft','RearRight'][i-1], n='0'+i;
  if(m[1]==='pressure') {v=acrD('TyrePressure'+suffix);u=String(acrProp('DataCorePlugin.GameData.TyrePressureUnit')).toLowerCase();var scale=u==='bar'?14.503773773:u==='kpa'?0.14503773773:u==='psi'?1:null;return v!==null&&scale!==null ? v*scale:null;}
  if(m[1]==='brakeTemp'||m[1]==='tyreTemp') {
   v=acrD((m[1]==='brakeTemp'?'BrakeTemperature':'TyreTemperature')+suffix);
   u=String(acrProp('DataCorePlugin.GameData.TemperatureUnit')).toLowerCase();
   var raw=acrR((m[1]==='brakeTemp'?'BrakeTemp':'TyreCoreTemperature')+n);
   return v!==null&&(v!==0||raw>0) ? (u.indexOf('fahren')>=0?(v-32)*5/9:v):null;
  }
  if(m[1]==='load') {v=acrR('WheelLoad'+n);return v===null?null:v/1000;}
  if(m[1]==='susp') {v=acrR('SuspensionTravel'+n);return v===null?null:v*1000;}
  if(m[1]==='slip') return acrR('WheelSlip'+n);
 }
 return null;
}
function acrText(key,digits) {var v=acrValue(key);return v===null||v===undefined?'—':(typeof v==='string'?v:Number(Number(v).toFixed(digits||0)).toFixed(digits||0));}
function acrGauge(key) {var v=acrValue(key);return v===null?0:Number(v);}
function acrRPMPercent() {var m=acrValue('maxrpm'),r=acrValue('rpm');return m>0&&r!==null?acrClamp(r/m*100,0,100):0;}
function acrName(key,fallback) {var s=acrState();if(!s.valid||s.stale)return fallback;var v=acrProp('DataCorePlugin.GameData.'+key);return v&&String(v).indexOf('\uFFFD')<0?String(v):fallback;}
function acrStatus() {var s=acrState();return !s.running?'等待遥测 · 启动 ACR 并进入赛段':!s.valid?'游戏已启动 · 等待赛段数据':s.paused?'已暂停':s.stale?'遥测暂未更新':'遥测已连接';}
function acrTime() {var s=acrState();if(!s.valid)return '—';var t=Math.floor(s.elapsed/1000);return ('0'+Math.floor(t/60)).slice(-2)+':'+('0'+t%60).slice(-2);}
function acrMap() {return ACR_VERIFIED.map && acrState().valid && acrProp('DataCorePlugin.GameData.MapAllowed')===true;}
function acrNight() {return String(acrProp('DataCorePlugin.DayNightMode')).toLowerCase()==='night';}
// Enabled only after current-install validation; see FIELD_MAP.md.
var ACR_VERIFIED={steer:true,steerScale:100,g:true,map:false};
// Visual temperature scale, not a vehicle operating window or alarm threshold.
var ACR_TYRE_SCALE={
 // Absolute display anchors, not optimal-temperature or damage limits.
 points:[[0,[69,150,255]],[15,[34,221,225]],[25,[67,229,142]],[35,[255,222,68]],[50,[255,150,53]],[65,[255,91,110]]]
};
function acrTyreColor(key) {
 var v=acrValue(key);if(v===null)return '#FF35404C';
 var p=ACR_TYRE_SCALE.points,lo=0;
 while(lo<p.length-2 && v>p[lo+1][0])lo++;
 var f=acrClamp((v-p[lo][0])/(p[lo+1][0]-p[lo][0]),0,1),s='#FF';
 for(var j=0;j<3;j++){var n=Math.round(p[lo][1][j]*(1-f)+p[lo+1][1][j]*f);s+=('0'+n.toString(16)).slice(-2);}
 return s.toUpperCase();
}

// Controls are gated by measured support, rather than interpreting placeholder zeros.
var ACR_CONTROL_SUPPORT={engine:true,ignition:true,starter:true,valve:false,absMode:true,tcMode:true,autoClutch:false,autoGear:false,engineMap:false,lights:false};
function acrMemoryControlsValid() {
 var age=acrNum('ACRControlsPlugin.AgeMs');
 return acrNum('ACRControlsPlugin.Valid')===1 && age!==null && age>=0 && age<=1500;
}
function acrControlSource() {return acrMemoryControlsValid()?(acrNum('ACRControlsPlugin.AutomaticLocator')===1?'菜单设置 / 自动定位':'菜单设置 / 内存 · 本次游戏'):'菜单设置 / 等待有效读取';}
function acrControlValue(key) {
 var s=acrState();if(!s.valid||s.stale||!ACR_CONTROL_SUPPORT[key])return null;
 if(key==='absMode'||key==='tcMode') return acrMemoryControlsValid()?acrNum('ACRControlsPlugin.'+(key==='absMode'?'ABS':'TCS')+'.Enabled'):null;
 var names={engine:'isEngineRunning',ignition:'ignitionOn',starter:'starterEngineOn'};
 return names[key]?acrR(names[key]):null;
}
function acrControlText(key) {
 var v=acrControlValue(key);if(v===null)return '—';
 if(key==='absMode'||key==='tcMode') {
  var level=acrNum('ACRControlsPlugin.'+(key==='absMode'?'ABS':'TCS')+'.Level');
  return level!==null&&level>=1&&level<=3?(v===1?'开启 · '+level.toFixed(0)+'档':'关闭'):'—';
 }
 if(key==='engine')return v===1?'运行':'停止';
 if(key==='starter')return v===1?'工作':'待机';
 return v===1?'开启':'关闭';
}
function acrControlColor(key) {var v=acrControlValue(key);return v===null?'#FF8092A5':v===1?'#FF44D7D5':'#FFFFC267';}



