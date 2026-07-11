# Skills

这是我的个人 Agent Skills 仓库，用于集中保存、整理和维护日常使用的 Skill。仓库同时包含自建 Skill 和经来源、版本、许可证核验后收录的第三方 Skill。

当前快照日期为 **2026-07-11**，共收录 **55 个用户级 Skill**：

| 分组 | 数量 | 类型 | 来源 | 许可证 |
| --- | ---: | --- | --- | --- |
| 自建 Skill | 2 | 自建 | 本仓库与本机协作维护 | 尚未单独声明 |
| Layers of Product Design | 9 | 收录 | [jamiemill/layers-skills](https://github.com/jamiemill/layers-skills/tree/a201dc8c2011940b9d93934abb0f40c3b226c7ca) | [MIT](./licenses/layers-skills-LICENSE.txt) |
| Owl Designer Skills | 14 | 收录 | [Owl-Listener/designer-skills](https://github.com/Owl-Listener/designer-skills/tree/acc3e574b36ef2895268a176dbae886e1b845ae0) | [MIT](./licenses/designer-skills-LICENSE.txt) |
| better-web-ui | 10 | 收录 | [aladicf/better-web-ui](https://github.com/aladicf/better-web-ui/tree/af21dcfa71d83104a9e0beb04ffedf79f800f53c) | [自定义许可证](./licenses/better-web-ui-LICENSE.txt) |
| HyperFrames Skills | 14 | 收录 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/tree/d2b915be9ea1cb0787629c44bb33c0de8e408722) | [Apache-2.0](./licenses/hyperframes-LICENSE.txt) |
| guizang-ppt-skill | 1 | 收录 | [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill/tree/6bfa520b86ed5a3dffdac0a3323155e2b6f516b6) | [MIT](./guizang-ppt-skill/LICENSE) |
| Matt Pocock Skills | 3 | 收录 | [mattpocock/skills](https://github.com/mattpocock/skills/tree/391a2701dd948f94f56a39f7533f8eea9a859c87) | [MIT](./licenses/mattpocock-skills-LICENSE.txt) |
| Obsidian Skills | 1 | 收录 | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills/tree/a1dc48e68138490d522c04cbf5822214c6eb1202) | [MIT](./licenses/obsidian-skills-LICENSE.txt) |
| Agently Mail | 1 | 收录 | [agent.qq.com](https://agent.qq.com/.well-known/skills/agently-mail/SKILL.md) | 待确认 |

完整的来源、固定提交和版权信息见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。

## 收录范围

本仓库收录本机可独立携带的用户级 Skill：

- `%USERPROFILE%\.codex\skills` 下除 `.system` 外的 Skill；
- `%USERPROFILE%\.agents\skills` 下的 Skill；
- `%USERPROFILE%\.codex\skills` 中指向 `%USERPROFILE%\.cc-switch\skills` 的当前启用链接；收录时解析真实目录，并逐项固定上游版本和许可证，不复制链接或 cc-switch 配置。

Codex 的 `.system`、插件缓存和 `vendor_imports` 不属于可移植的用户级安装内容，因此没有复制。它们可能依赖宿主工具、插件命名空间和插件级共享资源，也可能受专有或禁止提取的许可证约束。详见下方“未收录内容”。

## 入口与依赖

- [`evidence-first-product-design`](./evidence-first-product-design/) 是本仓库的主要**入口/编排 Skill**。它会根据任务选择少量相关 Skill，但不是使用其他 Skill 前必须调用的前置步骤。
- [`layers-intro`](./layers-intro/) 是 Layers of Product Design 的**框架入口和真实前置依赖**；使用其他 `layers-*` Skill 前应先加载它。
- `frontend-design` 会按需引用 `clarify`、`animate` 和 `optimize`，但并不要求每次前端任务都调用这三个 Skill。
- `grill-me` 是 `grilling` 的兼容入口，实际执行依赖 `grilling`，安装时应成对保留。
- `hyperframes` 是 Anime.js、CSS、GSAP、Lottie、Tailwind、Three.js、TypeGPU 和 WAAPI 适配 Skill 的共同创作上下文；`hyperframes-media` 在转写和字幕质检流程中还会读取 `hyperframes` 的 transcript guide，因此这类任务应同时安装两者。`hyperframes-cli` 和 `hyperframes-registry` 按具体工作流单独调用。

“角色”描述 Skill 如何参与工作流，“类型”描述它的来源。入口、编排或前置关系不会改变其“自建/改编/收录”类型。

## Skill 索引

### 自建 Skill

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`evidence-first-product-design`](./evidence-first-product-design/) | 从项目事实和上下文发现出发，按需编排产品策略、概念模型、交互、视觉实现与运行时 QA | 入口/编排 |
| [`windows-c-drive-cleanup`](./windows-c-drive-cleanup/) | 为中文 Windows 初学者安全扫描和清理 C 盘，并给出常见国内应用缓存与习惯修复建议 | 诊断/执行 |

### Layers of Product Design

来源：[jamiemill/layers-skills](https://github.com/jamiemill/layers-skills/tree/a201dc8c2011940b9d93934abb0f40c3b226c7ca)

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`layers-conceptual-model`](./layers-conceptual-model/) | 定义产品对象、关系、状态和统一词汇 | 方法 |
| [`layers-domain`](./layers-domain/) | 梳理领域概念、术语冲突和限界上下文 | 方法 |
| [`layers-interaction-flow`](./layers-interaction-flow/) | 在不预设视觉形式的情况下描述场所、操作、边界和失败路径 | 方法 |
| [`layers-intro`](./layers-intro/) | 介绍七层产品设计框架，并为其他 Layers Skill 提供共同上下文 | 框架入口/前置 |
| [`layers-observed-behaviour`](./layers-observed-behaviour/) | 规划用户研究并形成有证据和置信度的行为洞察 | 方法 |
| [`layers-orient`](./layers-orient/) | 跨七层诊断当前瓶颈并推荐工作重点 | 导航/诊断 |
| [`layers-product-strategy`](./layers-product-strategy/) | 将用户机会连接到业务结果、方案押注和低成本假设验证 | 方法 |
| [`layers-surface`](./layers-surface/) | 依据底层模型审查词汇、一致性、反馈、层级和可访问性 | 方法/审查 |
| [`layers-user-needs`](./layers-user-needs/) | 发现并排序用户需求、痛点和期望 | 方法 |

### Owl Designer Skills

来源：[Owl-Listener/designer-skills](https://github.com/Owl-Listener/designer-skills/tree/acc3e574b36ef2895268a176dbae886e1b845ae0)

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`competitive-analysis`](./competitive-analysis/) | 对竞品的 UX 模式、功能、优势和缺口进行结构化比较 | 方法 |
| [`critique-information-density`](./critique-information-density/) | 审查认知负荷、内容优先级、扫描路径和渐进披露 | 审查 |
| [`design-principles`](./design-principles/) | 制定可用于决策和解决权衡的设计原则 | 方法 |
| [`design-qa-checklist`](./design-qa-checklist/) | 为设计实现一致性建立 QA 检查清单 | QA |
| [`error-handling-ux`](./error-handling-ux/) | 设计错误预防、发现和恢复体验 | 方法 |
| [`form-design`](./form-design/) | 设计低摩擦、可预防错误并引导完成的表单 | 方法 |
| [`information-architecture`](./information-architecture/) | 设计产品内容与功能的结构、层级和导航模型 | 方法 |
| [`jobs-to-be-done`](./jobs-to-be-done/) | 从功能、情绪和社会维度梳理用户待办任务与结果预期 | 方法 |
| [`loading-states`](./loading-states/) | 设计加载、骨架屏和渐进内容展示 | 方法 |
| [`responsive-design`](./responsive-design/) | 设计适配不同屏幕尺寸和输入方式的布局与交互 | 方法 |
| [`search-ux`](./search-ux/) | 设计查找、筛选、失败恢复和结果优化体验 | 方法 |
| [`state-machine`](./state-machine/) | 用有限状态机描述复杂界面的状态、事件和转换 | 建模 |
| [`usability-test-plan`](./usability-test-plan/) | 制定可用性测试任务、指标、参与者标准和主持指南 | 研究 |
| [`visual-hierarchy`](./visual-hierarchy/) | 通过大小、字重、颜色、间距和位置建立视觉层级 | 方法 |

### better-web-ui

来源：[aladicf/better-web-ui](https://github.com/aladicf/better-web-ui/tree/af21dcfa71d83104a9e0beb04ffedf79f800f53c)

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`a11y`](./a11y/) | 系统审查并修复键盘、读屏、对比度、语义和动态效果等可访问性问题 | 审查/修复 |
| [`animate`](./animate/) | 实现有目的的动效、微交互、手势和过渡系统 | 专项实现 |
| [`audit`](./audit/) | 对可访问性、性能、主题、响应式和反模式进行量化技术审计 | 审查 |
| [`clarify`](./clarify/) | 改进 UX 文案、标签、操作提示、错误信息和 CTA | 专项修复 |
| [`critique`](./critique/) | 从层级、信息架构、认知负荷和整体体验进行 UX 评价 | 审查 |
| [`frontend-design`](./frontend-design/) | 创建或重构具有清晰层级和完整实现质量的生产级前端界面 | 基础/实现 |
| [`harden`](./harden/) | 加固错误处理、国际化、文本溢出和边界情况 | 专项修复 |
| [`hierarchy`](./hierarchy/) | 修复主次不清、视觉竞争和操作优先级问题 | 专项修复 |
| [`optimize`](./optimize/) | 诊断并改善加载、渲染、动效、图片和包体积性能 | 专项修复 |
| [`setup`](./setup/) | 收集并持久化受众、品牌、UX 目标和实现偏好等设计上下文 | 上下文准备 |

### HyperFrames Skills

来源：[heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/tree/d2b915be9ea1cb0787629c44bb33c0de8e408722)

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`animejs`](./animejs/) | 让 Anime.js 动画由 HyperFrames 时间轴确定性驱动和逐帧定位 | 适配/实现 |
| [`contribute-catalog`](./contribute-catalog/) | 创建 HyperFrames registry block 或 component，并按上游流程提交贡献 | 贡献/执行 |
| [`css-animations`](./css-animations/) | 让 CSS keyframes 在 HyperFrames 预览与渲染中可确定性 seek | 适配/实现 |
| [`gsap`](./gsap/) | 提供 HyperFrames 中 GSAP tween、timeline、stagger 和性能模式 | 方法/实现 |
| [`hyperframes`](./hyperframes/) | 用 HTML 创建视频、字幕、音频响应效果、文字动画和场景转场 | 基础/编排 |
| [`hyperframes-cli`](./hyperframes-cli/) | 执行 HyperFrames 初始化、校验、检查、预览、渲染和环境诊断 | 执行 |
| [`hyperframes-media`](./hyperframes-media/) | 执行本地 TTS、语音转写和图片或视频背景移除 | 预处理/执行 |
| [`hyperframes-registry`](./hyperframes-registry/) | 安装、发现并接入 HyperFrames registry block 和 component | 集成/执行 |
| [`lottie`](./lottie/) | 将 lottie-web 与 dotLottie 动画接入 HyperFrames 确定性渲染 | 适配/实现 |
| [`remotion-to-hyperframes`](./remotion-to-hyperframes/) | 将受支持的 Remotion React 视频组合迁移为 HyperFrames HTML | 迁移/验证 |
| [`tailwind`](./tailwind/) | 在 HyperFrames 中正确使用 Tailwind CSS v4.2 浏览器运行时 | 适配/实现 |
| [`three`](./three/) | 将 Three.js 场景、相机和动画接入 HyperFrames seek 事件 | 适配/实现 |
| [`typegpu`](./typegpu/) | 将 TypeGPU、WebGPU 和 WGSL 渲染接入 HyperFrames 时间轴 | 适配/实现 |
| [`waapi`](./waapi/) | 将 Web Animations API 动画接入 HyperFrames 确定性逐帧渲染 | 适配/实现 |

### guizang-ppt-skill

来源：[op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill/tree/6bfa520b86ed5a3dffdac0a3323155e2b6f516b6)

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`guizang-ppt-skill`](./guizang-ppt-skill/) | 生成电子杂志或瑞士国际主义风格的单文件横向翻页网页 PPT | 生成/执行 |

