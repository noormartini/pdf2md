es sein, zu zeigen, dass ein neuronales Netz mit RBQL trainiert werden kann. Außerdem soll verglichen werden, wie effektiv das mit RBQL trainierte Netz im Vergleich zu einem mit Experience Replay trainierten Netz abschneidet.

### 4.3 Trainieren des neuronalen Netzwerks mit RBQL

Das Training des neuronalen Netzes erfolgt mithilfe des RBQL-Algorithmus. Dabei übernimmt das neuronale Netz die Funktion der klassischen tabellarischen Q-Funktion. Es erhält die Zustandsinformationen als Eingabe und gibt für jede mögliche Aktion einen geschätzten Q-Wert zurück.

**Eingabe und Zielwerte** Die Eingabe des neuronalen Netzes besteht aus fünf normierten Werten:

- xBall: horizontale Position des Balls
- yBall: vertikale Position des Balls
- vx: horizontale Geschwindigkeit des Balls
- vy: vertikale Geschwindigkeit des Balls
- xSchläger: horizontale Position des Schlägers

Diese Werte werden jeweils auf den Bereich [0, 1] normiert, um zu große Gewichte zu verhindern. Die Ausgabe des neuronalen Netzes besteht aus zwei Werten, die den Q-Werten für die beiden möglichen Aktionen (Bewegung nach links oder rechts) entsprechen sollen.

**Trainingsablauf** Nach jeder abgeschlossenen Episode, also wenn der Ball den unteren Spielfeldrand berührt oder erfolgreich abgewehrt wird, wird der RBQL-Algorithmus verwendet, um die Q-Werte rückwirkend zu aktualisieren. Diese berechneten Q-Werte dienen anschließend als Zielwerte für das Training des neuronalen Netzes. Das Netz wird mithilfe des Backpropagation-Verfahrens trainiert. Ziel ist es, dass die Ausgabe des Netzes möglichst genau mit den vom RBQL-Algorithmus berechneten Q-Werten übereinstimmt.

**Aktionsauswahl während des Trainings** Um eine ausgewogene Exploration zu gewährleisten, kommt die Epsilon-Greedy-Strategie zum Einsatz. Dabei wird mit einer Wahrscheinlichkeit ε eine zufällige Aktion gewählt, ansonsten die Aktion mit dem höchsten
