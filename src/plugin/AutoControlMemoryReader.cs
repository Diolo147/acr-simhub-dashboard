using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;

namespace ACR.NativeControls
{
    public sealed class LocatorProfile
    {
        public string mode, image, sha256, gobjects_rva, state_vtable_rva;
        public uint pe_timestamp, image_size;
        public int state_anchor_offset;
        public int[] observed_level_indices;
    }
    // All addresses are resolved from the current process's image base and object
    // registry. Never use a previous PID, heap address, car or menu selection.
    public sealed class AutoControlMemoryReader : IDisposable
    {
        private readonly LocatorProfile profile;
        private readonly ulong registryRva, vtableRva;
        private IntPtr handle;
        private int pid, index, serial;
        private ulong born, imageBase, owner, ownerClass;
        private DateTime nextConnect, nextLocate;
        private string verifiedHashPath;
        private long verifiedHashSize, verifiedHashWrite;
        private bool hashMatches;
        private string failure="等待 ACR";
        public int ProcessId { get { return pid; } }
        public string ObjectAddress { get { return owner==0?null:"0x"+owner.ToString("x"); } }
        public double LastLocateMs { get; private set; }
        [DllImport("kernel32.dll",SetLastError=true)] private static extern IntPtr OpenProcess(uint access,bool inherit,int pid);
        [DllImport("kernel32.dll")] private static extern bool CloseHandle(IntPtr h);
        [DllImport("kernel32.dll")] private static extern bool GetExitCodeProcess(IntPtr h,out uint code);
        [DllImport("kernel32.dll")] private static extern bool GetProcessTimes(IntPtr h,out ulong created,out ulong exited,out ulong kernel,out ulong user);
        [DllImport("kernel32.dll",CharSet=CharSet.Unicode)] private static extern bool QueryFullProcessImageName(IntPtr h,uint flags,StringBuilder name,ref uint size);
        [DllImport("kernel32.dll")] private static extern bool ReadProcessMemory(IntPtr h,IntPtr address,[Out] byte[] bytes,UIntPtr size,out UIntPtr read);
        [DllImport("ntdll.dll")] private static extern int NtWow64ReadVirtualMemory64(IntPtr h,ulong address,[Out] byte[] bytes,ulong size,out ulong read);
        [DllImport("ntdll.dll")] private static extern int NtWow64QueryInformationProcess64(IntPtr h,int info,[Out] byte[] bytes,int size,out int read);
        [DllImport("ntdll.dll")] private static extern int NtQueryInformationProcess(IntPtr h,int info,[Out] byte[] bytes,int size,out int read);
        public AutoControlMemoryReader(string config)
        {
            profile=JsonConvert.DeserializeObject<LocatorProfile>(File.ReadAllText(config));
            if(profile==null || profile.mode!="automatic-uobject" || Path.GetFileName(profile.image).ToLowerInvariant()!="acr.exe" || profile.sha256==null || profile.sha256.Length!=64 || profile.state_anchor_offset!=252 || profile.observed_level_indices==null || profile.observed_level_indices.Length==0)throw new InvalidDataException("无有效自动定位配置");
            registryRva=ParseAddress(profile.gobjects_rva);vtableRva=ParseAddress(profile.state_vtable_rva);
            if(registryRva+32>=profile.image_size || vtableRva>=profile.image_size)throw new InvalidDataException("定位偏移越界");
        }
        private static ulong ParseAddress(string s) { return ulong.Parse(s.StartsWith("0x")?s.Substring(2):s,NumberStyles.HexNumber); }
        private static bool Pointer(ulong p) { return p>=0x10000 && p<0x7ffffffff000; }
        private bool ReadBytes(ulong address,byte[] bytes)
        {
            if(!Pointer(address) || bytes.Length==0 || address+(ulong)bytes.Length>=0x7fffffffffff)return false;
            if(IntPtr.Size==4) { ulong n;return NtWow64ReadVirtualMemory64(handle,address,bytes,(ulong)bytes.Length,out n)==0 && n==(ulong)bytes.Length; }
            UIntPtr got;return ReadProcessMemory(handle,new IntPtr((long)address),bytes,new UIntPtr((uint)bytes.Length),out got) && got.ToUInt64()==(ulong)bytes.Length;
        }
        private bool Identity()
        {
            uint code;ulong created,exited,kernel,user;
            return handle!=IntPtr.Zero && GetExitCodeProcess(handle,out code) && code==259 && GetProcessTimes(handle,out created,out exited,out kernel,out user) && created==born;
        }
        private bool VerifyHash(string path)
        {
            var info=new FileInfo(path);
            if(verifiedHashPath!=path || verifiedHashSize!=info.Length || verifiedHashWrite!=info.LastWriteTimeUtc.Ticks)
            {
                using(var input=File.OpenRead(path))using(var hash=SHA256.Create())hashMatches=String.Equals(BitConverter.ToString(hash.ComputeHash(input)).Replace("-",""),profile.sha256,StringComparison.OrdinalIgnoreCase);
                verifiedHashPath=path;verifiedHashSize=info.Length;verifiedHashWrite=info.LastWriteTimeUtc.Ticks;
            }
            return hashMatches;
        }
        private bool Connect()
        {
            if(Identity())return true;
            Disconnect();
            if(DateTime.UtcNow<nextConnect)return false;
            nextConnect=DateTime.UtcNow.AddSeconds(1);
            var processes=Process.GetProcessesByName("acr");
            try
            {
                if(processes.Length!=1){failure=processes.Length==0?"等待 ACR":"存在多个 ACR 进程";return false;}
                pid=processes[0].Id;handle=OpenProcess(0x410,false,pid);
                var name=new StringBuilder(32768);uint n=(uint)name.Capacity;ulong exit,kernel,user;
                if(handle==IntPtr.Zero || !QueryFullProcessImageName(handle,0,name,ref n) || !String.Equals(name.ToString(),profile.image,StringComparison.OrdinalIgnoreCase) || !GetProcessTimes(handle,out born,out exit,out kernel,out user)){failure="无法核对 ACR 进程";Disconnect();return false;}
                if(!VerifyHash(name.ToString())){failure="游戏版本未适配";Disconnect();return false;}
                var basic=new byte[48];int got;
                int result=IntPtr.Size==4?NtWow64QueryInformationProcess64(handle,0,basic,48,out got):NtQueryInformationProcess(handle,0,basic,48,out got);
                if(result!=0 || got!=48){failure="无法读取进程入口";Disconnect();return false;}
                ulong peb=BitConverter.ToUInt64(basic,8);var baseBytes=new byte[8];
                if(!ReadBytes(peb+16,baseBytes)){failure="进程入口失效";Disconnect();return false;}
                imageBase=BitConverter.ToUInt64(baseBytes,0);var header=new byte[4096];
                if(!ReadBytes(imageBase,header)){failure="无法读取游戏版本";Disconnect();return false;}
                int pe=BitConverter.ToInt32(header,60);
                if(header[0]!='M'||header[1]!='Z'||pe<64||pe>3500||BitConverter.ToUInt32(header,pe)!=0x4550||BitConverter.ToUInt32(header,pe+8)!=profile.pe_timestamp||BitConverter.ToUInt32(header,pe+24+56)!=profile.image_size){failure="游戏版本未适配";Disconnect();return false;}
                failure="正在自动定位";return true;
            }
            finally { foreach(var p in processes)p.Dispose(); }
        }
        private bool Registry(out ulong[] chunks,out int count)
        {
            chunks=null;count=0;var b=new byte[32];
            if(!ReadBytes(imageBase+registryRva,b))return false;
            ulong array=BitConverter.ToUInt64(b,0);int max=BitConverter.ToInt32(b,16),num=BitConverter.ToInt32(b,20),maxChunks=BitConverter.ToInt32(b,24),numChunks=BitConverter.ToInt32(b,28);
            if(!Pointer(array)||max<=0||max>3000000||num<=0||num>max||maxChunks<=0||maxChunks>64||numChunks<=0||numChunks>maxChunks||num>numChunks*65536)return false;
            var pointers=new byte[numChunks*8];if(!ReadBytes(array,pointers))return false;
            chunks=new ulong[numChunks];for(int i=0;i<numChunks;i++){chunks[i]=BitConverter.ToUInt64(pointers,i*8);if(!Pointer(chunks[i]))return false;}
            count=num;return true;
        }
        private bool HeaderMatches(byte[] b,int expectedIndex)
        {
            // Exclude CDO/archetype/transient clones and objects being destroyed.
            return BitConverter.ToUInt64(b,0)==imageBase+vtableRva && (BitConverter.ToUInt32(b,8)&0x18070)==0 && BitConverter.ToInt32(b,12)==expectedIndex && BitConverter.ToUInt32(b,28)==0 && Pointer(BitConverter.ToUInt64(b,16)) && Pointer(BitConverter.ToUInt64(b,32));
        }
        private bool Locate(Func<bool> cancelled)
        {
            if(DateTime.UtcNow<nextLocate)return false;
            nextLocate=DateTime.UtcNow.AddSeconds(2);var clock=Stopwatch.StartNew();ulong[] chunks;int count;
            if(!Registry(out chunks,out count)){failure="等待游戏对象注册";return false;}
            var found=new List<Tuple<ulong,int,int,ulong>>();var first=new byte[8];var header=new byte[40];
            for(int chunk=0;chunk<chunks.Length;chunk++)
            {
                int n=Math.Min(65536,count-chunk*65536);var cells=new byte[n*24];
                if(!ReadBytes(chunks[chunk],cells)){failure="对象注册表暂不可读";return false;}
                for(int i=0;i<n;i++)
                {
                    if((i&1023)==0 && ((cancelled!=null && cancelled()) || clock.ElapsedMilliseconds>2000)){failure="自动定位等待重试";return false;}
                    ulong objectPtr=BitConverter.ToUInt64(cells,i*24);if(!Pointer(objectPtr)||!ReadBytes(objectPtr,first)||BitConverter.ToUInt64(first,0)!=imageBase+vtableRva)continue;
                    int objectIndex=chunk*65536+i;
                    if(ReadBytes(objectPtr,header) && HeaderMatches(header,objectIndex))found.Add(Tuple.Create(objectPtr,objectIndex,BitConverter.ToInt32(cells,i*24+16),BitConverter.ToUInt64(header,16)));
                }
            }
            LastLocateMs=clock.Elapsed.TotalMilliseconds;
            if(found.Count!=1){failure=found.Count==0?"等待当前车辆设置对象":"车辆设置对象不唯一";return false;}
            owner=found[0].Item1;index=found[0].Item2;serial=found[0].Item3;ownerClass=found[0].Item4;return true;
        }
        public void ResetVehicle() { owner=ownerClass=0;index=serial=0;nextLocate=DateTime.MinValue; }
        public ControlSnapshot Read(double rpm,double fuel,Func<bool> cancelled)
        {
            if(!Connect())return ControlSnapshot.Missing(failure);
            if(owner==0 && !Locate(cancelled))return ControlSnapshot.Missing(failure);
            ulong[] chunks;int count;var slot=new byte[24];var header=new byte[40];
            if(!Registry(out chunks,out count)||index>=count||!ReadBytes(chunks[index/65536]+(ulong)(index%65536)*24,slot)||BitConverter.ToUInt64(slot,0)!=owner||BitConverter.ToInt32(slot,16)!=serial||!ReadBytes(owner,header)||!HeaderMatches(header,index)||BitConverter.ToUInt64(header,16)!=ownerClass){ResetVehicle();return ControlSnapshot.Missing("车辆对象已变化，重新定位");}
            var raw=new byte[244];if(!ReadBytes(owner+(ulong)profile.state_anchor_offset-24,raw)){ResetVehicle();return ControlSnapshot.Missing("设置读取失效");}
            int abs=BitConverter.ToInt32(raw,24),tc=BitConverter.ToInt32(raw,0);
            float currentRpm=BitConverter.ToSingle(raw,32),currentFuel=BitConverter.ToSingle(raw,240);
            if(!profile.observed_level_indices.Contains(abs)||!profile.observed_level_indices.Contains(tc)||raw[136]>1||raw[137]>1)return ControlSnapshot.Missing("设置值超出已验证范围");
            if(Double.IsNaN(rpm)||Double.IsNaN(fuel)||float.IsNaN(currentRpm)||float.IsNaN(currentFuel)||Math.Abs(currentRpm-rpm)>1500||Math.Abs(currentFuel-fuel)>1){ResetVehicle();return ControlSnapshot.Missing("车辆数据尚未同步");}
            return new ControlSnapshot {Valid=true,AbsEnabled=raw[136]==1,TcsEnabled=raw[137]==1,AbsLevel=abs+1,TcsLevel=tc+1,Status="自动定位 / 当前车辆设置"};
        }
        private void Disconnect() { if(handle!=IntPtr.Zero)CloseHandle(handle);handle=IntPtr.Zero;imageBase=0;ResetVehicle(); }
        public void Dispose() { Disconnect(); }
    }
}
