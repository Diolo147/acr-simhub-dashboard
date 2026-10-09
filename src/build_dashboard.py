"""Build an editable SimHub dashboard using native Dash Studio components.
Run with the user's embedded Python; no runtime Python dependency.
"""
import base64, copy, hashlib, io, json, pathlib, shutil, uuid, zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT=pathlib.Path(__file__).resolve().parents[1]
SIM=pathlib.Path(r'C:\Program Files (x86)\SimHub')
NAME='ACR Rally 21x9'
OUT=ROOT/'build'/NAME
OUT.mkdir(parents=True,exist_ok=True)
BG='#FF090D12'; PANEL='#FF111923'; LINE='#FF263442'; WHITE='#FFF1F5FA'; MUTED='#FF8092A5'; CYAN='#FF44D7D5'; AMBER='#FFFFC267'; RED='#FFFF6478'; BLUE='#FF739BFF'
items=[]; images=[]; resources={}; seq=0

def native(t,name,x,y,w,h,**kwargs):
 global seq
 seq+=1
 return dict({'$type':f'SimHub.Plugins.OutputPlugins.GraphicalDash.Models.{t}, SimHub.Plugins','Name':name,'Sid':seq,'Left':float(x),'Top':float(y),'Width':float(w),'Height':float(h),'Visible':True,'BackgroundColor':'#00FFFFFF','MinimumRefreshIntervalMS':100.0,'RenderingSkip':0},**kwargs)
def bind(o,prop,expr):
 o.setdefault('Bindings',{})[prop]={'Formula':{'Expression':expr,'Interpreter':1},'Mode':2,'TargetPropertyName':prop};return o
def add(o):items.append(o);return o
def text(name,label,x,y,w,h,size=24,color=WHITE,expr=None,align=0,font='Microsoft YaHei UI',outline=False):
 o=native('OutlinedTextItem' if outline else 'TextItem',name,x,y,w,h,Font=font,FontSize=float(size),FontWeight='Bold',FontStyle='Normal',Text=label,TextColor=color,HorizontalAlignment=align,VerticalAlignment=1,IsTextItem=True)
 if outline:o.update(StrokeColorEx='#FF162833',StrokeThickness=2,FillColorEx=color)
 if expr:bind(o,'Text',expr)
 return add(o)
def rect(name,x,y,w,h,color=PANEL):
 if name.endswith('Panel'):
  def frame(d):
   d.polygon([(0,14),(14,0),(w-28,0),(w,28),(w,h-14),(w-14,h),(0,h)],fill='#'+color[3:],outline='#2B4654',width=1)
   d.line([(0,47),(0,14),(14,0),(83,0)],fill='#44D7D5',width=3)
   d.line([(w-85,h-1),(w-14,h-1),(w-1,h-14),(w-1,h-41)],fill='#456778',width=2)
   for tx in range(w-120,w-35,12):d.line((tx,12,tx+5,18),fill='#365363',width=2)
  asset('frame_'+name,int(w),int(h),frame)
  return img(name,'frame_'+name,x,y,w,h)
 return add(native('RectangleItem',name,x,y,w,h,IsRectangleItem=True,BackgroundColor=color))
def gauge(name,key,x,y,w,h,color=CYAN,lo=0,hi=100):
 o=native('LinearGaugeItem',name,x,y,w,h,IsLinearGauge=True,GaugeOrientation=0,GaugeAlignment=0,AutoSize=False,GaugeColor=color,AlternateGaugeColor=color,UseAlternateStyle=False,Minimum=float(lo),Maximum=float(hi),Value=0.0,Steps=0.0,PAW=0.0,BackgroundColor='#FF24303D')
 bind(o,'Value','return '+key+';')
 import re
 field=re.search(r"acrGauge\('([^']+)'\)",key)
 bind(o,'Visible',"return acrValue('%s')!==null;"%field.group(1) if field else 'return acrState().valid && !acrState().stale;')
 return add(o)
