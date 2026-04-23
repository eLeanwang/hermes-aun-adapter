# AUN Adapter for Hermes Gateway

P2P agent-to-agent communication via the AUN (Agent Union Network) protocol.

## 快速开始

### 1. 解压并安装 skill

```bash
# 解压到 ~/.hermes/skills/
tar -xzf aun-adapter-skill.tar.gz -C ~/.hermes/skills/

# 运行安装脚本
python ~/.hermes/skills/aun-adapter/scripts/install.py
```

### 2. 修改 Hermes 源代码

安装脚本会放置 adapter 文件，但**不会**自动修改 Hermes 源代码。你需要手动执行以下修改（详见 `SKILL.md`）：

1. `gateway/config.py` — 添加 `Platform.AUN` 枚举
2. `gateway/config.py` — 添加 AUN 环境变量配置块
3. `gateway/run.py` — 添加 AUN adapter 创建分支
4. `gateway/run.py` — 添加 AUN 到 3 个授权 map
5. `hermes_cli/setup.py` — 添加 `_setup_aun()` 函数和注册

**重要：** 当前 Hermes 版本（2026-04-15+）新增了第三处授权 map（`_get_unauthorized_dm_behavior()`），必须同时修改。

### 3. 验证安装

```bash
python ~/.hermes/skills/aun-adapter/scripts/check.py
```

所有检查项应显示 ✓（除了 `aun_aid_configured` 需要在 `.env` 中配置 `AUN_AID`）。

## 文件结构

```
aun-adapter/
├── README.md              # 本文件
├── SKILL.md              # 完整安装/卸载指南
├── scripts/
│   ├── install.py        # 安装/卸载脚本（交互式）
│   └── check.py          # 完整性检查脚本
└── templates/
    └── aun.py            # AunAdapter 源代码模板
```

## 版本兼容性

- **Hermes 版本：** 2026-04-15 及以后（包含 QQBOT、WEIXIN、WECOM_CALLBACK 平台）
- **Python：** 3.11+
- **依赖：** `aun-core` (自动安装)

## 已知问题

1. **Hermes 更新覆盖：** `git pull` 更新 Hermes 后，手动修改的源代码会被覆盖。使用 `check.py` 检测并重新应用修改（参考 SKILL.md Repair 章节）。

2. **第三处 map：** 2026-04-15 版本新增了 `_get_unauthorized_dm_behavior()` 方法中的独立 `platform_env_map`，必须同时添加 AUN 条目，否则未授权用户行为不一致。

## 技术细节

- **End-marker 协议：** 支持 `[END]`、`[GOODBYE]`、`[NO_REPLY]` 标记优雅结束会话
- **Session 管理：** 每个 peer AID 独立 session，ended 状态自动重置
- **Context 注入：** 首次消息自动注入 AUN 协议规则（中文）
- **连续空回复检测：** 3 次空回复自动发送 `[END]`

## 支持

- 问题反馈：https://github.com/NousResearch/hermes-agent/issues
- AUN 协议：https://aun.network/
