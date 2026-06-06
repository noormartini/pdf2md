# Kapitel 2

## Theoretische Grundlagen

### 2.1 Reinforcement Learning

Beim Reinforcement Learning lernt der Agent durch Belohnung und Bestrafung. Der Agent befindet sich in einer Umgebung, welche er erlernen soll. Er hat dabei eine Auswahl an Aktionen, die er ausführen kann. Der Agent wählt die Aktion mit der besten Wahrscheinlichkeit, eine Belohnung zu bekommen, aus. Durch diese Aktion ändert sich der Zustand, in dem sich der Agent befindet. Er kann für diesen neuen Zustand eine Belohnung oder eine Bestrafung bekommen. Durch eine Belohnung lernt er, diesen Zustand zu wählen und durch eine Bestrafung diesen Zustand zu meiden. [6, 7] Um die korrekte Berechnung der zu erwartenden Belohnung sicherzustellen, muss die Umgebung die Markoweigenschaft erfüllen. Die Markoweigenschaft ist erfüllt, wenn die Wahrscheinlichkeit, in einen Folgezustand $s_{t+1}$ zu gelangen, nur von dem Zustand $s$ und der Aktion $a$ abhängt. [8, S. 274]

Auf Basis des Reinforcement Learning, wie von Sutton und Barto beschrieben, werden seitdem verschiedene Algorithmen entwickelt, die nach dem Prinzip des Reinforcement Learning arbeiten und versuchen, das Lernen möglichst effizient zu gestalten. Darunter fallen unter anderem der von Watkins und Dayan vorgestellte Q-Learning-Algorithmus oder der RBQL-Algorithmus [4].

### 2.2 Q-Learning

Das Q-Learning ist ein Algorithmus, der zum Reinforcement Learning zählt. Dabei wird die Aktion, welche ein Agent ausführt, auf Basis einer Bewertungsfunktion $Q^*(s,a)$ bestimmt. Diese Funktion soll in jedem Zustand die Aktion auswählen, die am wahrscheinlichsten zu einer Belohnung führt. [9] Dabei ist $Q^*$ die Summe der zukünftigen Belohnungen. Die zukünftigen Belohnungen werden über einen Discount-Faktor $\gamma$, dessen Wert zwischen 0 und 1 liegt, nach der folgenden Funktion (2.1) gewichtet. [8, 9]
