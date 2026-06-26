jedoch das Risiko sogenannter „Dead Neurons" mit sich, insbesondere bei tieferen Netzen. He u. a. [17] zeigten, dass durch eine angepasste Initialisierung und die Verwendung von Varianten wie Parametric ReLU (PReLU) signifikante Verbesserungen bei der Konvergenz erzielt werden können, vor allem bei tiefen Architekturen. Auch in dieser Arbeit zeigte sich, dass klassische ReLU-Funktionen zu instabilen Lernergebnissen führten, während Leaky ReLU diese Problematik abmildern konnte. In Unterabschnitt 6.5.1 wird das Problem der absterbenden Neuronen weiter untersucht. Als weitere Aktivierungsfunktion wird die Leaky ReLU-Funktion getestet. Diese ist in Quellcode 5.13 mit Ihrer Ableitung dargestellt. Im Gegensatz zur klassischen ReLu-Funktion gibt die Leaky-ReLu-Funktion selbst auch bei negativen Werten einen Wert zurück. Dadurch besteht nicht die Gefahr, dass Neuronen bei häufigen negativen Werten absterben. [11]

Quellcode 5.13 wird mittels der Bibliothek Numpy direkt auf eine ganze Schicht des Netzes angewandt.

```python
def leaky_relu(x):
    return np.where(x >= 0, x, a * x)

def leaky_relu_derivative(x):
    return np.where(x >= 0, 1, a)
```

**Quellcode 5.13**: Aktivierungsfunktion und Ableitung der Aktivierungsfunktion

In Quellcode 5.14 ist die Methode „foreward" zu sehen, welche für die Aktivierung des neuronalen Netzes genutzt wird. Die Variable „x" steht für die Eingabevektoren. „z1" ist dabei die Summe der gewichteten Eingänge des neuronalen Netzes. Diese werden benutzt, um die Ausgabe der versteckten Schicht zu berechnen. Die Ausgabe der versteckten Schicht wird in „a1" gespeichert.

Mit der Ausgabe der versteckten Schicht wird die gewichtete Eingabe der Ausgabeschicht berechnet. Diese wird in „z2" gespeichert. Abschließend wird aus „z2" mittels der Funktion leaky_relu() nochmal die Ausgabe der letzten Schicht berechnet. Diese wird als „a2" zurückgegeben.

```python
def forward(self, x):
    self.input = np.array(x)
    self.z1 = np.dot(self.W1, self.input) + self.b1
    self.a1 = leaky_relu(self.z1)

    self.z2 = np.dot(self.W2, self.a1) + self.b2
    self.a2 = leaky_relu(self.z2)
    return self.a2
```

**Quellcode 5.14**: Methode foreward zur Aktivierung des neuronalen Netzes