### Matt Pocock Skills

来源：[mattpocock/skills](https://github.com/mattpocock/skills/tree/391a2701dd948f94f56a39f7533f8eea9a859c87)

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`grill-me`](./grill-me/) | 作为兼容入口启动 `grilling` 决策访谈 | 入口 |
| [`grilling`](./grilling/) | 逐个追问并解决计划或设计中的关键决策与依赖 | 方法 |
| [`teach`](./teach/) | 在工作区内以任务、资料、课程和学习记录持续教授一个主题 | 编排/执行 |

### Obsidian Skills

来源：[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills/tree/a1dc48e68138490d522c04cbf5822214c6eb1202)

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`obsidian-cli`](./obsidian-cli/) | 通过 Obsidian CLI 读写 vault，并辅助插件与主题开发调试 | 执行 |

### 邮件工具

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`agently-mail`](./agently-mail/) | 通过 `agently-cli` 发送、回复、转发、搜索和读取邮件，并管理附件与收件箱 | 执行 |

## 安装

先在有访问权限的环境中克隆仓库：

```powershell
git clone https://github.com/pengGgxp/skills.git
Set-Location skills
```

安装单个 Codex Skill：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item .\evidence-first-product-design "$env:USERPROFILE\.codex\skills\" -Recurse -Force
```

安装仓库中的全部用户级 Skill：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null

Get-ChildItem -Directory |
  Where-Object {
    $_.Name -ne 'agently-mail' -and
    (Test-Path (Join-Path $_.FullName 'SKILL.md'))
  } |
  ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination "$env:USERPROFILE\.codex\skills" -Recurse -Force
  }

Copy-Item .\agently-mail "$env:USERPROFILE\.agents\skills\" -Recurse -Force
```

