# ACR Settings Bridge v2.5

读取ACR当前车辆的ABS/TCS菜单开关与选择档位，供SimHub原生仪表使用；不是实时介入。已实测：SimHub保持运行，游戏退出时清空，新游戏PID自动恢复有效值；无需修改配置。 当前实测ABS开启·1档、TCS关闭，结果见work/auto-reconnect-evidence.json。

## 安装与恢复

完全退出SimHub，将ACR.SettingsBridge.dll放到`C:\Program Files (x86)\SimHub`，将auto-locator-profile.json放到其`PluginsData\ACRSettingsBridge`子目录，正常启动SimHub。本机已经安装。仪表包另行导入；不能通过.simhubdash安装DLL。配置image是本机游戏exe完整路径；换安装目录时先核对同版本再改路径。旧session-profile.json不再使用，不要把旧PID或地址抄进新配置。

当前支持Steam build25170642，exeSHA256为42c359b0cd24774a86441710fdc7d7db3bc06b57b3ff30cb9ea5d56fb71448fb。重启、进入赛段和换车时重新取得当前对象；没有有效对象或更新后的未知版本显示—。若一直—查看PluginsData/ACRSettingsBridge/latest.json的status，以及Logs/SimHub.txt中ACR Settings Bridge条目。

卸载时正常退出SimHub后移走DLL；仪表设置显示—，无需修改游戏。

## 属性与有效性

| 属性前缀ACRControlsPlugin. | 含义 |
|---|---|
| Valid / AgeMs | 有效及结果年龄，仪表要求≤1500ms |
| ABS.Enabled / TCS.Enabled | bool或null，真实菜单模式 |
| ABS.Level / TCS.Level | int或null，选择档位1/2/3；关闭时界面只显示关闭 |
| Status | 等待/自动定位/版本不匹配等状态 |
| AutomaticLocator / SessionOnly | true / false |

门控：完整exe路径、进程创建时间、SHA256和PE标识、当前SimHub车辆/赛段/会话稳定1秒、UObject槽位/index/serial/class/vtable、唯一非临时状态对象、模式字节0/1、档位原值0/1/2、当前RPM/燃油同步。合法零值不会被当缺失；缓存失效重新定位，过期/退出/身份变化立即清空。

## 实现和接手

.NET Framework4.8 AnyCPU插件随SimHub运行，100ms后台读取；完整枚举每次最多2秒、重试节流2秒、可取消，数据更新线程只做短身份门控。定位从当前PEB取exe基址，经相对UObject注册表取得车辆对象；实际读取仅244字节。没有常驻Python、网页、内存写入、注入或暂停。latest.json每秒写一次诊断，不是仪表的数据传输方式。

32位SimHub读取64位ACR使用NtWow64QueryInformationProcess64及NtWow64ReadVirtualMemory64，64位测试分支用NtQueryInformationProcess及ReadProcessMemory。Windows非公开接口可能随系统变化；失败会清空。声明参考[Blackbone FunctionTypes.h](https://github.com/DarthTon/Blackbone/blob/master/src/BlackBone/Include/FunctionTypes.h)与[phnt ntmmapi.h](https://github.com/winsiderss/phnt/blob/master/ntmmapi.h)。具体ACR偏移和过滤依据为本机实验，不能视为Unreal通用规格。

源码src/plugin/AutoControlMemoryReader.cs、ACRControlsPlugin.cs；旧ControlMemoryReader.cs留存快照类型与历史测试。构建work/build-controls-plugin.ps1；work/test-auto-controls-reader.ps1分别用32/64位PowerShell通过自动读取、缓存重定位、错误车辆和错误版本拒绝。配置work/memory/auto-locator-profile.json不含PID、堆地址、车名或ABS/TCS常数。game_key/pid/object_address/locate_ms仅为最新诊断记录，不作为输入配置。游戏更新应重新验证结构，不能仅放宽哈希校验。

四轮、psi、转向/G和原有仪表保留。发动机曲线/灯光仍未确认，损伤与介入仍未接入。更多交接记录见PROJECT_STATUS.md。
