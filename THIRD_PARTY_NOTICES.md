# 第三方来源与许可

本文件记录仓库中第三方 Skill 的来源快照。快照日期：**2026-07-11**。

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
- 固定版本：`v0.6.42`
- 固定提交：[`d2b915be9ea1cb0787629c44bb33c0de8e408722`](https://github.com/heygen-com/hyperframes/tree/d2b915be9ea1cb0787629c44bb33c0de8e408722)
- 许可证：[Apache License 2.0](./licenses/hyperframes-LICENSE.txt)
- 致谢：[上游 CREDITS](./licenses/hyperframes-CREDITS.md)
- 收录数量：14

收录目录：`animejs`、`contribute-catalog`、`css-animations`、`gsap`、`hyperframes`、`hyperframes-cli`、`hyperframes-media`、`hyperframes-registry`、`lottie`、`remotion-to-hyperframes`、`tailwind`、`three`、`typegpu`、`waapi`。

`licenses/hyperframes-CREDITS.md` 保留上游内容，只将其中指向根 `LICENSE` 的相对链接改为本仓库的 `hyperframes-LICENSE.txt`，避免复制后的文档链接失效。

已知上游可移植性限制：`hyperframes/references/dynamic-techniques.md` 引用了不存在的 `skills/gsap-effects/scripts/extract-audio-data.py`；本快照中的实际脚本路径是 `gsap/scripts/extract-audio-data.py`。仓库保持第三方 Skill 原样，使用该命令时应改用实际路径。

这些目录与固定提交一致。本机当前还启用了同一提交中的 `website-to-hyperframes`，但该目录包含 19 个 Pixabay 原始 MP3；现有 `CREDITS.md` 没有逐文件作品、作者和来源 URL，且 Pixabay Content License 限制 standalone 原样分发，因此本仓库暂不收录该 Skill。

## guizang-ppt-skill

- 上游仓库：<https://github.com/op7418/guizang-ppt-skill>
- 固定提交：[`6bfa520b86ed5a3dffdac0a3323155e2b6f516b6`](https://github.com/op7418/guizang-ppt-skill/tree/6bfa520b86ed5a3dffdac0a3323155e2b6f516b6)
- 许可证：[MIT](./guizang-ppt-skill/LICENSE)
- 版权：Copyright (c) 2026 op7418 (歸藏)
- 收录数量：1

本机安装内容与该提交中的可分发 Skill 文件一致，没有复制上游仓库的 `.github/` 和根 `.gitignore`。上游在提交 [`014c572454065e905477a7432ae331dfc0fe6070`](https://github.com/op7418/guizang-ppt-skill/commit/014c572454065e905477a7432ae331dfc0fe6070) 后改为 AGPL-3.0；本仓库只收录更早、明确采用 MIT 的固定快照。

`guizang-ppt-skill/assets/motion.min.js` 是 jsDelivr 生成的 `motion@11.11.17` bundle。其上游为 [motiondivision/motion v11.11.17](https://github.com/motiondivision/motion/tree/ac650311b4ad8e65373ef96686d229cdf583bee1)，许可证为 [MIT](./licenses/motion-11.11.17-LICENSE.md)，版权为 Copyright (c) 2018 Framer B.V.

已知上游可移植性限制：Skill 的瑞士风格 QA 文档仍引用作者机器上的 golden source 绝对路径，该文件不在发布目录内；随附 `assets/template-swiss.html` 的封面和尾页示例也没有声明校验器要求的 `data-layout`，因此模板原文件不能直接通过 `validate-swiss-deck.mjs`。仓库保持第三方快照原样，没有把这些内容改写为未经上游确认的替代版本。

## Matt Pocock Skills

- 上游仓库：<https://github.com/mattpocock/skills>
- 固定提交：[`391a2701dd948f94f56a39f7533f8eea9a859c87`](https://github.com/mattpocock/skills/tree/391a2701dd948f94f56a39f7533f8eea9a859c87)
- 许可证：[MIT](./licenses/mattpocock-skills-LICENSE.txt)
- 版权：Copyright (c) 2026 Matt Pocock
- 收录数量：3

收录目录：`grill-me`、`grilling`、`teach`。`grill-me` 是调用 `grilling` 的兼容入口，两者应成对安装。

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
- 本地文件 SHA-256：`671C363FF3CD653F31678E53DD546BD713A421CFC7674B24DA4B3EF092E2371F`
- 许可证：上游 Skill 文件未声明，待确认

`agently-mail` 使用 `@tencent-qqmail/agently-cli`，但相关 CLI 包的许可证不能自动视为该 Skill 文件的许可证。在上游明确授权前，不应假定该 Skill 可以公开再分发。

## 未收录的本机用户级内容

- `punkzhou-video-writer`：只发现本机 `local:wenan` 安装记录，没有可核验的上游 URL 或许可证；在来源和授权确认前不收录。
- `.cc-switch/skills/wenan`：是 `punkzhou-video-writer` 的旧别名副本，目录名与 frontmatter `name` 不一致，也没有作为独立 Skill 收录。
- `website-to-hyperframes`：代码来源可以固定到 HyperFrames `v0.6.42`，但随附原始音频的再分发信息不完整，暂不收录。

## 未收录的宿主内容

本机的 Codex `.system`、插件缓存和 `vendor_imports` 未复制到仓库。它们是宿主或插件管理的环境内容，不是本仓库的第三方源码来源；其中还包含专有、受开发者条款约束或明确禁止外部提取的文件。
