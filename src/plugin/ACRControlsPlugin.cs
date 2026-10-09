using GameReaderCommon;
using SimHub.Plugins;
using System;
using System.IO;
using System.Threading;
using System.Windows.Media;
using Newtonsoft.Json;

namespace ACR.NativeControls
{
    [PluginDescription("ACR ABS/TCS菜单设置，当前版本自动定位，只读，失效清空")]
    [PluginAuthor("dxd")]
    [PluginName("ACR Settings Bridge")]
    public sealed class ACRControlsPlugin : IPlugin, IDataPlugin
    {
        public PluginManager PluginManager { get; set; }
        public ImageSource PictureIcon { get { return null; } }
        public string LeftMenuTitle { get { return "ACR Settings Bridge"; } }
        private volatile ControlSnapshot snapshot = ControlSnapshot.Missing("等待读取");
        private AutoControlMemoryReader reader;
        private Timer timer;
        private readonly object sync = new object();
        private readonly object pollSync = new object();
        private volatile string gateStatus = "等待 ACR";
        private long gateTicks;
        private string sessionKey;
        private string candidateKey;
        private DateTime candidateSince;
        private int generation, readerGeneration=-1;
        private double currentRpm, currentFuel;
        private string lastLogged;
        private DateTime lastDiagnostic=DateTime.MinValue;
        private string diagnosticPath;
        private volatile bool stopping;
        public ControlSnapshot Current { get { var status=gateStatus;if(status!=null)return ControlSnapshot.Missing(status);var s=snapshot; return s.Valid && (DateTime.UtcNow-s.TimestampUtc).TotalMilliseconds>1500 ? ControlSnapshot.Missing("读取已过期") : s; } }
        public void Init(PluginManager pluginManager)
        {
            PluginManager=pluginManager;
            var dir=Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"PluginsData","ACRSettingsBridge");
            Directory.CreateDirectory(dir);diagnosticPath=Path.Combine(dir,"latest.json");
            try { reader=new AutoControlMemoryReader(Path.Combine(dir,"auto-locator-profile.json")); }
            catch (Exception e) { snapshot=ControlSnapshot.Missing("缺少有效自动定位配置");SimHub.Logging.Current.Error("ACR Settings Bridge config: "+e.Message); }
            this.AttachDelegate("Valid", () => Current.Valid);
            this.AttachDelegate("AgeMs", () => (DateTime.UtcNow-snapshot.TimestampUtc).TotalMilliseconds);
            this.AttachDelegate("ABS.Enabled", () => Current.Valid ? (object)Current.AbsEnabled : null);
            this.AttachDelegate("ABS.Level", () => Current.Valid ? (object)Current.AbsLevel : null);
            this.AttachDelegate("TCS.Enabled", () => Current.Valid ? (object)Current.TcsEnabled : null);
            this.AttachDelegate("TCS.Level", () => Current.Valid ? (object)Current.TcsLevel : null);
            this.AttachDelegate("Status", () => Current.Status);
            this.AttachDelegate("SessionOnly", () => false);
            this.AttachDelegate("AutomaticLocator", () => true);
            timer=new Timer(Poll,null,100,100);
            SimHub.Logging.Current.Info("ACR Settings Bridge initialized (automatic UObject locator, read-only)");
        }
        public void DataUpdate(PluginManager pluginManager, ref GameData data)
        {
            // Only a gate on SimHub's data thread; actual reads run on a throttled worker.
            try
            {
                lock(sync)
                {
                    if (reader==null) return;
                    if (!data.GameRunning || !String.Equals(data.GameName,"AssettoCorsaRally",StringComparison.OrdinalIgnoreCase) || data.NewData==null)
                    {
                        if(sessionKey!=null || candidateKey!=null){generation++;sessionKey=candidateKey=null;}
                        gateStatus="等待 ACR";return;
                    }
                    string car=data.NewData.CarModel, track=data.NewData.TrackName;
                    string session=Convert.ToString(data.SessionId);
                    if (String.IsNullOrEmpty(car)||String.IsNullOrEmpty(track)||String.IsNullOrEmpty(session) || session=="00000000-0000-0000-0000-000000000000") { gateStatus="等待车辆和赛段身份";return; }
                    string key=session+"|"+car+"|"+track;
                    if (sessionKey!=key)
                    {
                        if (candidateKey!=key) { candidateKey=key;candidateSince=DateTime.UtcNow;generation++; }
                        if ((DateTime.UtcNow-candidateSince).TotalSeconds<1) { gateStatus="等待新车辆身份稳定";return; }
                        sessionKey=key;
                    }
                    currentRpm=data.NewData.Rpms;currentFuel=data.NewData.Fuel;
                    gateStatus=null;Interlocked.Exchange(ref gateTicks,DateTime.UtcNow.Ticks);
                }
            }
            catch { gateStatus="游戏数据不可用"; }
        }
        private void Poll(object ignored)
        {
            if (!Monitor.TryEnter(pollSync)) return;
            try
            {
                if (stopping) return;
                if (reader==null) return;
                string status,key;int currentGeneration;double rpm,fuel;long ticks;
                lock(sync){status=gateStatus;key=sessionKey;currentGeneration=generation;rpm=currentRpm;fuel=currentFuel;ticks=gateTicks;}
                if(currentGeneration!=readerGeneration){reader.ResetVehicle();readerGeneration=currentGeneration;}
                var result=status!=null ? ControlSnapshot.Missing(status) : (DateTime.UtcNow.Ticks-ticks>TimeSpan.FromSeconds(3).Ticks ? ControlSnapshot.Missing("游戏数据已过期") : reader.Read(rpm,fuel,()=>stopping||generation!=currentGeneration||gateStatus!=null));
                if(stopping)return;
                lock(sync){snapshot=generation==currentGeneration&&gateStatus==null?result:ControlSnapshot.Missing(gateStatus??"车辆已变化");}
                var s=snapshot;string summary=s.Status+"|"+s.Valid+"|"+s.AbsEnabled+"|"+s.AbsLevel+"|"+s.TcsEnabled+"|"+s.TcsLevel;
                if (summary!=lastLogged) { SimHub.Logging.Current.Info("ACR Settings Bridge: "+summary);lastLogged=summary; }
                if ((DateTime.UtcNow-lastDiagnostic).TotalSeconds>=1)
                {
                    var record=new { utc=DateTime.UtcNow, plugin="ACRControlsPlugin", valid=s.Valid, status=s.Status, abs_enabled=s.Valid?(bool?)s.AbsEnabled:null, abs_level=s.Valid?(int?)s.AbsLevel:null, tcs_enabled=s.Valid?(bool?)s.TcsEnabled:null, tcs_level=s.Valid?(int?)s.TcsLevel:null, session_only=false,automatic_locator=true,pid=reader.ProcessId,object_address=reader.ObjectAddress,locate_ms=reader.LastLocateMs,game_key=key };
                    // Small local diagnostic, once/sec. It is not the dashboard data transport.
                    File.WriteAllText(diagnosticPath,JsonConvert.SerializeObject(record,Formatting.Indented));lastDiagnostic=DateTime.UtcNow;
                }
            }
            catch (Exception e) { snapshot=ControlSnapshot.Missing("读取异常");SimHub.Logging.Current.Warn("ACR Settings Bridge: "+e.Message); }
            finally { Monitor.Exit(pollSync); }
        }
        public void End(PluginManager pluginManager)
        {
            stopping=true;if (timer!=null) timer.Dispose();
            lock(pollSync) { snapshot=ControlSnapshot.Missing("插件已停止");if(reader!=null) reader.Dispose(); }
        }
    }
}
