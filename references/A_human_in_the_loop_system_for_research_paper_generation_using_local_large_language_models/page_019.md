**Table 3.1**: A comparison of automated research systems. Date refers to the initial submission date of the respective paper. LLM Backend indicates whether the system is designed around cloud APIs or local models for inference. Several cloud-based systems use OpenAI-compatible APIs that could theoretically connect to local endpoints. The column reflects the intended and documented execution environment, not theoretical compatibility. HITL Mode describes how human review is integrated into the workflow. Interface describes the method by which the user interacts with the system.

| System | Date | LLM Backend | HITL Mode | Interface |
|---|---|---|---|---|
| data-to-paper [1] | 2024.04 | Cloud | None / Per-Step Gated | CLI / Desktop App |
| The AI Scientist [2] | 2024.08 | Cloud | None | Code Only |
| CycleResearcher [10] | 2024.10 | Local | None | Code Only |
| Agent Laboratory [3] | 2025.01 | Cloud | None / Per-Phase Gated | CLI |
| The AI Scientist v2 [7] | 2025.04 | Cloud | None | Code Only |
| AI-Researcher [30] | 2025.05 | Cloud | None | Code Only / Web App |
| DeepScientist [34] | 2025.09 | Cloud | Interruptible | TUI / Web App |
| freephdlabor [31] | 2025.10 | Cloud | Interruptible | CLI |
| DLMA [33] | 2025.10 | Cloud | None | N/A |
| Jr. AI Scientist [29] | 2025.11 | Cloud | None | N/A |
| EvoScientist [32] | 2026.03 | Cloud | None / System-Initiated | CLI / TUI |
| HLER [35] | 2026.03 | Cloud | Two Decision Gates | N/A |
| Proposed System | 2026.04 | Local | Per-Phase Gated | Desktop App |

Local LLM execution avoids several problems of cloud-based systems. For example, cost grows with API calls. The AI Scientist reports approximately $15 per paper [2], while a single successful finding in DeepScientist costs upwards of $175 in API calls alone, with total costs for the results presented in its paper reaching approximately $100,000 [34]. Cloud inference also requires sending prompts to third parties. Further, cloud providers could change pricing, rate limits or terms of service at any time, and if the service becomes unavailable, the system becomes unusable.

No reviewed system combines strictly local inference with a phase-gated HITL strategy. The system introduced in this thesis addresses this gap. The following chapter describes its architecture and design decisions in detail.
