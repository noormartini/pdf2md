**Design Decisions** The system's HITL implementation is based on three main design choices: file-based artifacts, bidirectional navigation and traceability.

The system uses files as the main interface between the user and the AI. Each phase produces a text file the user can inspect, edit, and approve before the next phase runs. This avoids the performance degradation LLMs experience when maintaining complex state over long multi-turn conversations [21]. Markdown is the core data format because it is human-readable, requires no special tooling, and lets the LLM write formatted text without complex parsing logic. Research data is stored separately from the application logic, so the user can edit any file in an external editor and resume the process without losing context.

The bidirectional navigation lets the user move freely between phases. There is no guarantee that research is linear, since new findings might require rethinking earlier ideas, so the system supports navigation in both directions. The user can return to any earlier phase, update its output, and trigger a regeneration of the following phases. Old results are overwritten automatically, so there is no need to clean up old data manually.

Lastly, this setup provides traceability. If the final result contains errors, it might be difficult to determine which step introduced them. By saving the output of every phase as a separate file, any generated content can be traced back to the exact step where it was created.

### 4.4 Generation Process

This section explains how the system turns an initial research idea into a compiled PDF document. The process consists of six phases: context analysis, literature search, hypothesis generation, experimentation, paper writing and document compilation.

This workflow implements the functional requirements defined in Table 4.1. Each phase handles one specific requirement (FR1 to FR6). Throughout the process, the system enables the user to verify the results (FR7) and keeps their data local (NFR1). The following subsections explain how each phase works, including its inputs, outputs and design choices.

#### 4.4.1 Context Analysis

The first phase turns the user's initial ideas into a structured research context. Before the system can search for related literature, experiment, or write a paper, it needs an understanding of the user's topic.
