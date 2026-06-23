# Chapter 4
## System Design
This chapter explains the design and architecture of the automated research paper genera-
tor. It is split into four parts:
1. Requirements: The specific features and constraints the system is built around.
2. System Architecture: The high-level structure of the system.
3. Human-in-the-Loop Strategy: The interaction pattern enabling the user to review
and correct the AI’s output.
4. Generation Process: A detailed explanation of all phases, from the initial context
analysis to the compilation of a PDF document.
4.1 Requirements
The system’s requirements are based on two frameworks, the Volere Template [37] and
IEEE 830 [38]. Only a selection of their elements was chosen to avoid excessive doc-
umentation for a single-developer project with a limited timeframe. These are unique
identifiers, categorization, titles, and deterministic “shall” statements. This makes each
requirement verifiable in the evaluation in Chapter 6.
Scope: System vs. Model
A known challenge in ML systems is distinguishing failures
and behaviors stemming from the software architecture versus the artificial intelligence
(AI) itself [39, 40]. This distinction is necessary for this work, because the quality of a
generated research paper also depends on the intelligence of the specific LLM used, not
just the system architecture. Therefore, the requirements only cover what the system does,
not the quality of the AI’s output. For example, one functional requirement says the system
must generate code, execute it, and save artifacts. It does not require the system to produce
a scientifically valid experiment. This distinction makes it possible to test the system’s
engineering with automated tests, instead of having to conduct qualitative, empirical or
similar studies, which are out of scope for this work.
10