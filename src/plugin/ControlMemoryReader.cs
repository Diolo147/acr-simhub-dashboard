using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using Newtonsoft.Json;

namespace ACR.NativeControls
{
    public sealed class SessionProfile
    {
        public int pid;
        public ulong creation_time;
        public string image;
        public string[] anchors;
        public int[] observed_level_indices;
        public string expected_car;
        public string expected_track;
    }

    public sealed class ControlSnapshot
    {
        public bool Valid;
        public bool AbsEnabled, TcsEnabled;
        public int AbsLevel, TcsLevel;
        public DateTime TimestampUtc = DateTime.UtcNow;
        public string Status;
        public static ControlSnapshot Missing(string status) { return new ControlSnapshot { Status = status }; }
    }

    // This reader has only QUERY_INFORMATION + VM_READ access. Addresses live in a
    // session identity checked config; no scanning/writes/injection in the plugin.
    public sealed class ControlMemoryReader : IDisposable
    {
        private readonly SessionProfile profile;
        private readonly long[] anchors;
        private IntPtr handle;
        public SessionProfile Profile { get { return profile; } }
        [DllImport("kernel32.dll", SetLastError=true)] private static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
        [DllImport("kernel32.dll")] private static extern bool CloseHandle(IntPtr h);
        [DllImport("kernel32.dll", SetLastError=true)] private static extern bool GetProcessTimes(IntPtr h, out ulong created, out ulong exited, out ulong kernel, out ulong user);
        [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern bool QueryFullProcessImageName(IntPtr h, uint flags, StringBuilder name, ref uint size);
        [DllImport("kernel32.dll", SetLastError=true)] private static extern bool ReadProcessMemory(IntPtr h, IntPtr address, byte[] bytes, UIntPtr size, out UIntPtr read);
        [DllImport("ntdll.dll")] private static extern int NtWow64ReadVirtualMemory64(IntPtr h, ulong address, [Out] byte[] bytes, ulong size, out ulong read);
        [DllImport("kernel32.dll", SetLastError=true)] private static extern bool GetExitCodeProcess(IntPtr h, out uint code);

        public ControlMemoryReader(string configPath)
        {
            profile = JsonConvert.DeserializeObject<SessionProfile>(File.ReadAllText(configPath));
            if (profile == null || profile.pid <= 0 || profile.creation_time == 0 || profile.anchors == null || profile.anchors.Length != 2 || profile.observed_level_indices == null || profile.observed_level_indices.Length == 0 || !String.Equals(Path.GetFileName(profile.image), "acr.exe", StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Invalid ACR session profile");
            anchors = profile.anchors.Select(s => long.Parse(s.StartsWith("0x") ? s.Substring(2) : s, NumberStyles.HexNumber)).ToArray();
            if (anchors[0] == anchors[1] || anchors.Any(x => x < 0x10000 || x > 0x7fffffffffff-256)) throw new InvalidDataException("Invalid anchors");
        }
        private bool EnsureIdentity()
        {
            if (handle == IntPtr.Zero) handle = OpenProcess(0x410, false, profile.pid);
            if (handle == IntPtr.Zero) return false;
            ulong born, exit, kernel, user; uint code;
            var name = new StringBuilder(32768); uint size = (uint)name.Capacity;
            return GetExitCodeProcess(handle, out code) && code == 259 &&
                GetProcessTimes(handle, out born, out exit, out kernel, out user) && born == profile.creation_time &&
                QueryFullProcessImageName(handle, 0, name, ref size) && String.Equals(name.ToString(), profile.image, StringComparison.OrdinalIgnoreCase);
        }
        public ControlSnapshot Read()
        {
            if (!EnsureIdentity()) { Dispose(); return ControlSnapshot.Missing("原游戏进程已失效，需重新定位"); }
            ControlSnapshot first = null;
            foreach (long anchor in anchors)
            {
                var raw = new byte[138];
                if (!ReadBytes(anchor-24, raw)) return ControlSnapshot.Missing("内存读取失效");
                int abs = BitConverter.ToInt32(raw,24), tc = BitConverter.ToInt32(raw,0);
                if (!profile.observed_level_indices.Contains(abs) || !profile.observed_level_indices.Contains(tc) || raw[136] > 1 || raw[137] > 1) return ControlSnapshot.Missing("设置值超出已验证范围");
                var current = new ControlSnapshot { Valid=true, AbsEnabled=raw[136]==1, TcsEnabled=raw[137]==1, AbsLevel=abs+1, TcsLevel=tc+1, Status="本次游戏内存设置" };
                if (first != null && (first.AbsEnabled!=current.AbsEnabled || first.TcsEnabled!=current.TcsEnabled || first.AbsLevel!=current.AbsLevel || first.TcsLevel!=current.TcsLevel)) return ControlSnapshot.Missing("两份设置值暂不一致");
                first = current;
            }
            return first;
        }
        private bool ReadBytes(long address, byte[] bytes)
        {
            // SimHub can run as x86 while ACR's allocations are above 4 GiB.
            if (IntPtr.Size==4)
            {
                ulong got;
                return NtWow64ReadVirtualMemory64(handle,(ulong)address,bytes,(ulong)bytes.Length,out got)==0 && got==(ulong)bytes.Length;
            }
            UIntPtr count;
            return ReadProcessMemory(handle,new IntPtr(address),bytes,new UIntPtr((uint)bytes.Length),out count) && count.ToUInt64()==(ulong)bytes.Length;
        }
        public void Dispose() { if (handle != IntPtr.Zero) { CloseHandle(handle); handle=IntPtr.Zero; } }
    }
}
