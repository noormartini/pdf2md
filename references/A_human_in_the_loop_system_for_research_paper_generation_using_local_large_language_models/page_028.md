User Inputs
The process begins at the application’s start screen, shown in Figure 4.3.
Here, the user can open the settings, edit the paper specification and the style guidelines
file, and optionally upload code and datasets.
Figure 4.3: Start screen of the application, with options to open the settings, edit the paper specifica-
tion and style guidelines, and upload code and datasets.
The only required input is the paper specification. This is a structured Markdown file that
defines the research topic. It is divided into two parts. The first part captures general
information, specifically the research topic and a hypothesis idea, which will be important
for the later experimentation phase. The second part contains a header for each section
of the paper, where the user can add specific instructions for that section, as shown in
Listing 4.1.
1 # Paper Specification
2
3 ## General Information
4
5 ### Topic
6 ...
7 ### Hypothesis
8 ...
9
10 ## Section Requirements
18