# 第三方来源与许可

本文件记录仓库中第三方 Skill 的来源快照。快照日期：**2026-07-13**。

## Layers of Product Design

- 上游仓库：<https://github.com/jamiemill/layers-skills>
- 固定提交：[`a201dc8c2011940b9d93934abb0f40c3b226c7ca`](https://github.com/jamiemill/layers-skills/tree/a201dc8c2011940b9d93934abb0f40c3b226c7ca)
- 许可证：[MIT](./licenses/layers-skills-LICENSE.txt)
- 版权：Copyright (c) 2026 Jamie Mill
- 收录数量：9

收录目录：`layers-intro`、`layers-orient`、`layers-observed-behaviour`、`layers-domain`、`layers-user-needs`、`layers-product-strategy`、`layers-conceptual-model`、`layers-interaction-flow`、`layers-surface`。

## Owl Designer Skills

- 上游仓库：<https://github.com/Owl-Listener/designer-skills>
- 固定提交：[`acc3e574b36ef2895268a176dbae886e1b845ae0`](https://github.com/Owl-Listener/designer-skills/tree/acc3e574b36ef2895268a176dbae886e1b845ae0)
- 许可证：[MIT](./licenses/designer-skills-LICENSE.txt)
- 版权：Copyright (c) 2026 MC Dean
- 收录数量：14

收录目录：`competitive-analysis`、`information-architecture`、`design-principles`、`jobs-to-be-done`、`usability-test-plan`、`state-machine`、`search-ux`、`error-handling-ux`、`loading-states`、`form-design`、`responsive-design`、`visual-hierarchy`、`critique-information-density`、`design-qa-checklist`。

## better-web-ui

- 上游仓库：<https://github.com/aladicf/better-web-ui>
- 固定提交：[`af21dcfa71d83104a9e0beb04ffedf79f800f53c`](https://github.com/aladicf/better-web-ui/tree/af21dcfa71d83104a9e0beb04ffedf79f800f53c)
- 许可证：[better-web-ui License](./licenses/better-web-ui-LICENSE.txt)，这是带有源码公开和禁止闭源收费分发限制的自定义许可证，不是标准 MIT
- 版权：Copyright (c) 2026 better-web-ui contributors
- 收录数量：10

收录目录：`frontend-design`、`setup`、`critique`、`audit`、`hierarchy`、`a11y`、`harden`、`clarify`、`animate`、`optimize`。

仓库根目录的 [NOTICE.md](./NOTICE.md) 和 [上游 NOTICE 副本](./licenses/better-web-ui-NOTICE.md) 记录了 Anthropic better-web-ui、Impeccable、Emil Kowalski、Refactoring UI、Design for Developers 和 Laws of UX 等来源与启发关系。

## HyperFrames Skills

- 上游仓库：<https://github.com/heygen-com/hyperframes>
- 固定版本：`v0.7.55`
- 固定提交：[`c830aa83c588b755552eb3725ea2d8e0bb3dd2c8`](https://github.com/heygen-com/hyperframes/tree/c830aa83c588b755552eb3725ea2d8e0bb3dd2c8)
- 许可证：[Apache License 2.0](./licenses/hyperframes-LICENSE.txt)
- 致谢：[上游 CREDITS](./licenses/hyperframes-CREDITS.md)
- 收录数量：9（原样收录 4，改编 5）

收录目录：`hyperframes`、`hyperframes-animation`、`hyperframes-cli`、`hyperframes-core`、`hyperframes-creative`、`hyperframes-keyframes`、`hyperframes-registry`、`media-use`、`remotion-to-hyperframes`。其中 `hyperframes-animation`、`hyperframes-cli`、`hyperframes-creative`、`media-use` 和 `remotion-to-hyperframes` 为改编，其余目录与固定提交一致。

`licenses/hyperframes-CREDITS.md` 保留上游正文，仅将其中指向根 `LICENSE` 的相对链接改为本仓库的 `hyperframes-LICENSE.txt`，避免复制后的文档链接失效；文件顶部另按 Apache-2.0 要求标注了这项修改。

本次升级按上游官方 core 定义迁移：原 Anime.js、CSS、GSAP、Lottie、Three.js、TypeGPU 和 WAAPI 适配内容已合并到 `hyperframes-animation`，Tailwind 指南已合并到 `hyperframes-core`，catalog 贡献流程已合并到 `hyperframes-registry`，原 `hyperframes-media` 能力由 `media-use` 继承。原已收录的 `remotion-to-hyperframes` 同步升级。

`hyperframes-animation` 基于 `v0.7.55` 改编：修正 10 份 rule/blueprint 文档中 49 处错误的文件路径，使示例、转场、adapter、根 `techniques.md` 和 Three.js 能力引用指向现有文件；没有改变动画工作流。

`hyperframes-cli` 基于 `v0.7.55` 改编：修正 skills 安装说明中已移除的 `-media` 旧命名，补齐 `hyperframes-keyframes` 和 `media-use`，并明确无参数命令安装完整发布集合。

`hyperframes-creative` 基于 `v0.7.55` 改编：只修正 `references/house-style.md` 中 13 处失效的相对链接，使其正确指向同目录的排版和动效资料，以及上一级 `palettes/` 中的配色文件；没有改写上游方法内容。

`media-use` 基于 `v0.7.55` 改编：删除 `audio/assets/sfx/` 中 19 个 Pixabay MP3 及其 manifest，因为上游 `CREDITS.md` 没有提供逐文件作品、作者和来源 URL，且 Pixabay Content License 限制 standalone 原样分发；同时修正 4 处指向根 `SKILL.md` 的相对路径，并修正文档、运行提示和测试，使没有 HeyGen 凭据或用户自备本地素材时明确跳过 SFX，不产生指向缺失文件的记录。显式本地 SFX 库还会校验 manifest 根结构、数值类型和安全音频文件名，拒绝绝对路径、路径穿越、嵌套路径及 Windows 设备名。为让上游已有的 `ffprobe` 时长回退测试可在 Windows 稳定运行，本仓库给相关进程调用增加了可注入参数，并将 TTS 测试 fixture 的路径改为宿主平台格式；运行行为不变。上游自动更新使用官方 manifest hash，运行 `npx hyperframes skills update` 会把本改编版识别为不同版本并恢复官方完整 `media-use`；该行为属于用户从上游直接更新，不代表本仓库重新分发这些音频。

`remotion-to-hyperframes` 基于 `v0.7.55` 改编：修正 `SKILL.md`、eval 指南及 3 个测试 fixture README 中依赖错误当前目录或错误层级的命令，并为每组命令明确运行目录；没有改写迁移规则或评测阈值。

为符合 Apache-2.0 第 4(b) 条，上述所有保留并修改的上游文件都在文件自身顶部携带显著修改声明；删除的音频及 manifest 则在本文件和 `media-use/audio/assets/sfx/CREDITS.md` 中记录。

版本复核于 2026-07-13 完成：`v0.7.55` 是最新稳定版，其解引用提交与默认分支 HEAD 均为 `c830aa83c588b755552eb3725ea2d8e0bb3dd2c8`。上游 `website-to-video` 仍包含同一组 19 个缺少逐文件来源信息的 MP3，本仓库暂不收录。

## guizang-ppt-skill

- 上游仓库：<https://github.com/op7418/guizang-ppt-skill>
- 固定提交：[`6bfa520b86ed5a3dffdac0a3323155e2b6f516b6`](https://github.com/op7418/guizang-ppt-skill/tree/6bfa520b86ed5a3dffdac0a3323155e2b6f516b6)
- 许可证：[MIT](./guizang-ppt-skill/LICENSE)
- 版权：Copyright (c) 2026 op7418 (歸藏)
- 收录数量：1

本机安装内容与该提交中的可分发 Skill 文件一致，没有复制上游仓库的 `.github/` 和根 `.gitignore`。版本复核于 2026-07-13 完成：最新稳定 tag `v1.1.0`（`3652b3c`）比本快照更旧；最新默认分支 HEAD `82fe5ae129e8c2a12e1155fcabed6703342749d6` 只增加赞助信息，并在提交 [`014c572454065e905477a7432ae331dfc0fe6070`](https://github.com/op7418/guizang-ppt-skill/commit/014c572454065e905477a7432ae331dfc0fe6070) 后把许可证从 MIT 改为 AGPL-3.0，没有功能、模板、校验器或可移植性修复。为避免改变模板复制产物的许可义务，本仓库继续保留当前 MIT 快照，并记录为最新版例外。

`guizang-ppt-skill/assets/motion.min.js` 是 jsDelivr 生成的 `motion@11.11.17` bundle。其上游为 [motiondivision/motion v11.11.17](https://github.com/motiondivision/motion/tree/ac650311b4ad8e65373ef96686d229cdf583bee1)，许可证为 [MIT](./licenses/motion-11.11.17-LICENSE.md)，版权为 Copyright (c) 2018 Framer B.V.

已知上游可移植性限制：Skill 的瑞士风格 QA 文档仍引用作者机器上的 golden source 绝对路径，该文件不在发布目录内；随附 `assets/template-swiss.html` 的封面和尾页示例也没有声明校验器要求的 `data-layout`，因此模板原文件不能直接通过 `validate-swiss-deck.mjs`。仓库保持第三方快照原样，没有把这些内容改写为未经上游确认的替代版本。

## Matt Pocock Skills

- 上游仓库：<https://github.com/mattpocock/skills>
- 固定版本：`v1.1.0`
- 固定提交：[`d574778f94cf620fcc8ce741584093bc650a61d3`](https://github.com/mattpocock/skills/tree/d574778f94cf620fcc8ce741584093bc650a61d3)
- 许可证：[MIT](./licenses/mattpocock-skills-LICENSE.txt)
- 版权：Copyright (c) 2026 Matt Pocock
- 收录数量：3

收录目录：`grill-me`、`grilling`、`teach`。`grill-me` 是调用 `grilling` 的兼容入口，两者应成对安装。

版本复核于 2026-07-13 完成：三个收录目录在 `v1.1.0` 与默认分支 HEAD `391a2701dd948f94f56a39f7533f8eea9a859c87` 的 tree 完全一致；本仓库按稳定版优先策略固定到 `v1.1.0`。

## Obsidian Skills

- 上游仓库：<https://github.com/kepano/obsidian-skills>
- 固定提交：[`a1dc48e68138490d522c04cbf5822214c6eb1202`](https://github.com/kepano/obsidian-skills/tree/a1dc48e68138490d522c04cbf5822214c6eb1202)
- 许可证：[MIT](./licenses/obsidian-skills-LICENSE.txt)
- 版权：Copyright (c) 2026 Steph Ango (@kepano)
- 收录数量：1

收录目录：`obsidian-cli`。

## Agently Mail

- 原始文件：<https://agent.qq.com/.well-known/skills/agently-mail/SKILL.md>
- 来源类型：`well-known`
- Skill 版本：`1.0.0`
- 本机安装和核验时间：`2026-07-11T00:27:30.488Z`
- 在线复核日期：`2026-07-13`
- 本地文件 SHA-256：`671C363FF3CD653F31678E53DD546BD713A421CFC7674B24DA4B3EF092E2371F`
- 许可证：上游 Skill 文件未声明，待确认

`agently-mail` 使用 `@tencent-qqmail/agently-cli`，但相关 CLI 包的许可证不能自动视为该 Skill 文件的许可证。在上游明确授权前，不应假定该 Skill 可以公开再分发。

## 未收录的本机用户级内容

- `punkzhou-video-writer`：只发现本机 `local:wenan` 安装记录，没有可核验的上游 URL 或许可证；在来源和授权确认前不收录。
- `.cc-switch/skills/wenan`：是 `punkzhou-video-writer` 的旧别名副本，目录名与 frontmatter `name` 不一致，也没有作为独立 Skill 收录。
- `website-to-hyperframes`：本机旧版已由上游 `website-to-video` 取代；后者在 HyperFrames `v0.7.55` 中仍随附再分发信息不完整的 19 个原始音频，暂不收录。

## 未收录的宿主内容

本机的 Codex `.system`、插件缓存和 `vendor_imports` 未复制到仓库。它们是宿主或插件管理的环境内容，不是本仓库的第三方源码来源；其中还包含专有、受开发者条款约束或明确禁止外部提取的文件。
