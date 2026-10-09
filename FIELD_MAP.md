v2.5 自动定位（2026-10-10）：ABS/TCS沿用ACRControlsPlugin.ABS.Enabled/Level、TCS.Enabled/Level，单位仍bool与选择档位int（内存0/1/2+1）。有效条件仍Valid=true、AgeMs≤1500ms及整页有效遥测。新增AutomaticLocator=true；SessionOnly=false。对象身份、当前RPM/燃油及exe版本均经校验，无效属性返回null。车辆/会话变化清空并重新定位，未确认数据仍—。当前配置没有PID或固定堆地址；不是共享内存标准字段，也不是介入指示。

<!-- v2.5 end -->
v2.4 ABS/TCS设置（2026-10-09）：已接入本机原生ACR Settings Bridge插件，只适用于已验证进程，不是标准共享内存字段，不代表介入。

| 显示 | 属性路径 | 单位/转换 | 有效条件 |
|---|---|---|---|
| ABS模式 | ACRControlsPlugin.ABS.Enabled | bool true开启/false关闭 | ACRControlsPlugin.Valid=true且AgeMs≤1500ms，并满足整页ACR遥测有效性 |
| ABS档位 | ACRControlsPlugin.ABS.Level | int，读取int32原值+1 | 已验证1/2/3；原生插件两副本一致及身份门控 |
| TCS模式 | ACRControlsPlugin.TCS.Enabled | bool | 同上 |
| TCS档位 | ACRControlsPlugin.TCS.Level | int，原值+1 | 同上 |

开启显示“开启 · N档”，关闭显示“关闭”，失效/缺失显示—。本机SimHub实际读到ABS开启2档/TCS开启1档。物理共享内存abs/tc仍0，不作为回退。发动机曲线、灯光尚未确认；不启用介入或损伤。详细实现与重启限制见ABS-TCS插件说明.md。以下为历史映射。

v2.2：只显示已验证的核心胎温；同样核心值驱动三纵带图案及一位小数，内中外0、第四组与核心重复，不显示假分层。色谱锚点0/15/25/35/50/65°C为视觉刻度，不是工作范围或报警，早期“固定胎温”结论已被本机动态样本更新。

2026-10-09补充：碰撞后三次递增包快照CarDamage01–05、suspensionDamage01–04仍0，不能显示100%健康。ABS/TCS不能一概判定游戏完全不支持：早期实测资料说Physics.abs/tc配置状态可能有值，介入字段却无数据；本机目前未验证。详见遥测支持调查.md。

v2.1（2026-10-09）新增与支持限制：

| 显示 | 实际属性 | 处理 / 实测 |
|---|---|---|
| 发动机 | R.isEngineRunning | 0停止、1运行；本次采到0/1 |
| 点火 | R.ignitionOn | 0关闭、1开启；本次读到1，未专门验证开关动作 |
| 启动机 | R.starterEngineOn | 0待机、1工作；本次采到0/1 |
| 气温 / 路温 | R.AirTemp / R.RoadTemp | 原始K−273.15→°C，约10.4°C；仅确认原始K字段才转换 |
| 分配阀压力 | 未确认 | 不能用D.BrakeBias或四轮制动压力代替，显示— |
| ABS模式/档位、发动机曲线、灯光 | 泛用Graphics字段占位0 | 用户改变菜单期间未响应，显示— |
| TCS、离合控制、自动变速箱 | 未确认 | 不把TC=0/AidAutoClutch=0/AutoShifterOn=0直接当作关闭或手动 |
| 天气/时刻/预报 | 未确认 | Clock=0，rainIntensity系列0不能充分验证，显示未输出 |
| 胎种、磨损、损伤 | 未确认 | 胎种空、wear/damage为0；无损车0不能证明健康百分比，暂不启用 |

原始证据work/status-test-20261009-220543.jsonl，汇总work/status-support-report.json。点火与控制状态在缺失/退出/陈旧时显示—；合法发动机停止0保留。以下历史映射不变。

# ACR Rally 21x9 字段映射

v1.1：胎温轮胎图案采用ACR_TYRE_SCALE可调整的15–100°C连续色谱，蓝/青/橙/红表达相对测量温度；缺失灰色。该色谱不定义车辆最佳胎温，不触发报警。单一核心胎温驱动整条轮胎，不虚构内中外三区温度。

更新：2026-10-07；本机 SimHub 9.12.8。标准属性道路样本为 `work/live-catalog.json`（2026-09-29），`work/ws0.json` 为标准化数据。2026-10-07另采集1200点/约120秒只读原始共享内存，见 `work/road-2026-10-07.jsonl`；单次样本不等于完整动态校准。

下表 D 表示 `DataCorePlugin.GameData.`，R 表示 `DataCorePlugin.GameRawData.Physics.`。四轮标准后缀依次为 FrontLeft / FrontRight / RearLeft / RearRight，原始后缀依次为 01 / 02 / 03 / 04。

