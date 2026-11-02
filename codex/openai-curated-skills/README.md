# codex / openai-curated-skills

来源：`~\.codex\vendor_imports\skills\skills\.curated (openai/skills 官方精选)`

共 39 项。

| 技能 | 说明 |
| --- | --- |
| aspnet-core | Build, review, refactor, or architect ASP.NET Core web applications using current official guidance for .NET web development. Use when working on Blazor Web App… |
| chatgpt-apps | Build, scaffold, refactor, and troubleshoot ChatGPT Apps SDK applications that combine an MCP server and widget UI. Use when Codex needs to design tools, regist… |
| cli-creator | Build a composable CLI for Codex from API docs, an OpenAPI spec, existing curl examples, an SDK, a web app, an admin tool, or a local script. Use when the user … |
| cloudflare-deploy | Deploy applications and infrastructure to Cloudflare using Workers, Pages, and related platform services. Use when the user asks to deploy, host, publish, or se… |
| define-goal | Help the user define a concrete, measurable goal before starting work, especially when they ask to use the goal tool, create a goal, set an objective, clarify s… |
| figma | Use the Figma MCP server to fetch design context, screenshots, variables, and assets from Figma, and to translate Figma nodes into production code. Trigger when… |
| figma-code-connect-components | Connects Figma design components to code components using Code Connect mapping tools. Use when user says "code connect", "connect this component to code", "map … |
| figma-create-design-system-rules | Generates custom design system rules for the user's codebase. Use when user says "create design system rules", "generate rules for my project", "set up design r… |
| figma-create-new-file | Create a new blank Figma file. Use when the user wants to create a new Figma design or FigJam file, or when you need a new file before calling use_figma. Handle… |
| figma-generate-design | "Use this skill alongside figma-use when the task involves translating an application page, view, or multi-section layout into Figma. Triggers: 'write to Figma'… |
| figma-generate-library | "Build or update a professional-grade design system in Figma from a codebase. Use when the user wants to create variables/tokens, build component libraries, set… |
| figma-implement-design | Translates Figma designs into production-ready application code with 1:1 visual fidelity. Use when implementing UI code from Figma files, when user mentions "im… |
| figma-use | "**MANDATORY prerequisite** — you MUST invoke this skill BEFORE every `use_figma` tool call. NEVER call `use_figma` directly without loading this skill first. S… |
| gh-address-comments | Help address review/issue comments on the open GitHub PR for the current branch using gh CLI; verify gh auth first and prompt the user to authenticate if not lo… |
| "gh-fix-ci" | "Use when a user asks to debug or fix failing GitHub PR checks that run in GitHub Actions; use `gh` to inspect checks and logs, summarize failure context, draft… |
| hatch-pet | Create, repair, validate, visually QA, and package Codex-compatible animated pets and pet spritesheets from character art, generated images, company or prospect… |
| "jupyter-notebook" | "Use when the user asks to create, scaffold, or edit Jupyter notebooks (`.ipynb`) for experiments, explorations, or tutorials; prefer the bundled templates and … |
| linear | Manage issues, projects & team workflows in Linear. Use when the user wants to read, create or updates tickets in Linear. |
| migrate-to-codex | Migrate supported instruction files, skills, agents, and MCP config into Codex project and global files. |
| netlify-deploy | Deploy web projects to Netlify using the Netlify CLI (`npx netlify`). Use when the user asks to deploy, host, publish, or link a site/repo on Netlify, including… |
| notion-knowledge-capture | Capture conversations and decisions into structured Notion pages; use when turning chats/notes into wiki entries, how-tos, decisions, or FAQs with proper linkin… |
| notion-meeting-intelligence | Prepare meeting materials with Notion context and Codex research; use when gathering context, drafting agendas/pre-reads, and tailoring materials to attendees. |
| notion-research-documentation | Research across Notion and synthesize into structured documentation; use when gathering info from multiple Notion sources to produce briefs, comparisons, or rep… |
| notion-spec-to-implementation | Turn Notion specs into implementation plans, tasks, and progress tracking; use when implementing PRDs/feature specs and creating Notion plans + tasks from them. |
| "openai-docs" | "Use when the user asks how to build with OpenAI products or APIs, asks about Codex itself or choosing Codex surfaces, needs up-to-date official documentation w… |
| "pdf" | "Use when tasks involve reading, creating, or reviewing PDF files where rendering and layout matter; prefer visual checks by rendering pages (Poppler) and use P… |
| "playwright" | "Use when the task requires automating a real browser from the terminal (navigation, form filling, snapshots, screenshots, data extraction, UI-flow debugging) v… |
| "playwright-interactive" | "Persistent browser and Electron interaction through `js_repl` for fast iterative UI debugging." |
| render-deploy | Deploy applications to Render by analyzing codebases, generating render.yaml Blueprints, and providing Dashboard deeplinks. Use when the user wants to deploy, h… |
| "screenshot" | "Use when the user explicitly asks for a desktop or system screenshot (full screen, specific app or window, or a pixel region), or when tool-specific capture ca… |
| "security-best-practices" | "Perform language and framework specific security best-practice reviews and suggest improvements. Trigger only when the user explicitly requests security best p… |
| "security-ownership-map" | "Analyze git repositories to build a security ownership topology (people-to-file), compute bus factor and sensitive-code ownership, and export CSV/JSON for grap… |
| "security-threat-model" | "Repository-grounded threat modeling that enumerates trust boundaries, assets, attacker capabilities, abuse paths, and mitigations, and writes a concise Markdow… |
| "sentry" | "Use when the user asks to inspect Sentry issues or events, summarize recent production errors, or pull basic Sentry health data via the Sentry CLI; perform rea… |
| "speech" | "Use when the user asks for text-to-speech narration or voiceover, accessibility reads, audio prompts, or batch speech generation via the OpenAI Audio API; run … |
| "transcribe" | "Transcribe audio files to text with optional diarization and known-speaker hints. Use when a user asks to transcribe speech from audio/video, extract text from… |
| vercel-deploy | Deploy applications and websites to Vercel. Use when the user requests deployment actions like "deploy my app", "deploy and give me the link", "push this live",… |
| winui-app | Bootstrap, develop, and design modern WinUI 3 desktop applications with C# and the Windows App SDK using official Microsoft guidance, WinUI Gallery patterns, Wi… |
| "yeet" | "Use only when the user explicitly asks to stage, commit, push, and open a GitHub pull request in one flow using the GitHub CLI (`gh`)." |