def ellipse(name,x,y,w,h,color=LINE,fill='#00FFFFFF',thick=2):return add(native('EllipseItem',name,x,y,w,h,FillColor=fill,EllipseColor=color,EllipseThickness=float(thick)))
def asset(name,w,h,drawfn):
 im=Image.new('RGBA',(w,h));drawfn(ImageDraw.Draw(im));buf=io.BytesIO();im.save(buf,format='PNG');data=buf.getvalue();resources[name+'.png']=data
 images.append(dict(Name=name,Extension='.png',Modified=False,Optimized=True,Width=w,Height=h,Length=len(data),MD5=hashlib.md5(data).hexdigest()));return name
def img(name,assetname,x,y,w,h):return add(native('ImageItem',name,x,y,w,h,Image=assetname,AutoSize=False,AutoSizeScale=1.0))
def group_since(start,name,x,y,w,h):
 children=items[start:];del items[start:]
 return add(native('Layer',name,x,y,w,h,Group=True,Childrens=children))
def expr(key,d=0):return "return acrText('%s',%s);"%(key,d)

# Original bitmap assets drawn from geometric primitives; telemetry stays native.
def draw_tread(d):
 # Three equal stripes share one measured core temperature; no fake thermal zones.
 d.rounded_rectangle((7,4,61,136),radius=7,outline='#8B9DA8',width=1)
 for x in [25,43]:d.line((x,5,x,135),fill='#101010',width=3)
 for pts in [[(8,5),(14,5),(8,11)],[(60,5),(54,5),(60,11)],[(8,135),(14,135),(8,129)],[(60,135),(54,135),(60,129)]]:
  d.polygon(pts,fill='#101010')
asset('rally_tread',68,140,draw_tread)
def draw_hud(d):
 for x,y,sx,sy in [(8,8,1,1),(998,8,-1,1),(8,548,1,-1),(998,548,-1,-1)]:
  d.line([(x,y+38*sy),(x,y),(x+54*sx,y)],fill='#44D7D5',width=3)
asset('drive_hud',1008,560,draw_hud)
def draw_car(d):
 d.polygon([(64,9),(119,9),(139,43),(148,96),(143,152),(126,187),(58,187),(40,152),(35,96),(43,43)],fill='#101F29',outline='#44D7D5',width=2)
 d.polygon([(60,59),(123,59),(130,99),(52,99)],fill='#233D4A',outline='#8092A5')
 d.polygon([(52,121),(130,121),(124,154),(59,154)],fill='#182F3D',outline='#496578')
 for x in [25,144]:
  for y in [45,128]:d.rounded_rectangle((x,y,x+15,y+39),radius=4,fill='#253A48',outline='#739BFF',width=2)
 d.line((92,15,92,183),fill='#284C59',width=1)
asset('rally_silhouette',184,200,draw_car)

# Header and hierarchy.
rect('HeaderAccent',24,27,5,39,CYAN)
text('Title','ACR / RALLY',46,22,330,50,32)
text('Car','等待车辆',388,23,730,48,26,MUTED,"return acrName('CarModel','等待车辆');")
text('Track','赛段信息待连接',1140,23,840,48,24,MUTED,"return acrName('TrackName','赛段信息待连接');")
button=native('ButtonItem','DayNightButton',2286,26,246,43,IsEnabled=True,SimulateKey=False,TriggerAction='DataCorePlugin.ToggleDayNightMode',TriggerSimHubInputName='',ButtonStyle=0,PressedOpacity=65,BackgroundColor=LINE)
button['Childrens']=[native('TextItem','DayNightLabel',0,0,246,43,Font='Microsoft YaHei UI',FontSize=20.0,FontWeight='Bold',Text='日间 / 夜间',TextColor=WHITE,HorizontalAlignment=1,VerticalAlignment=1)]
add(button)

