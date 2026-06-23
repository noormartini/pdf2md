experimentation, paper writing and document compilation. After each phase, the system
pauses to allow the user to review and edit the generated output before continuing.
## 06
**picture_as_pdf**
Document
Compilation
## 05
**history_edu**
Paper
Writing
## 04
**science**
Experimen-
tation
## 03
**lightbulb**
Hypothesis
Generation
## 02
**menu_book**
Literature
Search
## 01
**search**
Context
Analysis
Figure 1.1: An overview of the system’s research pipeline. Each phase produces artifacts the user can
review and edit before continuing to the next phase.
The research process is split into phases to keep each task smaller and more focused, which
improves the output quality of LLMs [11]. To mitigate hallucinations, each paper section is
drafted, critiqued and revised using text passages retrieved from the downloaded literature.
The system requires no model fine-tuning and allows different models to be assigned to
different phases (for example, a code-specialized model for experimentation and a writing-
focused model for paper sections), so each phase can use the most suitable model available.
Unlike the majority of the reviewed systems, it provides a desktop application interface
and does not require terminal or programming knowledge to use. All six phases use local
open-weight models served through LM Studio for inference, with no data sent to external
LLM services.
The scope of this work covers system design, implementation and a feasibility demon-
stration on a selected topic. It does not cover evaluation on multiple topics, user studies,
or qualitative comparisons with other approaches. The system is evaluated by verifying
eleven requirements and by running an end-to-end demonstration with a qualitative error
analysis.
Chapter 2 introduces the core concepts needed to understand the design of this system.
Chapter 3 reviews existing automated research systems and highlights the gap this work
addresses. Chapter 4 presents the system architecture and design. Chapter 5 describes
how the design was implemented. Chapter 6 tests the system against its requirements
and presents the end-to-end demonstration. Chapter 7 interprets the results and discusses
limitations and alternatives. Chapter 8 summarizes the findings and suggests directions
for future work.
2