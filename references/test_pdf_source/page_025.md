**Abbildung 5.1**: Beispielhafter Zustandsbaum des RBQL-Algorithmus. Jeder Knoten stellt einen möglichen Zustand des Agenten dar, Kanten zeigen die möglichen Aktionen und die daraus resultierenden Zustände. Die rote Farbmarkierung kennzeichnet in einer Episode neu erkundete Bereiche des Baums.

in einer vorherigen Episode schon einmal besucht wurde und schon bewertet ist. Abbildung 5.1 zeigt beispielhaft, über welche Zustände in einen Endzustand st gelangt werden kann. Dabei stellt der rechte rote Teil des Baumes einen neuen Weg dar, um in den Endzustand st zu gelangen.

Eine Möglichkeit zur Reduzierung des Lernaufwandes besteht darin, nur noch die neuen Zustände zu bewerten. Im Beispiel von Abbildung 5.1 müsste dadurch nur der rote Teil des Baumes bewertet werden.

Dazu wird von s5 ausgehend alle vorherigen Zustände bewertet.

Um nur die bisher nicht bewerteten Zustände bei der Bewertung zu betrachten, müssen im Quellcode einige Anpassungen vorgenommen werden. Quellcode 5.8 zeigt diese Anpassungen.

Der Warteschlange „queue" wird nun nicht mehr standardmäßig der Endzustand als Ausgangspunkt angefügt. Stattdessen wird eine Unterscheidung gemacht, welcher Zustand der Warteschlange angefügt wird. Wenn die Anzahl aller bisher ausgeführten Schritte mit der
