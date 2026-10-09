// Render an honest static view of the recorded SimHub road snapshot.
const fs=require('fs'),vm=require('vm');
const root=require('path').resolve(__dirname,'..')+'/';
const catalogFile=fs.existsSync(root+'work/live-catalog.json')?'work/live-catalog.json':'work/fixtures/live-catalog.json';
const catalog=JSON.parse(fs.readFileSync(root+catalogFile,'utf8'));
const props=Object.fromEntries(catalog.properties.map(p=>[p.name,p.value]));

// Preview-only standard-property fixtures derived from measured shared memory.
// This is not a live SimHub property export and must not change dashboard bindings.
const sample=JSON.parse(fs.readFileSync(root+'work/current-status-preview.json','utf8'));
const ph=sample.physics, st=sample.static;
for(const n of Object.keys(props))if(n.startsWith('DataCorePlugin.GameData.'))delete props[n];
const setD=(k,v)=>props['DataCorePlugin.GameData.'+k]=v;
const setR=(k,v)=>props['DataCorePlugin.GameRawData.Physics.'+k]=v;
props['DataCorePlugin.GameRunning']=true;props['DataCorePlugin.CurrentGame']='AssettoCorsaRally';props['DataCorePlugin.GamePaused']=false;
for(const [k,v] of Object.entries({SpeedKmh:ph.speedKmh,Rpms:ph.rpm,Gear:ph.gear===0?'R':ph.gear===1?'N':String(ph.gear-1),Throttle:ph.gas*100,Brake:ph.brake*100,Clutch:(1-ph.clutch)*100,Fuel:ph.fuel,WaterTemperature:ph.waterTemp-273.15,BrakeBias:ph.brakeBias*100,CarModel:st.carModel,TrackName:st.track,TyrePressureUnit:'Psi',TemperatureUnit:'Celcius'}))setD(k,v);
for(const [k,v] of Object.entries({PacketId:ph.packetId,SteerAngle:ph.steerAngle,AccG01:ph.accG[0],AccG03:ph.accG[2],AirTemp:ph.airTemp,RoadTemp:ph.roadTemp,ignitionOn:ph.ignitionOn,isEngineRunning:ph.isEngineRunning,starterEngineOn:ph.starterEngineOn}))setR(k,v);
props['DataCorePlugin.GameRawData.StaticInfo.MaxRpm']=null;
const controls=JSON.parse(fs.readFileSync(root+'work/controls-bridge-live.json','utf8'));
props['ACRControlsPlugin.Valid']=controls.valid;
props['ACRControlsPlugin.AutomaticLocator']=controls.automatic_locator===true;
props['ACRControlsPlugin.AgeMs']=0; // Static fixture evaluated at its capture time.
for(const [k,v] of Object.entries({'ABS.Enabled':controls.abs_enabled,'ABS.Level':controls.abs_level,'TCS.Enabled':controls.tcs_enabled,'TCS.Level':controls.tcs_level}))props['ACRControlsPlugin.'+k]=v;
for(let i=0;i<4;i++){
 const suffix=['FrontLeft','FrontRight','RearLeft','RearRight'][i],n='0'+(i+1);
 setD('TyrePressure'+suffix,ph.wheelPressure[i]);setD('BrakeTemperature'+suffix,ph.brakeTemp[i]-273.15);setD('TyreTemperature'+suffix,ph.tyreCoreTemp[i]-273.15);
 setR('WheelLoad'+n,ph.wheelLoad[i]);setR('SuspensionTravel'+n,ph.suspensionTravel[i]);setR('WheelSlip'+n,ph.wheelSlip[i]);setR('BrakeTemp'+n,ph.brakeTemp[i]);setR('TyreCoreTemperature'+n,ph.tyreCoreTemp[i]);
}

const ctx=vm.createContext({root:{},$prop:n=>props[n],Date:{now:()=>10000}});
vm.runInContext(fs.readFileSync(root+'src/acr.js','utf8'),ctx);
const dash=JSON.parse(fs.readFileSync(root+'build/ACR Rally 21x9/ACR Rally 21x9.djson','utf8'));
function apply(items) {for(const item of items) {
 for(const [key,b] of Object.entries(item.Bindings||{})) item[key]=vm.runInContext('(function(){'+b.Formula.Expression+'})()',ctx);
 delete item.Bindings;
 if(item.$type.includes('ChartItem')) {item.Visible=false;item.ChartEnabled=false;}
 if(item.Name==='ChartWaiting') {item.Visible=true;item.Text='实时趋势仅在运行时生成';}
 if(item.Name==='FooterData') item.Text='静态预览 · '+new Date(sample.time*1000).toLocaleDateString('sv-SE')+' 共享内存实测 · 趋势仅运行时生成';
 if(item.Childrens)apply(item.Childrens);
}}
apply(dash.Screens[0].Items);
fs.writeFileSync(root+'work/preview.djson',JSON.stringify(dash,null,2));

