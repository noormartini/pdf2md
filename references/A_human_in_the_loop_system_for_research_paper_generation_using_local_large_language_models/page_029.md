```
11
12 ### Abstract
13 ...
14 ### Introduction
15 ...
16 ### Related Work
17 ...
18 ### Methods
19 ...
20 ### Results
21 ...
22 ### Discussion
23 ...
24 ### Conclusion
25 ...
26 ### Acknowledgments
27 ...
```

**Source Code 4.1**: Structure of the paper_specification.md template. The file is divided into a general information section for the main topic and hypothesis, followed by headers for section-specific instructions.

Without this paper specification, the system has no basis for generating a research context. Structuring the specification by section gives the LLM a more focused prompt for each part of the paper.

Besides the specification, the user can optionally define writing style guidelines and provide code and dataset files. The style guidelines are defined in a separate Markdown file. They enable the user to define, for each section, how long it should be, what writing style to use and how it should be structured. As with the paper specification, the file is structured in segments using headers for each section. The style guidelines are used for the paper writing phase to keep the generated text aligned with the user's preferences. They are kept in a separate file because the paper specification is also used in earlier phases like context analysis and experimentation, where writing style is not relevant.

Code and dataset files can both be added via the graphical user interface (GUI) and are used in two ways. During context analysis, the system reads them to gain a better understanding of the user's research. For the experimentation phase, the LLM can import existing code directly and gets information on how to load each dataset from the generated load instructions.

**Code and Dataset Analysis** Code files are analyzed by an LLM. For each file, it is instructed to generate a technical summary and extract important code snippets that implement core logic. The files are processed one by one to keep each prompt shorter and more
