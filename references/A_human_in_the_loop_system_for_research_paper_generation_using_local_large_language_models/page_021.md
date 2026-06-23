The Specification
All system requirements are listed in Table 4.1. They are categorized
into three groups: functional requirements, non-functional requirements and constraints.
Table 4.1: The table lists all eleven system requirements. The requirements are grouped into eight
functional requirements, two non-functional requirements, and one constraint.
ID
Category
Title
Description
FR1
Functional
Context Analysis
The system shall process user data to gener-
ate a structured research topic definition.
FR2
Functional
Literature Search
The system shall query external databases
to retrieve and store metadata and full-text
documents of research papers.
FR3
Functional
Hypothesis
Generation
The system shall derive a formal hypothesis
from the provided context.
FR4
Functional
Experimentation
The system shall generate code, execute it,
and save the execution artifacts (logs, plots,
data).
FR5
Functional
Paper Writing
The system shall generate text sections that
include citations referenced from the re-
trieved literature.
FR6
Functional
Document
Compilation
The system shall compile the generated
content into a PDF document.
FR7
Functional
Human-in-the-
Loop
The system shall persist each phase’s out-
put, so the user can review and edit it be-
tween phases.
FR8
Functional
Model Selection
The system shall allow the assignment of
LLMs to specific tasks (for example coding
versus writing).
NFR1
Non-
Functional
Privacy
The system shall process all inference data
locally.
NFR2
Non-
Functional
Free Execution
The system shall perform all functions free
of charge.
C1
Constraint
Technology Stack
The system shall be implemented using
Python (language), Tkinter (GUI), and LM
Studio (inference engine).
Functional Requirements define the intended behavior of the system [38]. The require-
ments FR1–FR6 mirror the standard scientific method [41] to produce a paper through the
same steps a human researcher would follow:
Observation & Question: The process begins with FR1 (Context Analysis) to define
the research problem.
11