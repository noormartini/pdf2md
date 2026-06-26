# Kapitel 4

## Problemstellung und Lösungsansatz

### 4.1 Lernproblem im Kontext eines Ping-Pong-Spiels

In dieser Arbeit wird ein Ping-Pong Spiel verwendet, bei dem der Agent den Ball mit einem Schläger so lange wie möglich in der Luft halten muss. Als Vorlage für das Spiel wird der Python Code aus Maschinelles Lernen für Dummies®: Maschinelles Lernen richtig verstehen : GPT-Sprachmodell, Deep Learning, neuronales Q-Learning - alles selbst programmieren : viele Code-Beispiele zu allen behandelten Themen, S. 283–285 [8, S. 283–285] verwendet und angepasst. Dabei hat der Agent in jedem der Zustände zwei mögliche Aktionen, die er ausführen kann. Entweder er bewegt den Schläger einen Schritt nach links oder einen Schritt nach rechts. Der Zustand, in dem sich der Agent befindet, wird dabei anhand von fünf Parametern definiert: den X- und Y-Positionen des Balls, seinen Geschwindigkeiten entlang der X- und Y-Achse sowie der X-Position des Schlägers. Der Ball prallt auf dem Schläger, den seitlichen und der oberen Wand ab. Wenn der Ball aus dem Spielfeld nach unten herausfällt, beginnt das Spiel von vorne. Dabei wird es aufwendiger für einen Q-Learning Agenten, das Spiel zu lernen, je größer das Spielfeld wird. Dies hängt damit zusammen, dass je größer das Spielfeld wird, der Zustandsraum auch immer größer wird. Damit der klassische Q-Learning Agent das Spiel optimal erlernt, muss er in jeden Zustand einmal gelangen, um den entsprechenden Q-Wert für diesen Zustand und eine bestimmte Aktion erlernt wird.

### 4.2 Architektur des neuronalen Netzwerks

Getestet wird das Trainieren eines einfachen neuronalen Netzes. Dazu wird ein neuronales Netz mit einer Eingabeschicht, einer versteckten Schicht und einer Ausgabeschicht verwendet. Dabei hat die Eingabeschicht eine Größe von 5 Neuronen und die Ausgabeschicht eine Größe von 2 Neuronen. Die Ausgabe des neuronalen Netzes soll dabei mit der Ausgabe der Q-Funktion übereinstimmen. Ein Ausgabeneuron steht dabei für eine Bewegung nach rechts und das andere für eine Bewegung nach links. Je nachdem, welches Neuron die größere Ausgabe liefert, wird die entsprechende Aktion ausgeführt. Ziel soll