# Full-width RPM bar and genuinely native shift-light components.
rect('RPMPanel',24,88,2512,96)
text('RPMLabel','ENGINE / RPM',44,94,220,29,19,MUTED)
text('Redline','上限 —',2170,94,338,29,19,MUTED,"var v=acrValue('maxrpm');return v>0?'转速上限 '+v.toFixed(0):'转速上限未提供';",2)
gauge('RPMProgress','acrRPMPercent()',44,151,2468,13,CYAN)
for j in range(20):
 color=CYAN if j<12 else AMBER if j<17 else RED
 on=asset('led_on_'+str(j),108,18,lambda d,c=color:d.rounded_rectangle((0,0,107,17),radius=3,fill='#'+c[3:]))
 off=asset('led_off_'+str(j),108,18,lambda d:d.rounded_rectangle((0,0,107,17),radius=3,fill='#273341'))
 led=native('ShiftLightItem','ShiftLED_%02d'%j,284+j*91,102,81,23,IsToggleImage=True,ShiftLightMode=0,LedNumber=j+1,TotalLeds=20,RedlineBlink=False,PitlimiterBlink=False,OnImage=on,OffImage=off,AutoSize=False,StackImagesWhenOn=False,Value=False)
 bind(led,'Value','return acrState().live && acrRPMPercent()>='+str(50+j*2.5)+';');add(led)
for j in range(11):text('RPMTick'+str(j),str(j*10),44+j*244,166,34,15,11,MUTED,align=1)

# Left: honest drive timer + conditional native map with fallback summary.
rect('SessionPanel',24,200,560,560)
text('SessionTitle','01  /  SESSION',48,214,460,33,23,MUTED)
text('TimerLabel','本次驾驶计时',48,258,480,30,23,MUTED)
text('DriveTimer','—',48,294,480,94,68,WHITE,'return acrTime();',font='Bahnschrift')
text('TimerNote','移动后累计 · 暂停不计时',48,389,480,28,18,MUTED)
rect('LeftDivider',48,433,512,2,LINE)
fallback_start=len(items)
text('SummaryTitle','驾驶摘要',48,454,470,32,23,CYAN)
text('PeakLabel','本次最高速度',48,506,300,30,22,MUTED)
text('PeakValue','—',48,540,340,75,53,WHITE,"var s=acrState();return s.valid?s.peak.toFixed(0):'—';",font='Bahnschrift')
text('PeakUnit','km/h',413,568,124,36,24,MUTED,align=2)
text('MapNote','地图等待有效路线与坐标',48,658,486,29,21,MUTED)
text('MapNote2','无虚构路线 / 无估算剩余里程',48,700,486,25,17,MUTED)
fb=group_since(fallback_start,'SessionFallback',24,440,560,310);bind(fb,'Visible','return !acrMap();')
samples=json.loads((ROOT/'work/component_samples.json').read_text(encoding='utf-8'))
mapitem=copy.deepcopy(samples['GeneratedMapItem']);mapitem.update(Name='ACRDynamicMap',Left=48.0,Top=454.0,Width=512.0,Height=275.0,Visible=False,BaseMapScale=1.1,MinimumRefreshIntervalMS=100.0)
bind(mapitem,'Visible','return acrMap();');add(mapitem)

# Center: large driving information with restrained depth.
gradient=copy.deepcopy(samples['GradientItem'])
gradient={k:v for k,v in gradient.items() if k not in ['$id','Bindings','BindingsFast','BorderStyle','Id']}
gradient.update(Name='DrivingGradient',Left=600.0,Top=200.0,Width=1008.0,Height=560.0,Opacity=100.0)
gradient['Color']['LinearGradientBrush']['LinearGradientBrush.GradientStops']['GradientStop']=[{'@Color':'#FF13242D','@Offset':'0'},{'@Color':'#FF101820','@Offset':'1'}]
add(gradient)
img('DriveHUD','drive_hud',600,200,1008,560)
text('DrivingTitle','02  /  DRIVE',628,214,500,33,23,MUTED)
text('GearCaption','GEAR',642,269,330,38,28,CYAN,align=1)
text('Gear','—',630,298,360,314,240,WHITE,expr('gear'),align=1,font='Bahnschrift',outline=True)
rect('DriveVerticalRule',1007,280,2,330,LINE)
text('Speed','—',1031,305,542,174,128,WHITE,expr('speed'),align=1,font='Bahnschrift')
text('SpeedUnit','km/h',1043,476,506,44,34,MUTED,align=1)
text('RpmNumber','—',1033,535,370,68,48,CYAN,expr('rpm'),align=2,font='Bahnschrift')
text('RpmUnit','rpm',1419,553,132,42,25,MUTED)

