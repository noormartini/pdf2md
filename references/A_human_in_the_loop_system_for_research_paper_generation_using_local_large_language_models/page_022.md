**Background Research:** The system then performs FR2 (Literature Search) to gather existing knowledge.

**Hypothesis:** Based on this data, the system performs FR3 (Hypothesis Generation).

**Test:** The evaluation is handled by FR4 (Experimentation), where code is generated and executed.

**Conclusion:** Finally, the results are translated into a document via FR5 (Paper Writing) and FR6 (Document Compilation).

FR7 (Human-in-the-Loop) requires the system to allow the user to review and edit the output at every single one of these stages. FR8 (Model Selection) allows switching between specialized LLMs for different tasks to improve the quality of the output.

Non-Functional Requirements define the quality attributes of the system, rather than specific behaviors [42]. In this work, the focus for non-functional requirements is on data privacy and cost efficiency. NFR1 states that all inference data must be processed locally. NFR2 requires the system to run without inference or API fees by using open-weight models and free APIs only.

Constraints define the technical boundaries of the project [43]. C1 restricts the implementation to a technology that was selected to run on consumer-grade hardware and is described in the following section.

### 4.2 System Architecture

The system architecture combines local open-weight models with a phase-gated pipeline. LLMs are treated as interchangeable components, so the system does not depend on a specific model. The architecture splits the research process into smaller, isolated phases. Each phase reads its inputs from files, executes LLM calls, and writes the results to files. This avoids one single long conversation, which would worsen LLM performance over many turns [21]. As shown in Figure 4.1, the system is divided into four main logical blocks: the frontend, the backend, project data, and external services.

1. **Frontend** — The frontend is the interface of the application and is built with Tkinter, the standard graphical user interface library for Python [44]. It provides a screen for each phase of the pipeline. A settings screen lets the user configure the LLMs to use for each phase. Each phase screen shows the output of its phase, so the user can review and edit it before the next phase runs. This enables the user to catch errors the LLM made before they propagate into the next steps. The interface also allows the user to move back and forth between screens to improve outputs or run a specific phase again. For example, an error
