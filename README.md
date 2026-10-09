# ACR Rally 21x9

为 Assetto Corsa Rally 制作的 SimHub 原生可编辑仪表，以及补充 ABS/TCS 菜单设置的只读插件。当前版本 **v2.5**，验证日期 **2026-10-10**。

画布为 2560×1080，可按比例显示在 3440×1440。仪表运行不依赖网页或常驻 Python；Python 仅用于生成、研究和有限采样。已有仪表 V1–V4 和 test 保留。

![当前车辆数据静态预览](build/ACR%20Rally%2021x9/ACR%20Rally%2021x9.djson.png)

预览采用大众 Polo GTI R5／威尔士 Severn 的共享内存和插件记录；图表仅运行时生成，静态预览中的转速上限未填入，不代表游戏不支持。

## 已完成

| 功能 | 当前实现与验证 |
|---|---|
| 核心驾驶信息 | 挡位、车速、RPM、按有效车辆上限计算的转速条与换挡灯 |
| 四轮状态 | FL/FR/RL/RR 集中 2×2；胎压 psi、核心胎温 °C、刹温 °C、悬挂 mm、载荷 kN、滑移原值 |
| 胎温图形 | 核心单值驱动三纵带轮胎色谱；不虚构分区温度或最佳抓地范围 |
| 操作与趋势 | 油门／刹车／离合、转向百分比、原生 Chart 踏板与车速趋势 |
| 转向与 G | 用户驾驶校准；横向左负右正，纵向加速正制动负；二维球位置限幅，数字不截断 |
| 发动机与环境 | 发动机／点火／启动机状态、气温／路温、水温、燃油、前制动比例 |
| ABS/TCS 设置 | 原生 .NET Framework 4.8 AnyCPU 插件读取菜单开关及档位 1/2/3，不代表实时介入 |
| 自动定位 | 从当前 exe 基址及对象注册表定位车辆状态；无固定 PID 或堆地址配置 |
| 失效处理 | 游戏退出、身份变化、未知版本、缺失或过期数据清空，显示 `—`；合法零值保留 |

实际重连记录：SimHub 保持运行，ACR 从标致 208 Rally4 重启换成大众 Polo GTI R5，赛段更换为威尔士 Severn；旧值清空后自动恢复 ABS 开启 1 档／TCS 关闭，定位约 114ms。记录见 `work/auto-reconnect-evidence.json`。

当前原生仪表有 **216 个组件、126 个绑定**。32/64 位读取测试、缓存重定位、错误车辆/版本拒绝、绑定回归、原生加载、2560/3440 渲染及导出均已通过。暂停、赛段重开、多车连续切换仍需要更全面的回归，不能由一次重连推定全部场景通过。

## 安装

本机已经安装；仓库中的安装流程供恢复与新环境使用：

1. 在 SimHub 导入 `dist/ACR Rally 21x9.simhubdash`。
2. 完全退出 SimHub，将 `build/ACRSettingsBridge/ACR.SettingsBridge.dll` 放到 SimHub 根目录。
3. 将 `build/ACRSettingsBridge/auto-locator-profile.json` 放到 `PluginsData/ACRSettingsBridge/`，核对其 `image` 为本机 `acr.exe` 完整路径。
4. 正常启动 SimHub，打开仪表，选择 **LG ULTRAWIDE** 对应显示器；显示器编号可能变化。

导入仪表包不能代替安装 DLL。配置仅适配已验证的 ACR **Steam build 25170642**，不能仅修改哈希绕过版本检查。更新后未知版本显示 `—`；查看插件 `latest.json` 的 `status` 和 SimHub 日志。

## 构建与检查

本项目当前构建脚本使用本机路径 `I:\code\simhub-dashboard` 与 `C:\Program Files (x86)\SimHub`。换环境时先修改脚本路径及游戏配置。

```powershell
# 使用含 Pillow 的 Python 生成原生仪表
python src/build_dashboard.py

# 编译 AnyCPU 插件；依赖本机 SimHub DLL 和 .NET Framework 4.8
powershell -NoProfile -ExecutionPolicy Bypass -File work/build-controls-plugin.ps1

# 离线检查显示绑定及失效处理，不需要游戏运行
node work/verify-bindings.cjs

# 原生类型加载检查，需本机 SimHub
powershell -NoProfile -STA -File work/validate-native.ps1
```

`work/test-auto-controls-reader.ps1` 是需要当前游戏与同次共享内存样本的有限只读测试，可通过 `-SamplePath` 指定新样本。分别在 32/64 位 Windows PowerShell 运行。研究记录中的 PID/地址是历史证据，不能复制为运行配置。

## 项目资料与下一步

- [后续实现与游戏更新适配](ROADMAP.md)：候选参数、实验方式和验收标准。
- [项目状态及 agent 交接](PROJECT_STATUS.md)：当前状态及历史记录；最新段落优先。
- [字段映射](FIELD_MAP.md)：属性路径、单位和可用性。
- [ABS/TCS 插件说明](ABS-TCS插件说明.md)：安装、版本门控与自动定位机制。
- [使用说明](使用说明.md)、[校准说明](校准说明.md)、[遥测支持调查](遥测支持调查.md)、[内部读取说明](内部内存读取说明.md)。

原生编辑文件位于 `build/ACR Rally 21x9/`；生成源在 `src/`；只读证据与脚本在 `work/`。不提交完整进程转储、原始大候选数组、本机备份和第三方参考仪表。SimHub 与游戏 DLL 不随仓库分发。

GitHub 地址：<https://github.com/Diolo147/acr-simhub-dashboard>。仓库由用户创建为公开仓库；`work/fixtures/live-catalog.json` 只保留离线验证需要的游戏属性，完整属性清单留在本机。项目状态里的旧实验文件路径有部分仅本机保存，不能把缺少历史附件理解为当前功能失效。