# Four wheels: reusable native groups, not bitmap panels.
rect('WheelsPanel',1624,200,912,560)
text('WheelsTitle','03  /  FOUR CORNERS',1648,214,630,33,23,MUTED)
text('WheelUnits','psi  ·  °C  ·  mm  ·  kN',2150,217,354,28,19,MUTED,align=2)
for i,(code,x,y) in enumerate([('FL / 左前',1648,260),('FR / 右前',2100,260),('RL / 左后',1648,498),('RR / 右后',2100,498)],1):
 start=len(items);rect('WheelBg'+str(i),x,y,412,222,'#FF17222D')
 text('WheelName'+str(i),code,x+16,y+8,370,28,21,CYAN)
 fill=rect('TyreTint'+str(i),x+24,y+46,52,114,'#FF35404C');bind(fill,'BackgroundColor',"return acrTyreColor('tyreTemp%d');"%i)
 img('TyreTread'+str(i),'rally_tread',x+16,y+41,68,124)
 text('CoreLabel'+str(i),'核心 °C',x+5,y+169,90,21,13,MUTED,align=1)
 text('TyreTemp'+str(i),'—',x+2,y+188,96,28,21,WHITE,expr('tyreTemp'+str(i),1),align=1,font='Bahnschrift')
 text('PressureLabel'+str(i),'胎压',x+104,y+48,52,26,18,MUTED)
 text('Pressure'+str(i),'—',x+152,y+41,74,43,29,WHITE,expr('pressure'+str(i),1),align=2,font='Bahnschrift')
 text('BrakeLabel'+str(i),'刹温',x+232,y+48,64,26,20,MUTED)
 text('BrakeTemp'+str(i),'—',x+287,y+41,105,43,34,AMBER,expr('brakeTemp'+str(i)),align=2,font='Bahnschrift')
 for key,label,dy,color,dig in [('susp','悬挂',99,CYAN,1),('load','载荷',140,BLUE,2)]:
  text(key+'Label'+str(i),label,x+104,y+dy-3,52,25,18,MUTED)
  gauge(key+'Bar'+str(i),"acrGauge('%s%d')"%(key,i),x+165,y+dy+4,104,10,color,-150 if key=='susp' else 0,150 if key=='susp' else 15)
  text(key+'Value'+str(i),'—',x+283,y+dy-9,109,33,24,WHITE,expr(key+str(i),dig),align=2,font='Bahnschrift')
 text('SlipLabel'+str(i),'滑移原值',x+104,y+184,150,25,17,MUTED)
 text('Slip'+str(i),'—',x+323,y+180,68,32,22,MUTED,expr('slip'+str(i),1),align=2,font='Bahnschrift')
 group_since(start,'WheelWidget_'+str(i),x,y,412,222)
text('WheelNote','胎温色谱 15–100°C：蓝→青→橙→红 · 仅表示测量值，非最佳温度/告警',1648,731,865,22,15,MUTED)

