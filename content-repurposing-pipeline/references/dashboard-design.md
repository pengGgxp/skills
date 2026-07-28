## Design Context

### Users

The primary user is the content-workspace owner, working alone on a personal publishing pipeline. The core job is to scan article status, open the exact pending draft, read long-form content, and then state review decisions in the conversation.

### Brand Personality

Quiet, practical, and editorial. The interface should feel like a focused personal workbench: trustworthy and composed, never corporate, promotional, playful, or ceremonious.

### Aesthetic Direction

Preserve the existing light, paper-tinted interface with restrained green, blue, amber, and red status accents. Favor strong typographic hierarchy, compact controls, mostly square corners, and generous reading space. Avoid gradients, decorative cards, oversized headings, dark terminal styling, and ornamental motion.

### Implementation Defaults

The dashboard is the bundled static asset `assets/dashboard/index.html`, using semantic HTML, plain CSS, and vanilla JavaScript. The selected workspace's `dashboard/data.json` is the only workflow-state source. There is no build step, component library, form framework, table library, or virtualization layer. Prefer native browser controls such as `dialog`, `button`, and `input`, then add small progressive enhancements for focus and responsive behavior.

### Design Principles

- Keep the queue compact; move deep reading into a dedicated surface.
- Make status understandable through words and structure, not color alone.
- Use native semantics and preserve keyboard focus across every overlay transition.
- Keep the dashboard read-only; never imply that viewing content records a decision.
- Optimize for long-form reading on both desktop and mobile before adding visual polish.
