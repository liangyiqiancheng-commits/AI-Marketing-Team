# AI-Marketing-Team
AI_Marketing_Team 是一套完整的本地 AI 营销自动化系统，专为中小团队和个人创作者设计。通过 Claude Code Skills + Agents + Workflows 的架构，实现从品牌调研到内容产出的全链路自动化。
# 🤖 AI Marketing Team

<div align="center">

**本地 AI 营销自动化系统** — 一键驱动品牌调研 → 文案生成 → 图片创作 → SEO 优化

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Skills%20%2B%20Agents-green.svg)](https://claude.ai/code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Agnes AI](https://img.shields.io/badge/API-agnes--ai-orange.svg)](https://apihub.agnes-ai.com)

[中文文档](#-项目概述) · [快速开始](#-快速开始) · [模块详解](#-模块详解) · [贡献指南](#-贡献指南)

</div>

---

## 📋 项目概述

`AI_Marketing_Team` 是一套完整的本地 AI 营销自动化系统，专为中小团队和个人创作者设计。通过 **Claude Code Skills + Agents + Workflows** 的架构，实现从品牌调研到内容产出的全链路自动化。

### ✨ 核心能力

| 能力 | 说明 | 对应模块 |
|------|------|---------|
| 🎯 品牌调研 | 自动化品牌简报生成 | `brand-setup` Skill |
| ✍️ 文案生成 | 小红书/抖音/朋友圈多平台文案 | `ad-copy` Skill |
| 🎨 AI 作图 | 通过 Agnes AI API 生成营销图片 | `image-gen` Skill |
| 🔍 SEO 优化 | 关键词策略 + 内容优化 | `seo-expert` Agent |
| 🔄 全流程串联 | 品牌→文案→图片→SEO 一键跑通 | `full-marketing-campaign` Workflow |
| 📅 内容排期 | 周度内容计划 + 批量生成 | `weekly-content-plan` Workflow |

---

## 🗂️ 目录结构

```
My_AI_Marketing_Team/
│
├── .claude/                              # Claude Code 配置
│   ├── skills/                           # 技能库
│   │   ├── brand-setup/                  # 品牌调研 Skill
│   │   ├── ad-copy/                      # 文案生成 Skill
│   │   └── image-gen/                    # 图片生成 Skill
│   ├── agents/                           # 专家 Agent
│   │   ├── image-expert.md               # 图片生成专家
│   │   └── seo-expert.md                 # SEO 优化专家
│   ├── workflows/                        # 工作流
│   │   ├── full-marketing-campaign.md    # 完整营销活动
│   │   └── weekly-content-plan.md        # 周度内容计划
│   └── hooks/                            # 自动化钩子
│
├── scripts/                              # Python 脚本
│   ├── agnes_client.py                   # Agnes AI API 封装
│   ├── batch_generate.py                 # 批量图片生成
│   ├── file_utils.py                     # 文件读写工具
│   └── image_downloader.py               # 图片下载保存
│
├── input/                                # 参考知识库
│   ├── brand_reference/                  # 品牌资料
│   ├── copy_reference/                   # 文案素材
│   └── image_reference/                  # 视觉风格指南
│
├── output/                               # 输出归档
│   ├── brand_guides/                     # 品牌简报
│   ├── copy_results/                     # 文案输出
│   ├── images/                           # 图片输出
│   └── reports/                          # 报告输出
│
├── .env                                  # 🔒 环境变量
├── .gitignore                            # Git 忽略规则
├── requirements.txt                      # Python 依赖
└── README.md                             # 本文件
```

---

## 🚀 快速开始

### 1️⃣ 环境准备

```bash
# 克隆项目
git clone https://github.com/your-username/My_AI_Marketing_Team.git
cd My_AI_Marketing_Team

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2️⃣ 配置 API Key

编辑 `.env` 文件，填入你的 Agnes AI API Key：

```bash
# 复制模板并修改
cp .env.example .env

# 编辑 .env，填入你的密钥
# AGNES_API_KEY=sk-你的实际密钥
```

> 💡 获取 API Key：访问 [Agnes AI](https://apihub.agnes-ai.com) 注册并获取

### 3️⃣ 填写品牌资料

编辑 `input/brand_reference/company_profile.txt`，填写你的公司/品牌基本信息。

### 4️⃣ 启动 Claude Code

```bash
# 在项目中启动 Claude Code
claude
```

**常用命令示例：**

```bash
# 运行完整营销活动（品牌→文案→图片→SEO）
"运行完整营销活动"

# 单独执行品牌调研
"帮我做一次品牌调研"

# 生成小红书文案
"帮我写3条小红书种草文"

# 生成配图
"生成一张小红书封面图，风格用 brand-default"

# 制定周度内容计划
"制定下周的内容排期"
```

---

## 📖 模块详解

### Skills（技能）

每个 Skill 是一个独立的可复用能力单元：

| Skill | 功能 | 触发词 | 产出 |
|-------|------|--------|------|
| [brand-setup](./.claude/skills/brand-setup/SKILL.md) | 品牌调研与简报生成 | "品牌调研" | `output/brand_guides/*_brand_brief_*.md` |
| [ad-copy](./.claude/skills/ad-copy/SKILL.md) | 营销文案生成 | "写文案" | `output/copy_results/*.md` |
| [image-gen](./.claude/skills/image-gen/SKILL.md) | AI 图片生成 | "生成图片" | `output/images/*.png` |

### Agents（专家）

Agent 是具有深度领域知识的虚拟专家：

| Agent | 领域 | 核心能力 |
|-------|------|---------|
| [image-expert](./.claude/agents/image-expert.md) | 图片生成 | Prompt 工程、品牌视觉一致性、质量把控 |
| [seo-expert](./.claude/agents/seo-expert.md) | SEO 优化 | 关键词策略、平台 SEO、竞品分析 |

### Workflows（工作流）

Workflow 串联多个 Skill/Agent，实现端到端的自动化流程：

| Workflow | 流程 | 触发词 |
|----------|------|--------|
| [full-marketing-campaign](./.claude/workflows/full-marketing-campaign.md) | 品牌→文案→图片→SEO→汇总 | "完整营销活动" |
| [weekly-content-plan](./.claude/workflows/weekly-content-plan.md) | 调研→排期→批量生成 | "周度内容计划" |

---

## 🔧 API 接口

### Agnes AI 图片生成

`scripts/agnes_client.py` 封装了完整的 API 调用逻辑：

```python
from scripts.agnes_client import generate_image

# 生成一张图片
result = generate_image(
    prompt="A beautiful product photo, clean background, professional lighting",
    size="1024x1024",
)

if result["success"]:
    print(f"图片已保存至: {result['images'][0]['local_path']}")
```

**API 配置：**
- **Base URL**: `https://apihub.agnes-ai.com/v1`
- **格式**: OpenAI 兼容（`POST /v1/images/generations`）
- **认证**: `Bearer Token`

**特性：**
- ✅ 自动重试机制（最多 3 次，指数退避）
- ✅ 自动保存到 `output/images/`
- ✅ 元数据记录到 `_metadata.json`
- ✅ 支持 URL 和 Base64 双模式

---

## 📝 输入文件说明

| 文件 | 说明 |
|------|------|
| `input/brand_reference/company_profile.txt` | 品牌基础信息，调研输入 |
| `input/copy_reference/hooks.txt` | 20个爆款文案钩子模板 |
| `input/copy_reference/competitor_ads.txt` | 竞品广告文案收集 |
| `input/image_reference/style_guide.txt` | 品牌视觉风格定义 |

---

## 📊 输出文件说明

所有生成内容自动归档到 `output/` 对应子目录：

| 目录 | 内容 | 格式 |
|------|------|------|
| `output/brand_guides/` | 品牌简报 | Markdown |
| `output/copy_results/` | 营销文案 | Markdown |
| `output/images/` | AI 生成图片 | PNG + JSON 元数据 |
| `output/reports/` | SEO 报告 / 活动总结 | Markdown |

---

## ⚙️ 自定义指南

- **添加新的风格预设**：编辑 `.claude/skills/image-gen/config/style_presets.json`
- **添加新的 Hook 模板**：编辑 `input/copy_reference/hooks.txt`
- **修改品牌声音**：更新 `output/brand_guides/` 下的最新品牌简报
- **配置自动化钩子**：编辑 `.claude/hooks/hooks.json`

---

## 🔒 安全注意事项

1. **`.env` 文件**包含 API 密钥，已加入 `.gitignore`，不会提交到版本控制
2. **不要**将 API Key 硬编码在任何代码文件中
3. **如果**密钥泄露，立即到 Agnes AI 平台重置
4. **生成内容的版权**遵循 Agnes AI 服务条款

---

## 🐛 问题反馈 & 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 License

MIT License — 自由使用、修改和分发。

---

## 🙏 致谢

- [Agnes AI](https://apihub.agnes-ai.com) — 图片生成 API
- [Claude Code](https://claude.ai/code) — AI 编程助手框架

---

<div align="center">
Made with ❤️ by AI Marketing Team<br>
Build your brand with AI automation 🚀
</div>