复制后重新启动或重新加载 Agent。不要只复制 `SKILL.md`；部分 Skill 还依赖同目录下的 `references/`、`scripts/`、`assets/` 或 `agents/`。该命令恢复为普通目录，不复刻本机 cc-switch 的符号链接布局。

## 未收录内容

以下用户级 Skill 当前仍在本机，但因来源或再分发条件不足而暂未收录：

- `punkzhou-video-writer`：只找到本机 `local:wenan` 记录，没有可核验的上游 URL 或许可证；
- `website-to-hyperframes`：代码可追溯到 HyperFrames 的 Apache-2.0 提交，但目录内 19 个 Pixabay 原始 MP3 缺少逐文件作品、作者和来源 URL，不能据现有信息确认可原样再分发；
- `.cc-switch\skills\wenan`：是 `punkzhou-video-writer` 的旧别名副本，目录名与 frontmatter 不一致，也没有单独索引。

以下宿主或运行时内容也没有复制：

- Codex `.system` Skill；
- `openai-bundled`、`openai-api-curated` 和 `openai-primary-runtime` 插件 Skill；
- Codex 的 `vendor_imports` Skill 目录镜像。

原因包括：它们由宿主自动管理、缓存中存在重复版本、部分 Skill 依赖插件级共享资源或 MCP/App 能力，以及部分文件采用专有条款。其中 `documents` Skill 的专用许可证明确禁止将其从服务中提取并保留副本，因此不得复制到本仓库。