# Inputs, using native arc to show steering and normal gauges for pedals.
rect('InputsPanel',24,776,560,240)
text('InputsTitle','04  /  INPUTS',48,788,350,30,21,MUTED)
for key,label,y,color in [('throttle','油门',838,CYAN),('brake','刹车',887,RED),('clutch','离合*',936,BLUE)]:
 text(key+'Label',label,48,y,70,28,20,MUTED)
 gauge(key+'Gauge',"acrGauge('%s')"%key,127,y+8,249,15,color)
 text(key+'Value','—',382,y-4,75,36,23,WHITE,expr(key),align=2,font='Bahnschrift')
arc=native('ArcGaugeItem','SteeringArc',460,838,98,98,ArcThickness=5.0,SweepMinValue=-100.0,SweepMaxValue=100.0,Value=0.0,SweepStartAngle=-135.0,SweepAngle=270.0,SweepAngleCounterClockWise=False,SweepBackgroundColor=LINE,SweepColor=CYAN,UseEllipse=False,CompleteCircleEnabled=False)
bind(arc,'Value',"return acrGauge('steer');");bind(arc,'Visible',"return acrValue('steer')!==null;");add(arc)
text('SteeringValue','—',469,864,80,43,28,WHITE,expr('steer'),align=1,font='Bahnschrift')
text('SteeringLabel','转向 %',454,939,115,29,17,MUTED,align=1)
text('SteeringNote','待校准',450,975,120,24,16,MUTED,"return ACR_VERIFIED.steer?'已校准':'待校准';",align=1)

# Genuine Chart components: 150 samples at 100ms, separate speed scale.
rect('ChartsPanel',600,776,1008,240)
text('ChartsTitle','05  /  LAST 15 SECONDS',628,788,500,30,21,MUTED)
text('ChartsLegend','油门  /  刹车  /  离合',1190,788,388,28,19,MUTED,align=2)
for y in [838,891,944,990]:rect('ChartGrid'+str(y),654,y,902,1,LINE)
text('PedalAxis','100%',619,828, sixty:=60,24,13,MUTED)
text('SpeedAxis','km/h',619,960,60,24,13,MUTED)
for key,col,y,h,maxval in [('throttle',CYAN,825,90,100),('brake',RED,825,90,100),('clutch',BLUE,825,90,100),('speed',WHITE,922,78,240)]:
 c=native('ChartItem',key+'History',671,y,891,h,ChartEnabled=True,ChartSuspended=False,CurrentValue=0.0,Minimum=0.0,Maximum=float(maxval),UseMinimum=True,UseMaximum=key!='speed',LineColor=col,LineTickness=2,PointsCount=150.0)
 bind(c,'CurrentValue',"return acrGauge('%s');"%key);bind(c,'ChartEnabled','return acrState().live;');add(c)
 bind(c,'Visible','return acrState().valid && !acrState().stale;')
text('ChartWaiting','进入赛段后显示实时曲线',803,875,670,39,26,MUTED,align=1)
bind(items[-1],'Visible','return !acrState().valid;')

# G-ball based on bundled Accelerometer, plus engine readouts.
rect('EnginePanel',1624,776,912,240)
text('EngineTitle','06  /  VEHICLE',1648,788,440,30,21,MUTED)
ellipse('GOuter',1651,834,160,160)
ellipse('GInner',1691,874,80,80)
rect('GHorizontal',1651,913,160,1,LINE);rect('GVertical',1730,834,1,160,LINE)
dot=ellipse('GBall',1723,906,15,15,CYAN,CYAN,0)
bind(dot,'Left',"return 1723+acrClamp(acrGauge('gx'),-2,2)*36;");bind(dot,'Top',"return 906-acrClamp(acrGauge('gy'),-2,2)*36;");bind(dot,'Visible',"return acrValue('gx')!==null;")
text('GWaiting','—',1675,893,112,36,20,MUTED,align=1);bind(items[-1],'Visible',"return acrValue('gx')===null;")
text('GLabel','横 / 纵 G',1830,840,110,27,20,MUTED)
text('GValue','—',1820,879,143,45,22,CYAN,"return acrText('gx',2)+' / '+acrText('gy',2);",align=1)
for key,label,x,w,d in [('water','水温 °C',1980,180,0),('fuel','燃油 L',2170,160,1),('bias','前制动 %',2342,166,1)]:
 text(key+'Title',label,x,835,w,29,20,MUTED,align=1)
 text(key+'Number','—',x,881,w,61,43,WHITE,expr(key,d),align=1,font='Bahnschrift')
