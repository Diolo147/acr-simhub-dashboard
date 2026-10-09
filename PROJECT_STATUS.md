GitHub 提交准备（2026-10-10）：用户已创建公开仓库 https://github.com/Diolo147/acr-simhub-dashboard，main 初始提交9952de9a76fa34cef7fafab1f9b76fc3b7ab42bb。本机已初始化 Git 并连接 origin，保留用户初始提交。新增 README.md（已完成功能、验证、安装与构建入口）、ROADMAP.md（候选参数、更新适配和验收）、AGENTS.md（接手约定）。当前整理45个明确选择的源码、原生文件、安装包、脚本和有限证据，排除本机完整日志/硬件属性清单、备份、原始NPZ和第三方参考仪表。离线测试提供只有DataCorePlugin/ACRControlsPlugin的612项游戏属性夹具；JS验证/预览脚本支持仓库相对路径及夹具回退，构建插件不再要求旧固定地址配置。准备清单work/github-publication-manifest.json仅本机，生成脚本work/prepare-github-publication.py已纳入源码。GitHub插件负责提交，不依赖gh登录；完成后追加实际远端SHA，当前不能视为已推送。

当前版本 v2.5（2026-10-10 00:12）：ABS/TCS菜单设置自动定位已编译安装，运行仪表已加载。已实测：SimHub保持运行，游戏退出时清空，新游戏PID自动恢复有效值；无需修改配置。 当前实际记录ABS开启·1档、TCS关闭，PID49008，定位113.9ms；菜单关闭时仪表仅显示“关闭”，不显示隐藏选择档位。保留四轮集中布局、psi、校准与所有既有仪表。以下旧版固定地址限制是历史记录，以本段及新版插件说明为准。

实现：AutoControlMemoryReader由当前进程PEB取得exe基址，经SHA256、PE时间戳和映像大小门控，从exe相对UObject注册表定位唯一非临时车辆状态对象，核对slot/index/serial/class/vtable及当前RPM/燃油；缓存失效重新枚举。配置auto-locator-profile.json没有PID、堆地址、车名或菜单常数。游戏build25170642已验证；未来版本须重新分析偏移，未适配时显示—，没有跨所有未来版本的保证。每100ms轻量读取，完整定位节流2秒，后台线程上限2秒且可取消，SimHub DataUpdate不做枚举。

验证：32/64位真实自动定位、清除缓存重定位、错误车辆燃油拒绝、错误exe哈希拒绝通过（work/auto-reader-test-4/8.json）；216组件126绑定回归及自动来源/无效清空检查通过；原生加载、2560/3440渲染及原生导出已通过。安装djson/JS/DLL与源文件哈希一致，V1–V4/test仍保留。安装后实机左侧“菜单设置 / 自动定位”及ABS/TCS值已核对。证据work/auto-host-verification.txt、auto-controls-live-dashboard.jpg（标致首次验证）、auto-reconnect-evidence.json（大众重启重连）。重连验证未操作用户正在驾驶的窗口，预览为共享内存/插件静态采样，不是实机截图。不表示ABS/TCS介入、损伤、发动机曲线或灯光也已支持。

接手：src/plugin/AutoControlMemoryReader.cs为当前运行读取器；旧ControlMemoryReader.cs保留历史原型/共用快照类型，session-profile.json不再被运行插件加载。构建work/build-controls-plugin.ps1；测试work/test-auto-controls-reader.ps1（新的共享内存样本传-SamplePath）。配置源work/memory/auto-locator-profile.json→build/ACRSettingsBridge→SimHub/PluginsData/ACRSettingsBridge；DLL安装在SimHub根目录，更新前正常退出SimHub。最新说明ABS-TCS插件说明.md。有限研究脚本可能含历史PID/地址，不能当运行程序使用；verify-object-locator.py仅只读校验且不会覆盖定位配置。备份backups/auto-v2.4。交付work/finalize-auto-delivery.py、prepare-live-preview.cjs、export-native.ps1、package-delivery.py；不要运行旧finalize-controls-delivery.py（它断言旧设置并写回v2.4记录）。

