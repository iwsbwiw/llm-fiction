# LLM Fiction

## What This Is

一个由 LLM 驱动的沉浸式小说生成与阅读系统。用户输入一句话即可启动一个完整故事，系统在用户阅读时后台预生成下一章节，实现流畅的阅读体验。

个人娱乐项目，无用户系统，配置简单，上手即玩。

## Core Value

**一句话生成小说，边读边生成，沉浸式阅读体验。**

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 用户可以通过一句话启动小说生成
- [ ] 多 Agent 协作：编剧 Agent 规划剧情，写作 Agent 生成内容，审核 Agent 保证连贯性
- [ ] 后台预生成章节（用户读当前章节时，下一章已在生成）
- [ ] 本地存档功能，保存已生成的小说
- [ ] 章节历史，可回看之前章节
- [ ] 极简灰白风格 UI，主页面只有一个输入框
- [ ] 简单配置（.env 文件配置 API Key、模型名、章节长度等）

### Out of Scope

- 用户系统/登录注册 — 个人项目，无需多用户
- 复杂配置界面 — 用户直接编辑配置文件
- 付费/订阅功能 — 个人娱乐用途
- 社交/分享功能 — 纯本地体验

## Context

- 参考项目采用多 Agent 分工模式，包括 Management、Production、Writing、Evaluation 等 Agent
- 目标是快速上线，技术选型优先考虑开发效率
- 前端使用 Streamlit 实现快速开发，与后端统一语言
- 使用 uv 进行 Python 依赖管理

## Constraints

- **Tech Stack**: Python + LangChain + Streamlit + uv
- **LLM Support**: 主流 API（OpenAI、Claude、DeepSeek 等）
- **Configuration**: .env 文件，简单直接
- **UI Style**: 极简灰白风格

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Streamlit 前端 | Python 全栈，快速开发 | — Pending |
| 故事驱动型 Agent | 编剧+写作+审核三层结构，保证故事质量 | — Pending |
| 预生成章节 | 用户无感知等待，流畅阅读 | — Pending |
| .env 配置 | 简单直接，上手即玩 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-24 after initialization*
