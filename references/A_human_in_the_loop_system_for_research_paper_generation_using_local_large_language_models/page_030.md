focused, which in turn reduces complexity and the number of tokens the model has to
process at once.
Dataset files are analyzed programmatically. The system extracts column names, data
types, row counts, and sample values from each dataset. It also generates a load instruction
for each one. The result is a report the LLM can use to understand the dataset without
having to load it into the prompt directly.
Generating the Research Context
The process begins with the user writing the paper
specification and optionally providing style guidelines, code and datasets (see Figure 4.4).
After triggering the automated context analysis, the system first loads and parses the pa-
per specification. If code or datasets were provided, it enters a loop to process each file
individually, until all files are analyzed and the data is merged. The system then generates
the actual research context artifact. With the gathered information, it prompts an LLM to
generate a research description and identify open questions.
The final research context artifact consists of four components:
• Research Description: The LLM processes the user’s data into a structured re-
search description including the domain, research direction, problem definition and
technical approach.
• Code Analysis: The analysis generated from provided code files. If no code files
were provided, this section remains empty.
• Dataset Descriptions: The metadata reports generated from any provided dataset
files. If no datasets were provided, this section also stays empty.
• Open Questions: The LLM generates a list of open questions based on the research
description and the code and dataset reports.
Design Decisions
Forcing the LLM to write a description of the user’s input acts as a test
of its comprehension. If the system misunderstood the research topic, the user can edit the
description or regenerate it with updated inputs. Second, the semantic similarity algorithm
used in the following literature search phase is designed to compare dense, narrative texts.
Translating the user’s raw Markdown text and files into a dense description meets this
requirement.
The optional code analysis step helps the system understand the user’s technical imple-
mentation, which is later reused for the experimentation phase. Open questions are gener-
ated for additional context for the literature search, where they are used to help the LLM
generate more specific search queries. The open questions also show the user what the
20