| 显示 | 属性路径 | 单位与转换 | 有效性与验证状态 |
|---|---|---|---|
| 车速 | D.SpeedKmh | km/h，不转换 | 样本 0；合法零值保留 |
| 挡位 | D.Gear | 字符串，不转换 | 使用标准挡位，避免原始枚举偏移 |
| 转速 | D.Rpms | rpm | 样本 1918 |
| 转速上限 | D.CarSettings_MaxRPM；备选 GameRawData.StaticInfo.MaxRpm | rpm，需 >1000 | 样本 7583；禁止使用异常的 R.currentMaxRpm |
| 油门/刹车 | D.Throttle / D.Brake | 0–100% | 标准属性；零值有效，动态响应待驾驶复核 |
| 离合* | D.Clutch | SimHub 0–100 原值 | 样本标准值 100 / 原始值 0，方向未确认；明确标注原值 |
| 胎压 | D.TyrePressure + 四轮后缀 | 根据 D.TyrePressureUnit：Psi 原值；kPa×0.14503773773；bar×14.503773773 | 样本约 26.0 psi；未知单位不显示 |
| 制动温度 | D.BrakeTemperature + 四轮后缀 | D.TemperatureUnit 为 Celcius 时原值；Fahrenheit 用 (x−32)×5/9 | 样本约 19.28°C；标准值已转换，禁止重复减去 273.15 |
| 胎温 | D.TyreTemperature + 四轮后缀 | 同上 | 样本约 20°C；2026-10-09已实测前轮46.7/42.8、后轮15.5/14.5°C；不用于抓地力告警 |
| 四轮载荷 | R.WheelLoad01…04 | N÷1000 → kN | 样本约 6.40 / 1.40 / 4.39 / 2.76；条显示 0–15 kN，非健康百分比 |
| 悬挂 | R.SuspensionTravel01…04 | m×1000 → mm | 样本约 83.6 / 27.5 / 47.9 / 56.2；条显示 ±150 mm，非故障阈值 |
| 滑移 | R.WheelSlip01…04 | 原值 | 不转换为抓地力或健康百分比 |
| 水温 | D.WaterTemperature | 标准 °C；华氏按上述公式转换 | 样本 71.37°C；原始 R.waterTemperature 344.52 K 仅用于零值有效性判断 |
| 燃油 | D.Fuel | L | 样本 30；不估算续航 |
| 前制动比例 | D.BrakeBias | 0–1 时×100，其他值按 % | 样本 52% |
| 转向 | R.SteerAngle | ×100，左负右正 | 2026-10-07停车实测端点−1/+1，已启用 |
| G 值 | R.AccG01 / R.AccG03 | 横向=−AccG01；纵向=AccG03；原值已为G | 2026-10-07实测确认，已启用；不再除以9.80665 |
| 地图 | D.MapAllowed + 有效坐标和路线 | 不推算路线或进度 | 样本 MapAllowed=true 但坐标和路线缺失，默认禁用并显示驾驶摘要 |
| 车辆/赛段 | D.CarModel / D.TrackName | 文本 | 乱码替代字符会回退为提示文字 |
| 计时/最高速度 | 本仪表 root 状态 | 移动后累计有效驾驶时间、当前会话峰值 | 明确标为本次驾驶计时；暂停不累计；无 PB、领先差、剩余距离 |

统一有效性：`DataCorePlugin.GameRunning=true`、`DataCorePlugin.CurrentGame=AssettoCorsaRally`、有效 R.PacketId；连续 3 秒包编号未变化则提示遥测暂未更新并隐藏数值/曲线。退出、换车辆/赛段或包编号回退时重置本次驾驶摘要。速度、油门、刹车的 0 不表示缺失。

手刹、油温、油压、增压、车损、轮胎磨损没有加入未验证绑定。缺失字段显示 —，不设置通用 GT 胎压/温度报警阈值。

2026-10-07采样确认油门/刹车/离合0–1变化、四轮载荷和悬挂变化，以及转向值变化；缺少动作时间标注，尚不能验证离合方向、左右符号、G单位与轴向。原始结构参考 [ACR共享内存采集实现](https://github.com/albertowd/live-telemetry-evo/blob/develop/src/live_telemetry_evo/sources/acrally.py)，第三方针对相邻游戏的轴向假设没有直接照搬。

动态校准后才能更改 `src/acr.js` 的 `ACR_VERIFIED` 开关。修改时同步此表及 PROJECT_STATUS.md，然后重新生成和安装。

2026-10-09内部进程调查：ABS/TCS选择档位已在本次进程的两份结构确认，int32原值+1；独立模式开关为uint8 0/1。此项尚未接入SimHub，也没有跨重启定位，不能开启ACR_CONTROL_SUPPORT的absMode/tcMode。具体地址、受控快照和有限读取工具见内部内存读取说明.md；它们不是Physics.abs/tc或实时介入属性。


