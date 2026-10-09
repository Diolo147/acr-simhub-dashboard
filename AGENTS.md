# Agent 工作说明

用中文与用户沟通。每次修改都更新 PROJECT_STATUS.md，区分已验证事实与研究计划，保持现有 V1–V4/test 仪表。

当前 v2.5；入口 README.md、ROADMAP.md、PROJECT_STATUS.md 最新段落与 ABS-TCS插件说明.md。运行读取器是 src/plugin/AutoControlMemoryReader.cs；ControlMemoryReader.cs 保留共用快照类型及历史固定地址原型，不再是插件运行路径。

仪表使用 SimHub 原生组件，默认 2560×1080，保持 3440×1440 比例兼容，不引入网页或常驻 Python。字段有效性、零值、单位、轮位及校准约定见 FIELD_MAP.md。新增功能只接入有受控实验依据的字段。

本机路径 I:\code\simhub-dashboard；Python I:\ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe；SimHub C:\Program Files (x86)\SimHub。本机也有 pwsh7。脚本当前含本机路径，换环境先审查。游戏配置 image 可修改安装路径，未知 exe 哈希必须重新适配，不能放宽校验。

修改 JS 后更新 build 中扩展并运行 work/verify-bindings.cjs。修改组件运行 src/build_dashboard.py，再进行原生加载和所需尺寸的渲染。修改插件运行 work/build-controls-plugin.ps1；活游戏读测需同次新样本，不能拿旧 RPM/fuel 夹具测试正在驾驶的车辆。安装 DLL 前正常退出 SimHub，勿强杀游戏。

用户不希望电脑控制阻碍操作；有限读取及文件/API操作优先，界面动作保持少量、观察后执行。研究采样必须有限时，不发布完整进程转储或本机凭据。原始大候选/第三方参考/备份留本机并在 .gitignore 排除。

旧 work/finalize-controls-delivery.py 会断言旧设置并写回 v2.4 文案，不要运行。新 finalize-auto-delivery.py 也只用于当次实机交付，不要在未知游戏状态下运行覆盖证据；新增状态段落要保留当前 GitHub 提交记录。
