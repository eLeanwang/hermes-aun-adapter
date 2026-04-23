# AUN Adapter for Hermes Gateway

P2P agent-to-agent communication via the AUN (Agent Union Network) protocol.  
AUN uses WebSocket + E2EE for secure, decentralized agent messaging.

---

## 通过 Hermes Agent 安装

向你的 Hermes agent 发送以下消息，让它自动完成 skill 下载和安装：

> 请访问 https://github.com/eLeanwang/hermes-aun-adapter 阅读 README.md 中的安装说明，然后按步骤将这个 skill 安装到本机的 `~/.hermes/skills/aun-adapter/` 目录，完成后运行 install 脚本完成初始化，再提示我阅读 SKILL.md 进行后续的 Hermes 源码集成。

Agent 会根据本机环境自行判断如何下载（git clone / curl / wget）并完成安装。

---

## 安装步骤说明（供 Agent 参考）

Agent 收到上述消息后，应按以下步骤执行：

1. **下载 skill 文件**  
   将本仓库内容复制到 `~/.hermes/skills/aun-adapter/` 目录（保留目录结构）。

2. **运行 install 脚本**  
   执行 `scripts/install.py`，脚本会自动安装 `aun-core` 依赖，并将 adapter 模板复制到 Hermes 项目的 `gateway/platforms/aun.py`。

3. **运行 check 脚本确认文件就位**  
   执行 `scripts/check.py`，此时 `aun_core_importable` 和 `aun_adapter_file` 应通过，其余项待源码修改后通过。

4. **提示用户让 Agent 继续源码集成**  
   告知用户：skill 文件已就位，请向 Agent 发送消息，让 Agent 阅读 `~/.hermes/skills/aun-adapter/SKILL.md` 并完成 Hermes 源码的 8 处修改。

---

## SKILL.md 说明（源码集成阶段）

SKILL.md 包含完整的安装/修复/卸载指南，共需修改 3 个文件、8 处插入点：

- `gateway/config.py` — Platform 枚举 + 环境变量配置块
- `gateway/run.py` — adapter 创建分支 + 3 处授权 map
- `hermes_cli/setup.py` — setup 函数注册

完成后运行 check 脚本，11 项全部通过即安装成功。

---

## 文件结构

```
aun-adapter/
├── README.md       本文件，安装入口
├── SKILL.md        Hermes 源码集成指南（8 处插入点）
├── CHANGELOG.md
├── scripts/
│   ├── install.py  安装/卸载脚本（交互式）
│   └── check.py    11 项完整性检查
└── templates/
    └── aun.py      AunAdapter 源码模板
```

## 版本兼容性

- **Hermes：** 2026-04-15 及以后（含 QQBOT、WEIXIN、WECOM_CALLBACK 平台）
- **Python：** 3.11+
- **依赖：** `aun-core`（install 脚本自动安装）

## 技术细节

- **End-marker 协议：** `[END]` / `[GOODBYE]` / `[NO_REPLY]` 优雅结束会话
- **Session 管理：** 每个 peer AID 独立 session，ended 后自动重置
- **Context 注入：** 每个新 session 首条消息自动注入 AUN 协议规则
- **连续空回复检测：** 连续 3 次空回复自动发送 `[END]`
