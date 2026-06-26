# Kapitel 3

## Verwandte Arbeiten

### 3.1 Markow Entscheidungsprozess

Die heutigen Ansätze des verstärkenden Lernens bauen auf dem Markow Entscheidungsprozess auf. Eine erste Beschreibung findet sich bereits 1957 bei BELLMAN in „A Markovian Decision Process". BELLMAN untersuchte ein Entscheidungsproblem, bei dem eine Folge von Entscheidungen in einem stochastischen Umfeld getroffen werden muss, wobei der zukünftige Zustand des Systems nur vom aktuellen Zustand und der gewählten Aktion abhängt. Dieses Prinzip der Markov-Eigenschaft bildet die Grundlage für seine Analyse. Er formuliert eine nichtlineare Rekursionsgleichung, mit der der optimale Erwartungswert einer Entscheidungsstrategie beschrieben werden kann. Anhand eines konkreten Anwendungsbeispiels, dem sogenannten Maschinenersatzproblem, zeigt Bellman, dass unter bestimmten Bedingungen das asymptotische Verhalten dieser Rekursionsgleichung durch lineares Wachstum gekennzeichnet ist und dass sich die zugehörige Wachstumsrate als Lösung eines weiteren Optimierungsproblems bestimmen lässt. Obwohl die heute gebräuchliche Formulierung des Markow-Entscheidungsprozesses mit expliziten Zustands- und Aktionsmengen erst später entwickelt wurde, legt Bellmans Arbeit den Grundstein für zahlreiche Folgearbeiten und stellt eine der theoretischen Grundlagen des verstärkenden Lernens dar. [13]

### 3.2 Experience Replay

Bereits 1992 führte Lin in „Self-improving reactive agents based on reinforcement learning, planning and teaching" [14] das Konzept des Experience Replay ein, um die Effizienz von verstärkendem Lernen zu verbessern. Ausgangspunkt seiner Arbeit ist die Beobachtung, dass Verfahren wie Q-Learning [9] und Adaptive Heuristic Critic (AHC) Learning zwar gut theoretisch fundiert, in der Praxis jedoch häufig sehr langsam konvergieren und daher für komplexe, dynamische Umgebungen schwer anwendbar sind. Lin verfolgte daher zwei Hauptziele: erstens die Untersuchung von Reinforcement Learning in einer deutlich