text('FuelHint','燃油量不用于推算续航',1979,966,510,26,18,MUTED,align=1)

# Standby icon uses native ToggleImage, meaningful image indication.
asset('link_on',36,36,lambda d:d.ellipse((7,7,29,29),fill='#44D7D5'))
asset('link_off',36,36,lambda d:d.ellipse((7,7,29,29),outline='#8092A5',width=3))
status=native('ToggleImageItem','ConnectionIcon',24,1026,36,36,IsToggleImage=True,Value=False,OnImage='link_on',OffImage='link_off',StackImagesWhenOn=False,AutoSize=False)
bind(status,'Value','return acrState().live;');add(status)
text('Footer','ACR RALLY 21x9  /  1.4',64,1033,570,24,16,MUTED)
text('TelemetryStatus','等待遥测',446,1029,645,28,17,CYAN,'return acrStatus();')
text('FooterData','— 未提供 · 离合* 为 SimHub 原值，方向待验证 · 待校准字段不参与告警',1094,1033,1418,24,17,MUTED,align=2)
# Screen dimmer is a native translucent rectangle; Day/Night button is above it.
night=rect('NightDimmer',0,78,2560,944,'#65000000');bind(night,'Visible','return acrNight();')

exec((ROOT/'src/cockpit_layout.py').read_text(encoding='utf-8-sig'))

# Copied native samples carry editor identifiers; assign unique IDs recursively.
def normalize_components(children):
 global seq
 for o in children:
  seq+=1;o['Sid']=seq
  for key in ['$id','BindingsFast','Id']:o.pop(key,None)
  if 'Childrens' in o:normalize_components(o['Childrens'])
seq=0
normalize_components(items)

dashboard=dict(Version=2,Id='e5c9e579-1841-4d55-9d37-b0a450fe7801',BaseHeight=1080,BaseWidth=2560,BackgroundColor=BG,
 Screens=[dict(Name='Rally',InGameScreen=True,IdleScreen=True,PitScreen=True,ScreenId='dba16b56-661d-42b0-98d0-a6b7f92c4bf1',AllowOverlays=True,BackgroundColor=BG,Items=items)],
 Images=images,SnapToGrid=True,GridSize=8,ShowOnScreenControls=True,IsOverlay=False,EnableClickThroughOverlay=False,EnableOnDashboardMessaging=True,UseStrictJSIsolation=False,ShowInTaskBar=True,
 Metadata=dict(Title=NAME,Author='dxd',Description='原生 ACR 单页拉力仪表 · 2560×1080',DashboardVersion='2.5',ScreenCount=1.0,InGameScreensIndexs=[0],IdleScreensIndexs=[0],PitScreensIndexs=[0],MainPreviewIndex=0,IsOverlay=False,Width=2560.0,Height=1080.0,MetadataVersion=2.0,EnableOnDashboardMessaging=True))
(OUT/(NAME+'.djson')).write_text(json.dumps(dashboard,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/(NAME+'.djson.metadata')).write_text(json.dumps(dashboard['Metadata'],ensure_ascii=False),encoding='utf-8')
with zipfile.ZipFile(OUT/(NAME+'.djson.ressources'),'w',zipfile.ZIP_DEFLATED) as z:
 for n,data in resources.items():z.writestr(n,data)
(OUT/'JavascriptExtensions').mkdir(exist_ok=True)
shutil.copy2(ROOT/'src/acr.js',OUT/'JavascriptExtensions/acr.js')
print('Built',OUT,'components',seq,'native types',len(set(x['$type'] for x in items)))









