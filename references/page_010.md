$$Q^*_t(s, a) = \sum_{i=0}^{\infty} \gamma^i \cdot r_{t+i} \tag{2.1}$$

Über die optimale Belohnungsfunktion $Q^*(s,a)$ lässt sich dann für jeden Zustand die Aktion auswählen, bei der die höchste Belohnung erwartet wird.

Die Bewertungsfunktion $Q$ wird in der Regel mit zufälligen Werten oder mit null initialisiert. Um die Q-Funktion für die entsprechende Umgebung zu approximieren, muss der Agent zu allen Zuständen die jeweiligen Aktionen ausprobieren. Das Ausprobieren neuer Aktionen nennt man Exploration. Es gibt verschiedene Ansätze, um zu entscheiden, ob ein Agent eine Exploration durchführen soll oder die Aktion mit der höchsten Wahrscheinlichkeit wählen soll. Ein häufig verwendeter Ansatz ist die Aktionsauswahl mit „Epsilon-Greedy". Dabei wird mit einer Wahrscheinlichkeit $\varepsilon$ eine zufällige Aktion ausgewählt. Nach jeder Aktion wird der Q-Wert der Bewertungsfunktion für den Zustand $s_t$ und die Aktion $a_t$ angepasst. Dabei wird der entsprechende Q-Wert, nach der in Gleichung (2.2) dargestellten Vorgehensweise, angepasst. [8, 9]

$$Q_t \leftarrow Q_t + \alpha \left( r_t + \gamma \cdot \max_{a_{t+1}}(Q_{t+1}) - Q_t \right) \tag{2.2}$$

### 2.3 Neuronale Netze

Neuronale Netzwerke im Bereich des maschinellen Lernen basieren auf biologischen Neuronen, wie sie auch in unserem Körper vorkommen. Neuronen sind über Synapsen miteinander verbunden. Erreichen die Eingangsimpulse eines Neurons einen Schwellwert, wird das Neuron aktiviert. Diese Verhaltensweise wird durch ein künstliches Neuron simuliert. Die Aktivität eines Neurons wird durch die Summe der gewichteten Eingänge beschrieben. Die Summe der gewichteten Eingänge wird durch Gleichung (2.3) beschrieben. [8]

$$\varphi_j = \sum_i o_i w_{ji} \tag{2.3}$$

Über die Transferfunktion wird die Ausgabe eines künstlichen Neurons beschrieben. Es gibt verschiedene Transferfunktionen, die in neuronalen Netzwerken eingesetzt werden. Neben der Sigmoidfunktion (2.4) [8] werden häufig auch die ReLU-Funktion (2.5) [8, 10] oder eine lineare Transferfunktion (2.6) [8] eingesetzt, da diese durch ihre einfache Abbildung und Ableitung effizient sind. Neben den hier aufgeführten Transferfunktionen gibt es noch viele weitere, mit denen die Ausgabe eines künstlichen Neurons beschrieben werden kann. Die Leaky ReLU-Funktion (2.7) bietet gegenüber ReLU den Vorteil, dass absterbende Neuronen verhindert werden. [11]

$$\text{Sigmoidfunktion:} \quad o_j = F(\varphi_j) = \frac{1}{1 + e^{-x}} \tag{2.4}$$

$$\text{ReLU-Funktion:} \quad o_j = F(\varphi_j) = \begin{cases} 0 & \text{if } \varphi \leq 0 \\ \varphi & \text{if } \varphi > 0 \end{cases} \tag{2.5}$$

$$\text{lineare Funktion:} \quad o_j = F(\varphi_j) = \varphi \tag{2.6}$$

$$\text{Leaky ReLU-Funktion:} \quad o_j = F(\varphi_j) = \begin{cases} \alpha \varphi_j & \text{if } \varphi_j \leq 0 \\ \varphi_j & \text{if } \varphi_j > 0 \end{cases} \tag{2.7}$$

Zum Trainieren eines neuronalen Netzes wird häufig Backpropagation verwendet. Bei dieser Lernmethode wird das neuronale Netz zunächst normal vorwärts aktiviert. Über die Ausgabe und die erwartete Ausgabe wird ein Fehler berechnet. Ziel ist es diesen Fehler zu minimieren. Dieser Fehler wird daraufhin rückwärts durch das neuronale Netz geleitet und die Gewichte entsprechend angepasst.

Häufig wird der quadratische Fehler nach Gleichung 2.8 berechnet. Um die Gewichtsänderung zu berechnen, benötigt man noch die Ableitung der genutzten Transferfunktion. Die Ableitungen der oben vorgestellten Transferfunktionen sind in (2.9) bis (2.12) zu sehen. [8, 12]

$$\text{Fehlerberechnung:} \quad E_k = \frac{1}{2}(o_k - t_k)^2 \tag{2.8}$$

$$\text{Ableitung der Sigmoidfunktion:} \quad \frac{dF}{d\varphi} = \sigma(\varphi) \cdot (1 - \sigma(\varphi)), \quad \sigma(\varphi) = \frac{1}{1 + e^{-\varphi}} \tag{2.9}$$

$$\text{Ableitung der ReLU-Funktion:} \quad \frac{dF}{d\varphi} = \begin{cases} 0 & \text{falls } \varphi < 0 \\ 1 & \text{falls } \varphi > 0 \end{cases} \tag{2.10}$$

$$\text{Ableitung der linearen Funktion:} \quad \frac{dF}{d\varphi} = 1 \tag{2.11}$$

$$\text{Ableitung der Leaky ReLU-Funktion:} \quad \frac{dF}{d\varphi} = \begin{cases} \alpha & \text{falls } \varphi < 0 \\ 1 & \text{falls } \varphi > 0 \end{cases} \tag{2.12}$$

Damit kann man nun anhand der entsprechenden Lernregel die Gewichtsänderung berechnen. Dies wird so lange gemacht, bis das neuronale Netz ein zufriedenstellendes Ergebnis liefert. [8, 12]
