# Prior-art usefulness matrix

This one-page view answers three questions from the 20
[individual prior-art reviews](OTHER_REPOS/): does it solve an active task better, offer a better
pipeline model, or show a useful possibility for Marp and its themes? It does not recommend copying
source or select the extension language. Marp Markdown remains the starting point, not an assumption
of feature completeness, and the repository-owned native exporter remains the rendering boundary.

- **Reuse permitted:** use it as the installed tool, a discovery source, or an upstream behavior
  reference.
- **Ideas only:** retain the lesson and implement it within the existing pipeline.
- **Do not reuse:** its approach creates a major safety or maintainability problem.

| Repository | Decision | Strongest practical lesson | Priority |
| --- | --- | --- | --- |
| `MarpX` | Ideas only | A richer vocabulary of semantic teaching layouts can stay simple in Marp. | Theme study |
| `ai-lesson-planner` | Ideas only | It informs course planning, not a stronger slide-production pipeline. | Reference |
| `awesome-marp` | Reuse permitted | It is a discovery map for bounded future comparisons. | As needed |
| `cdl-slides` | Ideas only | A feature inventory for a smaller extension language, not a compiler to adopt. | Language-design reference |
| `deck2video` | Ideas only | Presenter notes can drive a separate narration-and-video lane. | If asynchronous output matters |
| `lectern-slides` | Ideas only | Source-aware diagnostics and accessibility audits are a stronger quality model. | Next validation work |
| `marp-cli` | Do not reuse | It is excluded from the future extension-language rendering path. | No new work |
| `marp-community-themes` | Ideas only | Preview galleries show small motifs can expand Marp's teaching range. | Theme study |
| `marp-core` | Reuse permitted | It defines the upstream behavior to test during renderer upgrades. | On upgrades |
| `marp-deck-directory` | Ideas only | Output paths and assets need explicit, collision-safe ownership. | When deck count grows |
| `marp-slides` | Ideas only | Its layout catalog demonstrates comparison, sequence, and dashboard possibilities. | Theme study |
| `marp-slides-template` | Ideas only | Browser-measured overflow is the clearest immediate validation improvement. | Now |
| `marp-to-editable-pptx` | Ideas only | A typed model plus visual and structural checks is the right editable-output model. | If editability is required |
| `marp2pptx` | Ideas only | It supplies a contrasting editable-output experiment for a future bakeoff. | If editability is required |
| `my-marp-themes` | Ideas only | Graph-paper and border motifs can support problem-solving slides. | Theme study |
| `odpdown` | Ideas only | Master pages and direct shapes offer a future native-ODP model. | If native ODP is required |
| `ppt2asciidocslides` | Ideas only | A renderer-neutral model confirms the local importer architecture. | Reference |
| `pptx2marp` | Ideas only | Its weaker importer is a useful baseline for protecting local quality. | Reference |
| `slide-ai-agent` | Do not reuse | Its oversized agent platform and unsafe execution model harm maintainability. | No action |
| `slideSonnet` | Ideas only | Stable slide identity, caching, and preflight checks fit a future narration lane. | If narration is required |

The individual reports contain the evidence and constraints behind each practical lesson.
