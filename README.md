# Skills

这是我的个人 Agent Skills 仓库，用于集中保存、整理和维护日常使用的 Skill。仓库同时包含自建 Skill 和经来源、版本、许可证核验后收录的第三方 Skill。

当前快照日期为 **2026-10-27**，共收录 **54 个用户级 Skill**：

| 分组 | 数量 | 类型 | 来源 | 许可证 |
| --- | ---: | --- | --- | --- |
| 自建 Skill | 6 | 自建 | 本仓库与本机协作维护 | 尚未单独声明 |
| Layers of Product Design | 9 | 收录 | [jamiemill/layers-skills](https://github.com/jamiemill/layers-skills/tree/a201dc8c2011940b9d93934abb0f40c3b226c7ca) | [MIT](./licenses/layers-skills-LICENSE.txt) |
| Owl Designer Skills | 14 | 收录 | [Owl-Listener/designer-skills](https://github.com/Owl-Listener/designer-skills/tree/acc3e574b36ef2895268a176dbae886e1b845ae0) | [MIT](./licenses/designer-skills-LICENSE.txt) |
| better-web-ui | 10 | 收录 | [aladicf/better-web-ui](https://github.com/aladicf/better-web-ui/tree/af21dcfa71d83104a9e0beb04ffedf79f800f53c) | [自定义许可证](./licenses/better-web-ui-LICENSE.txt) |
| HyperFrames Skills | 9 | 收录 4 / 改编 5 | [heygen-com/hyperframes v0.7.55](https://github.com/heygen-com/hyperframes/tree/c830aa83c588b755552eb3725ea2d8e0bb3dd2c8) | [Apache-2.0](./licenses/hyperframes-LICENSE.txt) |
| guizang-ppt-skill | 1 | 收录 | [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill/tree/6bfa520b86ed5a3dffdac0a3323155e2b6f516b6) | [MIT](./guizang-ppt-skill/LICENSE) |
| Matt Pocock Skills | 3 | 收录 | [mattpocock/skills v1.1.0](https://github.com/mattpocock/skills/tree/d574778f94cf620fcc8ce741584093bc650a61d3) | [MIT](./licenses/mattpocock-skills-LICENSE.txt) |
| Obsidian Skills | 1 | 收录 | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills/tree/a1dc48e68138490d522c04cbf5822214c6eb1202) | [MIT](./licenses/obsidian-skills-LICENSE.txt) |
| Agently Mail | 1 | 收录 | [agent.qq.com](https://agent.qq.com/.well-known/skills/agently-mail/SKILL.md) | 待确认 |

完整的来源、固定提交和版权信息见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。

## 收录范围

本仓库收录本机可独立携带的用户级 Skill：

- `%USERPROFILE%\.codex\skills` 下除 `.system` 外的 Skill；
- `%USERPROFILE%\.agents\skills` 下的 Skill；
- `%USERPROFILE%\.codex\skills` 中指向 `%USERPROFILE%\.cc-switch\skills` 的当前启用链接；收录时解析真实目录，并逐项固定上游版本和许可证，不复制链接或 cc-switch 配置。

Codex 的 `.system`、插件缓存和 `vendor_imports` 不属于可移植的用户级安装内容，因此没有复制。它们可能依赖宿主工具、插件命名空间和插件级共享资源，也可能受专有或禁止提取的许可证约束。详见下方“未收录内容”。

## 版本维护

入库的第三方 Skill 默认优先跟踪最新稳定 release/tag；没有有效稳定版本时才固定默认分支 HEAD。每次复核同时检查稳定版与 HEAD，并始终记录不可变 commit，不使用浮动的 `latest`。若最新版因许可证、资产授权、宿主依赖或兼容性不能安全收录，则保留最近可用版本，并在 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) 记录例外原因和复核日期。详细规则见 [AGENTS.md](./AGENTS.md)。

## 入口与依赖

- [`content-repurposing-pipeline`](./content-repurposing-pipeline/) 是内容复用工作流的**编排/执行 Skill**。它先按需完成选题调研与传播角度筛选，再在当前内容 workspace 中组织母稿、来源、图片、多平台版本和 `dashboard/data.json`；Skill 自带模板、16 个按需加载的平台写作 profile、只读看板和运行脚本，Git 只是可选同步方式。用户只需调用这一入口：完整母稿在事实边界形成后内部路由一次 [`edit-article-spine`](./edit-article-spine/) 编辑，中文平台稿在适配后再做平台感知的局部检查，然后由一个轻量独立审稿子智能体完成事实回归、盲读、残留模板模式和视觉 QA。流程仍只有“母稿审核、平台稿发布审核”两个人工节点。文章配图按需调用 `image2-api-generator`、`guizang-ppt-skill` 和 `chrome:control-chrome`。它不是其他 Skill 的前置依赖。
- [`edit-article-spine`](./edit-article-spine/) 是独立的长文**编辑方法 Skill**，可单独用于只读诊断、结构重建、局部修复和基于真实样稿的声音校准；它也是 `content-repurposing-pipeline` 完整母稿编辑阶段的实际依赖。
- [`evidence-first-product-design`](./evidence-first-product-design/) 是本仓库的主要**入口/编排 Skill**。它会根据任务选择少量相关 Skill，但不是使用其他 Skill 前必须调用的前置步骤。
- [`layers-intro`](./layers-intro/) 是 Layers of Product Design 的**框架入口和真实前置依赖**；使用其他 `layers-*` Skill 前应先加载它。
- `frontend-design` 会按需引用 `clarify`、`animate` 和 `optimize`，但并不要求每次前端任务都调用这三个 Skill。
- `grill-me` 是 `grilling` 的兼容入口，实际执行依赖 `grilling`，安装时应成对保留。
- `hyperframes` 是视频任务入口和路由器；官方核心集还包括 `hyperframes-animation`、`hyperframes-cli`、`hyperframes-core`、`hyperframes-creative`、`hyperframes-keyframes`、`hyperframes-registry` 和 `media-use`，安装时应一起保留。`remotion-to-hyperframes` 只在明确迁移 Remotion 源码时调用。
- `hyperframes` 会按需通过上游 CLI 安装未入库的专项 workflow。它们不是本仓库核心集的静态前置依赖；运行 `npx hyperframes skills update` 会从上游恢复官方完整 `media-use`，包括本仓库因再分发信息不足而删除的 SFX 音频。

“角色”描述 Skill 如何参与工作流，“类型”描述它的来源。入口、编排或前置关系不会改变其“自建/改编/收录”类型。

## Skill 索引

### 自建 Skill

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`chinese-work-writing`](./chinese-work-writing/) | 起草、审阅和改写中文项目汇报、方案说明与工作总结，调整结构、标题、句法和信息取舍 | 方法/写作 |
| [`content-repurposing-pipeline`](./content-repurposing-pipeline/) | 在当前内容 workspace 中完成选题、自然中文母稿、实机配图、16 个平台版本、独立 QA 和只读状态看板 | 编排/执行 |
| [`edit-article-spine`](./edit-article-spine/) | 保护事实边界，同时重建长文观点脊柱、论证推进、限定条件与真实作者声音 | 方法/编辑 |
| [`evidence-first-product-design`](./evidence-first-product-design/) | 从项目事实和上下文发现出发，按需编排产品策略、概念模型、交互、视觉实现与运行时 QA | 入口/编排 |
| [`image2-api-generator`](./image2-api-generator/) | 通过配置的 OpenAI 兼容 Images API 和固定的 `gpt-image-2` 模型生成并保存栅格图像 | 生成/执行 |
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

来源：[heygen-com/hyperframes v0.7.55](https://github.com/heygen-com/hyperframes/tree/c830aa83c588b755552eb3725ea2d8e0bb3dd2c8)

| Skill | 简介 | 类型 | 角色 |
| --- | --- | --- | --- |
| [`hyperframes`](./hyperframes/) | 为视频、动画和动态图形请求选择 HyperFrames 专项工作流与领域 Skill | 收录 | 入口/导航 |
| [`hyperframes-animation`](./hyperframes-animation/) | 提供动作规则、场景蓝图、转场及 GSAP、Lottie、Three.js 等运行时适配 | 改编 | 方法/实现 |
| [`hyperframes-cli`](./hyperframes-cli/) | 执行初始化、校验、预览、渲染、发布、诊断和云端渲染等 CLI 工作流 | 改编 | 执行 |
| [`hyperframes-core`](./hyperframes-core/) | 定义 HTML composition、时间属性、轨道、子组合、变量和确定性渲染契约 | 收录 | 基础/实现 |
| [`hyperframes-creative`](./hyperframes-creative/) | 负责画面规范、配色、字体、旁白、节拍和品牌风格等创意方向 | 改编 | 方法/设计 |
| [`hyperframes-keyframes`](./hyperframes-keyframes/) | 编写并诊断可 seek 的 2D/3D 关键帧、路径、遮罩、SVG 和 FLIP 动画 | 收录 | 方法/实现 |
| [`hyperframes-registry`](./hyperframes-registry/) | 安装、发现、接入并贡献 HyperFrames registry block 和 component | 收录 | 集成/执行 |
| [`media-use`](./media-use/) | 解析、生成、处理和复用音频、图片、图标、旁白、字幕及调色媒体 | 改编 | 预处理/执行 |
| [`remotion-to-hyperframes`](./remotion-to-hyperframes/) | 将受支持的 Remotion React 视频组合迁移为 HyperFrames HTML 并验证差异 | 改编 | 迁移/验证 |

### guizang-ppt-skill

来源：[op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill/tree/6bfa520b86ed5a3dffdac0a3323155e2b6f516b6)

| Skill | 简介 | 角色 |
| --- | --- | --- |
| [`guizang-ppt-skill`](./guizang-ppt-skill/) | 生成电子杂志或瑞士国际主义风格的单文件横向翻页网页 PPT | 生成/执行 |

### Matt Pocock Skills

来源：[mattpocock/skills v1.1.0](https://github.com/mattpocock/skills/tree/d574778f94cf620fcc8ce741584093bc650a61d3)

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
    $_.Name -notin @('agently-mail', 'content-repurposing-pipeline') -and
    (Test-Path (Join-Path $_.FullName 'SKILL.md'))
  } |
  ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination "$env:USERPROFILE\.codex\skills" -Recurse -Force
  }

Copy-Item .\agently-mail "$env:USERPROFILE\.agents\skills\" -Recurse -Force

$pipelineSource = (Resolve-Path .\content-repurposing-pipeline).Path
$pipelineLinks = @(
  "$env:USERPROFILE\.codex\skills\content-repurposing-pipeline",
  "$env:USERPROFILE\.agents\skills\content-repurposing-pipeline"
)

foreach ($link in $pipelineLinks) {
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $link) | Out-Null
  if (Test-Path -LiteralPath $link) {
    $item = Get-Item -LiteralPath $link -Force
    $isExpectedJunction = $item.LinkType -eq 'Junction' -and
      [IO.Path]::GetFullPath([string]$item.Target) -eq $pipelineSource
    if ($isExpectedJunction) { continue }
    throw "目标已存在且不是预期 junction：$link"
  }
  New-Item -ItemType Junction -Path $link -Target $pipelineSource | Out-Null
}
```

安装后重新启动或重新加载 Agent。不要只复制 `SKILL.md`；部分 Skill 还依赖同目录下的 `references/`、`scripts/`、`assets/` 或 `agents/`。除 `content-repurposing-pipeline` 明确建立 junction 外，其他复制项会成为普通目录。

`content-repurposing-pipeline` 不需要 workspace 配置。各 Agent junction 共享同一份 Skill 代码；AI 以当前任务的内容 workspace 根目录作为脚本工作目录，不向用户索取 workspace 参数，也不搜索父级或相邻目录。Skill 自带目录初始化、校验和只读看板服务，并按需加载共用约束和精确的平台写作 profile；workspace 不要求是 Git 仓库。完整安装会同时复制其内部编辑依赖 `edit-article-spine`，用户仍只调用主流程 Skill；依赖暂时不可用时使用主流程内置的有界回退，不会仅因此永久卡住稿件。运行脚本要求 Python 3.10+ 和 PyYAML；PyYAML 仅用于平台 `meta.yaml` 等内容元数据，不用于选择 workspace。

## 未收录内容

以下用户级 Skill 当前仍在本机，但因来源或再分发条件不足而暂未收录：

- `punkzhou-video-writer`：只找到本机 `local:wenan` 记录，没有可核验的上游 URL 或许可证；
- `website-to-hyperframes`：本机旧版已由上游 `website-to-video` 取代；最新稳定版仍含 19 个 Pixabay 原始 MP3，缺少逐文件作品、作者和来源 URL，不能据现有信息确认可原样再分发；
- `.cc-switch\skills\wenan`：是 `punkzhou-video-writer` 的旧别名副本，目录名与 frontmatter 不一致，也没有单独索引。

以下宿主或运行时内容也没有复制：

- Codex `.system` Skill；
- `openai-bundled`、`openai-api-curated` 和 `openai-primary-runtime` 插件 Skill；
- Codex 的 `vendor_imports` Skill 目录镜像。

原因包括：它们由宿主自动管理、缓存中存在重复版本、部分 Skill 依赖插件级共享资源或 MCP/App 能力，以及部分文件采用专有条款。其中 `documents` Skill 的专用许可证明确禁止将其从服务中提取并保留副本，因此不得复制到本仓库。

## 来源与许可证

- 第三方 Skill 的著作权归原作者所有，使用和分发必须遵循对应许可证；
- better-web-ui 不是标准 MIT，公开分发时必须同时公开完整对应源码，且不得作为闭源、专有或收费产品分发；
- HyperFrames Skill 固定在最新稳定版 `v0.7.55` 的 Apache-2.0 提交；`hyperframes-animation`、`hyperframes-cli`、`hyperframes-creative` 和 `remotion-to-hyperframes` 修正了上游失效的路径、旧命名或命令示例，`media-use` 因音频再分发信息不足删除了上游 SFX 文件，五者标记为改编；
- `guizang-ppt-skill` 保留在 MIT 提交 `6bfa520`：最新稳定 tag 比它更旧，最新 HEAD 只增加赞助信息并改为 AGPL-3.0，没有功能修复。其内置 `motion@11.11.17` 另按 [Motion MIT 许可证](./licenses/motion-11.11.17-LICENSE.md) 分发；
- `chinese-work-writing` 是本机维护的中文工作写作 Skill，按 2026-10-27 的用户级安装版本原样收录，包含入口、改写示例与界面配置；未单独声明许可证；
- `content-repurposing-pipeline` 最初由本机 Skill Workshop 创建，现由本仓库以运行时中立方式维护，可供 Codex、Claude Code、WorkBuddy、OpenClaw 等 Agent 使用；它没有第三方上游、tag、LICENSE 或 NOTICE；
- `edit-article-spine` 是基于本机真实文章编辑问题协作创建的自建 Skill，没有第三方上游、tag、LICENSE 或 NOTICE；
- `image2-api-generator` 是本机协作创建的自建 Skill，没有第三方上游、tag、LICENSE 或 NOTICE；源目录中已配置的 `.env` 未收录，安装后必须在本地单独配置；
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