<!-- v2.5 end -->
最终实机验收（2026-10-09 23:31）：已在下方LG ULTRAWIDE原生2560×1080启动v2.4 WPF仪表。真实画面左侧ABS开启·2档、TCS开启·1档，来源菜单设置/内存·本次游戏，布局无裁切。日志work/controls-host-verification.txt、实机截图work/controls-live-dashboard.jpg、插件结果work/controls-bridge-live.json佐证；源djson/JS与安装文件SHA256一致，其他V1–V4/test保留。运行中的仪表已加载更新，不需要用户再次重开。SimHub重启加载插件已验证；游戏重启/换车/重开后新定位仍未完成，当前会话失败时显示—。预览2560/3440、原生导入包、插件包与源码包已更新。

当前版本 v2.4（2026-10-09，ABS/TCS设置接入）：按用户最新要求先实现设置值，不处理实时介入。左侧显示ABS模式/档位与TCS模式/档位，真实读取开启2档/开启1档，新增菜单来源小字；分配阀压力、离合控制、变速箱模式保持删除。216组件126绑定。原生插件ACR Settings Bridge已编译安装并随SimHub加载，AttachDelegate属性为ACRControlsPlugin.*，不用Python常驻/网页。两结构一致、PID/路径/创建时间、当前车/赛段、稳定后的SimHub会话、年龄门控；失效显示—。这是本次游戏会话原型，仍无跨游戏重启定位，不声称永久可用。

验证：32/64位真实读取测试及错误创建时间拒绝通过；绑定合法关闭/缺失/过期/退出检查通过；SimHub实际32位加载AnyCPU DLL成功，2026-10-09 23:27:13日志和latest.json确认Valid=true ABS=true/2 TCS=true/1。已修复32位读取64位地址溢出（NtWow64ReadVirtualMemory64分支）及启动会话号短暂变化误判（初始稳定1秒）。原生加载、2560/3440静态渲染通过，预览采用23:27实测共享内存与插件记录，不把静态预览叫实时截图。实机仪表显示验收见本段后续记录。

