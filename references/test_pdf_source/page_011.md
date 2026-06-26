Neben der Sigmoidfunktion (2.4) [8] werden häufig auch die ReLU-Funktion (2.5) [8, 10] oder eine lineare Transferfunktion (2.6) [8] eingesetzt, da diese durch ihre einfache Abbildung und Ableitung effizient sind. Neben den hier aufgeführten Transferfunktionen gibt es noch viele weitere, mit denen die Ausgabe eines künstlichen Neurons beschrieben werden kann. Die Leaky ReLU-Funktion (2.7) bietet gegenüber ReLU den Vorteil, dass absterbende Neuronen verhindert werden. [11]

$$\text{Sigmoidfunktion:} \quad o_j = F(\varphi_j) = \frac{1}{1 + e^{-x}} \tag{2.4}$$

$$\text{ReLU-Funktion:} \quad o_j = F(\varphi_j) = \begin{cases} 0 & \text{if } \varphi \leq 0 \\ \varphi & \text{if } \varphi > 0 \end{cases} \tag{2.5}$$

$$\text{lineare Funktion:} \quad o_j = F(\varphi_j) = \varphi \tag{2.6}$$

$$\text{Leaky ReLU-Funktion:} \quad o_j = F(\varphi_j) = \begin{cases} \alpha \varphi_j & \text{if } \varphi_j \leq 0 \\ \varphi_j & \text{if } \varphi_j > 0 \end{cases} \tag{2.7}$$

Zum Trainieren eines neuronalen Netzes wird häufig Backpropagation verwendet. Bei dieser Lernmethode wird das neuronale Netz zunächst normal vorwärts aktiviert. Über die Ausgabe und die erwartete Ausgabe wird ein Fehler berechnet. Ziel ist es diesen Fehler zu minimieren. Dieser Fehler wird daraufhin rückwärts durch das neuronale Netz geleitet und die Gewichte entsprechend angepasst.

Häufig wird der quadratische Fehler nach Gleichung 2.8 berechnet. Um die Gewichtsänderung zu berechnen, benötigt man noch die Ableitung der genutzten Transferfunktion. Die Ableitungen der oben vorgestellten Transferfunktionen sind in (2.9) bis (2.12) zu sehen. [8, 12]

$$\text{Fehlerberechnung:} \quad E_k = \frac{1}{2}(o_k - t_k)^2 \tag{2.8}$$

$$\text{Ableitung der Sigmoidfunktion:} \quad \frac{dF}{d\varphi} = \sigma(\varphi) \cdot (1 - \sigma(\varphi)), \quad \sigma(\varphi) = \frac{1}{1 + e^{-\varphi}} \tag{2.9}$$

$$\text{Ableitung der ReLU-Funktion:} \quad \frac{dF}{d\varphi} = \begin{cases} 0 & \text{falls } \varphi < 0 \\ 1 & \text{falls } \varphi > 0 \end{cases} \tag{2.10}$$
