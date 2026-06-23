Neben der Sigmoidfunktion (2.4) [8] werden häufig auch die ReLU-Funktion (2.5)[8, 10]
oder eine lineare Transferfunktion (2.6)[8] eingesetzt, da diese durch ihre einfache Abbil-
dung und Ableitung effizient sind. Neben den hier aufgeführten Transferfunktionen gibt es
noch viele weitere, mit denen die Ausgabe eines künstlichen Neurons beschrieben werden
kann. Die Leaky ReLU-Funktion (2.7) bietet gegenüber ReLU den Vorteil, dass abster-
bende Neuronen verhindert werden. [11]
Sigmoidfunktion: oj = F(φj) =
1
1 + e−x
(2.4)
ReLU-Funktion: oj = F(φj) =



0
if φ ≤0
φ
if φ > 0
(2.5)
lineare Funktion: oj = F(φj) = φ
(2.6)
Leaky ReLU-Funktion: oj = F(φj) =



αφj
if φj ≤0
φj
if φj > 0
(2.7)
Zum Trainieren eines neuronalen Netzes wird häufig Backpropagation verwendet. Bei die-
ser Lernmethode wird das neuronale Netz zunächst normal vorwärts aktiviert. Über die
Ausgabe und die erwartete Ausgabe wird ein Fehler berechnet. Ziel ist es diesen Fehler
zu minimieren. Dieser Fehler wird daraufhin rückwärts durch das neuronale Netz geleitet
und die Gewichte entsprechend angepasst.
Häufig wird der quadratische Fehler nach Gleichung 2.8 berechnet. Um die Gewichtsände-
rung zu berechnen, benötigt man noch die Ableitung der genutzten Transferfunktion. Die
Ableitungen der oben vorgestellten Transferfunktionen sind in (2.9) bis (2.12) zu sehen.
[8, 12]
Fehlerberechnung: Ek = 1
2(ok −tk)2
(2.8)
Ableitung der Sigmoidfunktion:
dF
dφ = σ(φ) · (1 −σ(φ)),
σ(φ) =
1
1 + e−φ
(2.9)
Ableitung der ReLU-Funktion:
dF
dφ =



0
falls φ < 0
1
falls φ > 0
(2.10)
5