## 来源与许可证

- 第三方 Skill 的著作权归原作者所有，使用和分发必须遵循对应许可证；
- better-web-ui 不是标准 MIT，公开分发时必须同时公开完整对应源码，且不得作为闭源、专有或收费产品分发；
- HyperFrames Skill 固定在 `v0.6.42` 的 Apache-2.0 提交；没有用今天已经重组目录的上游 HEAD 冒充本机版本；
- `guizang-ppt-skill` 固定在仍采用 MIT 的历史提交；当前上游已改用 AGPL-3.0。其内置 `motion@11.11.17` 另按 [Motion MIT 许可证](./licenses/motion-11.11.17-LICENSE.md) 分发；
- `windows-c-drive-cleanup` 是本机协作创建的自建 Skill，没有第三方上游；
- `agently-mail` 的来源可以确认，但其 Skill 文件未声明许可证；在许可证确认前，不应假定拥有公开再分发权；
- 本仓库当前没有统一的根许可证，不会覆盖第三方内容各自的条款。

维护规则见 [AGENTS.md](./AGENTS.md)。

## 目录结构

```text
skills/
├── <skill-name>/
│   ├── SKILL.md
│   ├── agents/       # 可选
│   ├── scripts/      # 可选
│   ├── references/   # 可选
│   └── assets/       # 可选
├── licenses/
├── AGENTS.md
├── NOTICE.md
├── README.md
└── THIRD_PARTY_NOTICES.md
```
