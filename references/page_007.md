# Kapitel 1

## Einleitung

### 1.1 Motivation und Hintergrund

Neuronale Netze gewinnen in der heutigen Zeit immer mehr an Relevanz. Es gibt vielfältige Einsatzmöglichkeiten. Sie werden zum Beispiel in der Bilderkennung, bei Sprachmodellen oder bei der Schrifterkennung eingesetzt. [1] [2]

Die Idee, neuronale Netze zum Erlernen von Anwendungsaufgaben zu benutzen, entstammt aus der Biologie. In unserem Gehirn gibt es etwa 100 Milliarden Neuronen. Ein Neuron ist mit 1000 bis 10 000 anderen Neuronen über Axone verbunden. Über diese Verbindungen werden Signale in Form von elektrischen Impulsen gesendet, wodurch Informationen weitergeleitet werden und das menschliche Gehirn in der Lage ist zu lernen. [3]

Diese Funktion unseres Gehirns versucht man künstlich nachzubauen. Neben dem Aufbau des künstlichen Netzes ist dabei das Training ein wichtiger Aspekt. Komplexe Anwendungsfälle benötigen oft ein langes und aufwendiges Trainieren des neuronalen Netzes. Diesen Trainingsaufwand zu optimieren, ohne Genauigkeit zu verlieren, ist eine wichtige Aufgabe, um neuronale Netze effizienter zu erstellen und Anwendungsbereiche zu erweitern. Diese Arbeit beschäftigt sich mit dem Training von neuronalen Netzen mittels RBQL in deterministischen Umgebungen. RBQL ist dabei ein optimierter Q-Learning Algorithmus, welcher im Vergleich zum klassischen Q-Learning weniger Episoden benötigt um eine Problemstellung zu erlernen. [4] Dies ist besonders interessant, da sich viele Bereiche unseres Lebens deterministisch annähern lassen.

Vor allem Large Language Models (LLMs), wie GPT, benötigen ein aufwendiges Training des neuronalen Netzes. Das hat zur Folge, dass mehr elektrische Energie benötigt wird um die Computer zu betreiben, auf denen das neuronale Netz trainiert wird. Um die Kosten und die Belastung für die Umwelt zu reduzieren, sollten die LLMs möglichst effizient trainiert werden. [5]

Obwohl Sprachmodelle in der Regel nicht deterministisch sind, können sie dennoch deterministische Ausgaben erzeugen, sofern die Temperatur gleich null gesetzt wird. Dadurch