接手：读ABS-TCS插件说明.md，源码src/plugin/*.cs；work/build-controls-plugin.ps1构建，test-controls-reader.ps1可分别用Framework64/32位PowerShell测试。config是work/memory/controls-session-profile.json，插件安装在SimHub根目录，配置在PluginsData/ACRSettingsBridge/session-profile.json。latest.json仅本地诊断，非传输文件。修改DLL需完全退出SimHub再覆盖；当前仪表JS使用插件属性，不读共享内存占位ABS/TC。新游戏进程必须重新定位验证，不能只改PID或放宽门控。DLL独立交付ACR Settings Bridge.zip，simhubdash不能安装DLL；源码ZIP包含插件源码、DLL、当前配置和证据。备份backups/bridge-v2.3。以下条目是历史记录，有冲突以v2.4和插件说明为准。

当前版本 v2.3（2026-10-09，控制区精简及内部内存调查）：按用户要求删除左侧分配阀压力、离合控制、变速箱模式三行；保留ABS/TCS/发动机曲线/灯光四行并扩大行间距，右下前制动比例及实际离合踏板保留。216组件、123绑定，单位/缺失/退出/颜色回归与本机原生加载、2560/3440预览通过。已安装、原生导出，运行实例未重新加载。备份backups/controls-v2.2。

内部内存调查完成第一阶段：实际读取acr.exe进程，PID48404/Steam build25170642；OpenProcess(0x410)、VirtualQueryEx、ReadProcessMemory只读，无写入/注入/暂停。定位两份一致结构：ABS档位锚点0x21ca854b7ac与0x21cb8a664cc，int32原值+1；TCS档位锚点−24，模式ABS+112/TCS+113为uint8 0关闭1开启。11组受控邻域快照×2结构通过验证；ABS/TCS档位1/2/3分别对应0/1/2，模式开关独立。切至发动机页面后有限读取8秒32样本一致，最后恢复ABS开启2档/TCS开启1档及原菜单。证据work/memory/research-results.json与control-read-20261009-230715.jsonl；说明内部内存读取说明.md。work/read-control-memory.py为最长60秒的有限原型，按PID/路径/创建时间校验、要求两份值一致，所有采集器已退出。初轮显示数字直读筛选不稳定已排除；abs-confirm4画面实际仍3，实验作废。不要沿用错误候选。

限制与接手：本次仅找到设置模式和选择档位，不代表实时介入；绝对堆地址未验证重开赛段、换车或游戏重启，没有稳定指针/对象定位，没有接入SimHub。src/acr.js支持门控仍false，仪表依旧—，不可硬编码本次地址或伪装SimHub原生属性。下一步应先找稳定定位并跨重启验证，再开发插件；无需用户再配合重复本次静止菜单测试。原始大候选NPZ仅本地保存，源ZIP包含有限上下文与结果，不包含完整进程转储。

历史版本 v2.2（2026-10-09，胎温优化）：用户游戏轮胎分层彩色与仪表单值核心色谱不同。实测work/status-20261009-222500.json：核心K [319.81778,315.97791,288.61871,287.60742]→°C [46.6678,42.8279,15.4687,14.4574]；Physics.tyreTemp第四组与核心逐轮相同，tyreTempI/M/O全部0。当前确有核心胎温动态变化，旧资料“0.3后固定胎温”不能代替本机结论。游戏分层HUD的具体数值/色谱未找到官方ACR规格，不能推定已有表面温度，也不能借ACC资料制造前轮上半热/下半冷。
优化：原15–100°C宽均匀色谱改固定绝对锚点0°C蓝、15青、25绿、35黄、50橙、65红，线性插值，越界限幅、无数据灰色；这只是显示范围，绿色不代表最佳抓地、红色不代表过热报警。不会按实时最冷/最热轮胎自动重缩放。源ACR_TYRE_SCALE.points可调整，必须保留物理值不变。位图胎纹换为透明三纵带轮廓，同一核心温度驱动整条轮胎，不伪造三路温度；数字保留1位小数，新增核心°C标签，图形高度缩到124px避免标签重叠。四轮底注说明只有核心单值。后台仍标准TyreTemperature优先，未改Kelvin/摄氏转换，校准和psi保持。
验证：224组件、126绑定；0/15/25/32/35/50/65/100°C颜色与插值、缺失、零值及限幅检查通过，原绑定回归、原生加载及2560/3440渲染通过。最新预览使用该次共享内存实测夹具，转速上限仍未从标准属性同步到夹具，因此显示未提供（不能拿旧车上限顶替）。本轮未电脑控制，未重载运行实例；已复制安装文件并导出，需用户关闭重开当前仪表。备份backups/tyre-v2.1；接手修改图案在build_dashboard.py draw_tread，色谱在acr.js；以下历史记录以本段为准。

最新调查（2026-10-09）：用户碰撞后游戏图标变色，但三次递增packetId快照车身/悬挂损伤及磨损仍0，直接游戏共享内存证据见work/post-impact-check.json。没有开启损伤显示。网络核对发现早期ACR项目报告Physics.abs/tc可能有配置状态，不能笼统宣称全不支持；实际介入字段与效果支持不能混用。本机当前未验证，ACR_CONTROL_SUPPORT仍关闭。详情和来源见遥测支持调查.md；Steam build25170642。仪表仍v2.1，本轮只更新调查、映射说明和证据，没有修改布局/绑定。

当前版本 v2.1（2026-10-09）：按用户要求四轮重新合并到右侧2×2（FL/FR在上，RL/RR在下），恢复原模块坐标和psi；左侧改车辆控制与环境区域，中央保留挡位/速度/RPM/驾驶摘要，底部保持输入/趋势/G/水温/燃油/前制动比例。新增原生Text/Rectangle的发动机、点火、启动机状态及温度显示；未知控制设置保留灰色—，不解释为关闭/自动。
实测证据：游戏acr与SimHubWPF 9.12.8均运行。work/status-test-20261009-220543.jsonl记录300点、约60秒三块只读共享内存；用户确认完成发动机曲线/灯光/ABS菜单改变后恢复。Graphics.EngineMap/ABS/lightsStage始终0；Physics.abs/tc始终0；isEngineRunning出现0/1、starterEngineOn出现0/1、ignitionOn当前始终1。支持运行/启动机、点火原始状态；不采用标准EngineMap可能默认1的值冒充菜单选择。TCS/自动离合/自动变速箱没有可靠证据，关闭显示绑定；分配阀压力不是BrakeBias，也不是四轮brakePressure，后者本次均0。天气时刻/预报、胎种不输出有效值；无损车损/磨损等0不能证明支持或提供健康百分比，因此不启用。总结work/status-support-report.json，原始布局仅用于只读解析，不执行第三方运行代码。所有采集器已退出。
单位：Physics.AirTemp/RoadTemp为K，减273.15，实测约10.4°C与用户菜单10°C相符；不改变标准水温/胎温/刹温已有转换。环境原始0或异常K值显示—，正常0°C保留。状态词随原始0/1变化且受acrState有效/陈旧判断保护。src/acr.js中ACR_CONTROL_SUPPORT显式门控，当前只有engine/ignition/starter为true，其余false。将来只能在确认菜单变化和SimHub属性后开启，不可直接用泛用零值字段。
验证：220组件、126绑定；回归检查、发动机停止/运行/缺失、未支持项、Kelvin和退出检查通过；原生加载与2560/3440渲染完成。work/prepare-live-preview.cjs把当天共享内存样本映射成预览专用标准属性夹具，预览并非实时SimHub完整属性导出；该车静态转速上限0，预览明确显示未提供，绝不沿用Hyundai旧车上限。该脚本不改运行绑定。显示数值格式修正负零。UI属性页多次检测到用户输入，停止点击；没有强制导出或重载运行实例。最新安装文件与原生导入包更新，需用户关闭重开当前仪表。旧v2.0源文件在backups/style-v2.0。
接手：源布局src/cockpit_layout.py；新增状态helpers在src/acr.js；capture-status.py为单次读，capture-status-test.py为60秒读，analyze-status.py汇总，prepare-live-preview.cjs为当日静态展示，prepare-preview.cjs仍可检查旧SimHub属性样本。不要把原始记录的占位0当成有效ABS模式、TCS模式或轮胎磨损。历史描述冲突以本段为准。

当前版本 v2.0（2026-10-09）：参考用户两张赛车仪表截图，以及J:/Game/dashboard中的ACR Hyundai i20N Rally2、AIO DASHBOARD WIDE、HERVE FULL实际包内预览/原生结构。只参考布局与视觉，不执行第三方JS，不复制其资源或导入覆盖模板。全黑背景、原生Rectangle分区和细直线、黄色超大主挡位，去掉网页风切角框体及装饰渐变。左侧FL/RL、右侧FR/RR，中间挡位/速度/RPM，中央下沿驾驶计时/最高速度，底部输入/趋势/车辆状态；轮胎图案和温度颜色保留，胎压psi保持。移除无有效地图时的空白占位和地图组件（地图从未启用），没有删掉可用物理遥测。185原生组件、111绑定；绑定回归与原生加载检查通过，2560/3440原生静态渲染通过。预览来自历史记录，不代表当前游戏实时画面。运行实例未UI重载，重新打开仪表生效。src/acr.js数据转换/校准未改动。
实现：src/build_dashboard.py生成初始组件后执行src/cockpit_layout.py，对WheelWidget子组件采用绝对坐标变换，维持Layer语义；夜间遮罩重新放在最上方覆盖新增元素。主挡位改TextItem，避免OutlinedText零描边导致本机渲染空白。旧生成器备份backups/style-v1.4。接手布局修改优先改cockpit_layout.py，字段修改仍在acr.js。已更新安装目录及原生导入包；以下为历史记录，状态不一致以本段和FIELD_MAP为准。

视觉精简 v1.2（2026-10-07）：应用户要求删除中央三条装饰弧线、底部斜刻度及两组装饰连线；删除中央车身小图、重复单位与装饰英文文案。保留四角短边、深色渐变和挡位/车速/转速层级。192组件、113绑定，绑定检查及本机原生反序列化通过；2560×1080与3440×1440原生静态预览通过。最新文件已安装并重新导出；运行中的仪表未通过UI重新加载，用户需重新打开仪表才能看到本次更改。转向/G等待校准状态保持不变。以下v1.1段落为历史记录。

# ACR Rally 21x9

视觉改版 v1.1（2026-10-07）：连接状态移到左下角；原中央状态条删除，替换为小型车身示意和动力信息标识；新增原创几何生成PNG的轮胎胎纹、HUD弧线、切角框体和电路刻线。四轮胎温使用原生Rectangle背景色绑定+透明Image胎纹，因此仍可编辑且不需要网页。ACR_TYRE_SCALE默认15–100°C，蓝→青→橙→红是测量色谱，不是最佳温度或警报；无数据灰色。196组件，113绑定；颜色端点/缺失检查及原生双分辨率渲染验证。校准流程见校准说明.md。当前轮次仅更换文件，不操作用户鼠标键盘；已打开仪表需重新加载或下次启动生效。

更新：2026-10-07。状态：本轮仪表修改、安装、导出、双分辨率预览与文档交付完成；部分动态校准保持待验证。

目标：SimHub 9.12.8 原生单页 2560×1080 拉力仪表，适配下方 LG，兼容 3440×1440。保留现有 ACR_Ultrawide_Tech V1–V4 和 test。

目录：src 为生成器和字段处理；build 为原生仪表；work 为属性导出、组件结构检查和测试；backups 为改动前备份。不得覆盖其他仪表。

已核实：完整属性清单已通过 SimHub 导出到 work/property-catalog.json；Chart/OutlinedText/Button 等组件属性通过本机程序集反射核对，未修改程序程序集。原生 .djson.ressources 是图片资源 ZIP。

已完成：修正 Rectangle 的 BackgroundColor、Layer 绝对坐标、OutlinedText 的 FillColorEx/StrokeColorEx、复制组件重复 Sid；188 个组件，13 类顶层原生类型；所有字段优先标准属性，明确原始单位转换。109 个绑定通过 Node 执行验证，包括单位、零值、缺失、陈旧包、退出、其他游戏、重开、错误上限回退。SimHub 本机程序集反序列化通过（OK 1）。这不是完整动态驾驶验证。

实测：2026-09-29道路样本已保留在 work/live-catalog.json 和 ws0.json。2026-10-07原生 WPF Renderer 已成功显示布局，日志明确启动目标 LG ULTRAWIDE，2560×1080。编辑器原生可编辑。最新修正已复制到安装目录，仅覆盖 ACR Rally 21x9。

导出：work/export-native.ps1 使用本机 SimHub 原生 Export(GraphicalDashItem,string,bool) API，非改扩展名。当前交付目录 C:\Users\dxd\Documents\Codex\2026-09-28\new-chat\outputs。最终包含原生文件、图片资源、局部 JS 扩展和预览图片，ZIP CRC 校验通过。

字段支持、转换、有效性和待验证项目见 FIELD_MAP.md；使用说明见 使用说明.md。转向/G/地图默认关闭，离合方向明确待验证；不要为了“功能全面”强行启用。温度和压力没有通用 GT 告警。

环境：SimHub 9.12.8，免费版；GlobalSimhubSettings.RunAsAdmin 原为 true，用户改为 false 后 UI 自动操作恢复；日志已确认普通权限。8888端口被微信绑定，网页服务启动失败；本仪表用 WPF，不依赖网页服务。不要擅自退出微信或升级 SimHub。

接手：先阅读 FIELD_MAP.md；构建 src/build_dashboard.py，再运行 work/verify-bindings.cjs 与 validate-native.ps1，复制 build/ACR Rally 21x9 到 SimHub/DashTemplates；关闭旧编辑器以免其保存覆盖生成器文件，再通过更多菜单重新加载。导出脚本默认写用户输出目录。不要修改其他模板。

最终预览：prepare-preview.cjs 计算 2026-09-29 样本绑定，render-native.ps1 使用 SimHub 的 DashHostRendering 和 ImageCapturer 原生渲染，生成 2560×1080 与 3440×1440 图片并目检。不是浏览器仿制或 AI 效果图；预览明确标注静态样本，不伪造趋势历史。布局与挡位数字正确，3440 原生渲染保持比例且无裁切。

最终启动：2026-10-07 12:39:02 日志确认最终文件启动 WPF，目标 LG ULTRAWIDE {X=346,Y=1440,Width=2560,Height=1080}。UI 操作已结束；用户需要可随时 Esc 中断，避免连续争抢鼠标键盘。优先通过文件/只读接口工作。

动态采集：work/capture-road.py 为一次性只读 OpenFileMapping/MapViewOfFile 采样，已退出，无常驻采集器。work/road-2026-10-07.jsonl 共1200点、约120秒；油门/刹车/离合原始值都有0–1变化，转向范围 -0.0253…0.8272，最高27.804km/h，最高7563rpm；四轮悬挂和载荷有变化。没有足够的动作时间标注验证左右正负、离合按压方向、G量纲与轴向，不能据此开启相关开关。原始布局参考 https://github.com/albertowd/live-telemetry-evo/blob/develop/src/live_telemetry_evo/sources/acrally.py ，只采用已检视的800字节结构声明，不执行第三方采集器。

仍待验证：重启自动恢复 LG；实际桌面3440屏运行（已有3440原生渲染检查）；四轮物理顺序的专门动作验证、离合按压/释放方向、转向、G、暂停重开换车。保持诚实限制，不要将 Node 模拟检查或单次道路采样称为完整验收。

约束：不把零当作普遍缺失；不臆造计时/健康百分比；没有动态验证的轴向不启用；不需要外部网页或常驻 Python。


校准准备（2026-10-07）：新增work/capture-calibration.py，按steering/longitudinal/lateral分阶段采集、带时间戳保存独立文件，不覆盖道路旧记录；仅一次性只读共享内存，尚未开始采集。等待用户进入道路并就位，然后分阶段记录明确动作。需要同步核对SimHub标准加速度和原始AccG，确认转换后再启用，现有开关保持关闭。

校准完成 v1.3（2026-10-07，覆盖历史待校准说明）：用户配合停车回中/左满/右满以及加速/制动/左右弯，保存350点转向与600点驾驶记录（work/calibration-*.jsonl）。转向实测端点−1/+1，顺序先左后右，启用×100百分比；不擅自消除真实中心偏差。纵向用1秒中心差分速度计算G，在速度>15km/h且|转向|<0.08的360点中，AccG03相关0.95367、过原点比例1.04677，确认原值为G；不能重复除9.80665，不套用实测拟合比例修正。左右弯10–35km/h、|转向|>0.3时AccG01中位数左+0.311（53点）右−0.13578（51点），显示横向取负以左负右正，纵向加速正/制动负。使用原始AccG01/03绕开尚未同步验证的SimHub标准加速度转换；AccG02不用于二维球。已启用ACR_VERIFIED.steer/g，map仍禁用。新增端点、缺失、G符号/无重复换算检查通过；本机原生反序列化和预览通过。安装文件及导入包更新，运行实例未重载，需要用户重新打开仪表。采集器均已退出。该校准不代表暂停/换车等全部验收；换设备输入设置后需重新核对转向。

v1.4（2026-10-07）：按用户要求胎压统一psi，保留1位小数，输入单位psi/bar/kPa分别正确转换，未知单位仍不显示；四轮制动标签改为刹温，避免误认为踏板或制动力。温度°C、悬挂mm、载荷kN、滑移原值不变。构建、绑定检查、原生加载及预览检查后更新安装文件和导入包；运行仪表需用户重新打开。
