"""Grouped wheel display and validated ACR vehicle status area (v2.5)."""
BG='#FF050505'
for o in items:
 if o['Name'].endswith('Panel'):
  o['$type']='SimHub.Plugins.OutputPlugins.GraphicalDash.Models.RectangleItem, SimHub.Plugins'
  o.update(BackgroundColor='#FF080808',IsRectangleItem=True);o.pop('Image',None)
remove={'SessionPanel','SessionTitle','TimerNote','LeftDivider','SessionFallback','ACRDynamicMap','WheelsTitle','WheelUnits','WheelNote','DrivingGradient','DriveHUD','DrivingTitle','GearCaption','DriveVerticalRule','TimerLabel','DriveTimer','EngineTitle','ChartsTitle','InputsTitle'}
items[:]=[o for o in items if o['Name'] not in remove]
for o in items:
 n=o['Name']
 if n=='Gear':
  o.update(Left=620.,Top=231.,Width=382.,Height=330.,FontSize=270.,TextColor='#FFFFD53D')
  o['$type']='SimHub.Plugins.OutputPlugins.GraphicalDash.Models.TextItem, SimHub.Plugins'
 if n=='Speed':o.update(Left=1025.,Top=282.,Width=550.,Height=175.,FontSize=140.)
 if n=='SpeedUnit':o.update(Left=1090.,Top=468.,Width=419.,Height=43.,FontSize=30.)
 if n=='RpmNumber':o.update(Left=1040.,Top=545.,Width=349.,Height=62.,FontSize=49.)
 if n=='RpmUnit':o.update(Left=1410.,Top=560.,Width=148.,Height=38.)
 if n=='RPMLabel':o.update(Text='RPM / %',TextColor='#FFFFD53D')
 if n in ['InputsPanel','ChartsPanel','EnginePanel']:o['BackgroundColor']='#FF080808'
 if n=='FuelHint':o['Text']='测量值 · 未提供显示 —'
 if n=='Footer':o['Text']='ACR / RALLY 21:9 · 2.5'
 if n.startswith('WheelWidget_'):
  for c in o['Childrens']:
   if c['Name'].startswith('WheelName'):c['TextColor']='#FFFFD53D'
   if c['Name'].startswith('WheelBg'):c['BackgroundColor']='#FF101010'
# A grouped 2x2 wheel block preserves FL/FR/RL/RR physical placement.
rect('WheelRail',1624,200,912,3,'#FFFFD53D')
text('WheelsRole','四轮状态 / TYRES',1648,211,460,32,23,'#FFFFD53D')
text('WheelUnits','psi · °C · mm · kN',2116,213,390,29,19,MUTED,align=2)
text('WheelSupportNote','单值核心胎温色谱 · 无分层温度 / 最佳温度 / 磨损结论',1648,731,865,23,16,MUTED)
rect('CenterRail',600,200,1008,3,'#FF44D7D5')
rect('CenterInfoRule',628,643,954,1,'#FF404040')
text('GearRole','GEAR',643,212,330,36,23,MUTED,align=1)
text('SpeedRole','SPEED',1025,212,550,36,23,MUTED,align=1)
text('TimerRole','本次驾驶',628,660,365,29,20,MUTED)
text('DriveTimer','—',628,695,382,53,43,WHITE,'return acrTime();',font='Bahnschrift')
text('PeakRole','最高速度 / km/h',1110,660,447,29,20,MUTED,align=2)
text('PeakValue','—',1190,695,365,53,43,WHITE,"var s=acrState();return s.valid?s.peak.toFixed(0):'—';",align=2,font='Bahnschrift')
text('InputsRole','驾驶输入',48,788,430,30,21,'#FFFFD53D')
text('HistoryRole','操作 / 最近 15 秒',628,788,500,30,21,'#FFFFD53D')
text('VehicleRole','车辆测量',1648,788,440,30,21,'#FFFFD53D')
# Left side: engine state, controls and ambient conditions.
rect('VehicleStateSurface',24,200,560,560,'#FF080808')
rect('StateRail',24,200,560,3,'#FFFFD53D')
text('VehicleStateTitle','车辆控制 / STATUS',48,211,487,33,23,'#FFFFD53D')
for key,label,x in [('engine','发动机',48),('ignition','点火',220),('starter','启动机',392)]:
 rect(key+'StatusBg',x,257,158,78,'#FF141414')
 text(key+'StatusLabel',label,x+12,260,134,26,17,MUTED)
 text(key+'StatusText','—',x+12,290,134,33,24,WHITE,"return acrControlText('%s');"%key,align=1)
 bind(items[-1],'TextColor',"return acrControlColor('%s');"%key)
text('SettingsCaption','菜单设置 / 等待有效读取',48,350,481,29,18,MUTED,'return acrControlSource();')
rows=[('absMode','ABS 模式 / 档位'),('tcMode','TCS 模式 / 档位'),('engineMap','发动机曲线'),('lights','灯光控制')]
for i,(key,label) in enumerate(rows):
 y=397+i*57
 if i%2==0:rect(key+'RowBg',48,y,512,45,'#FF121212')
 text(key+'Label',label,59,y+5,276,35,21,MUTED)
 text(key+'Value','—',341,y+5,202,35,22,WHITE,"return acrControlText('%s');"%key,align=2)
 if key in ('absMode','tcMode'):bind(items[-1],'TextColor',"return acrControlColor('%s');"%key)
rect('EnvironmentRule',48,655,512,1,'#FF404040')
for key,label,x in [('air','气温 °C',48),('road','路温 °C',220)]:
 text(key+'Label',label,x,670,158,27,18,MUTED)
 text(key+'Value','—',x,700,158,43,32,WHITE,expr(key,1),font='Bahnschrift')
text('WeatherLabel','天气 / 时刻',392,670,158,27,18,MUTED)
text('WeatherValue','未输出',392,706,158,29,20,MUTED)
# Keep the dimmer above every component added in this layout.
night_item=next(o for o in items if o['Name']=='NightDimmer');items.remove(night_item);items.append(night_item)


