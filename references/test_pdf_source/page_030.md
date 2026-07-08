Quellcode 5.15 zeigt die Methode zum Trainieren des neuronalen Netzes. In diesem Netz wird Backpropagation verwendet, um das Netz zu trainieren. Die Funktion benötigt als Eingabeparameter die Eingabewerte „x" des neuronalen Netzes, die gewünschte Ausgabe „target" und eine Lernrate „learning_rate", welche standardmäßig auf 0,01 gesetzt ist. Zunächst wird das Netz vorwärts aktiviert, indem die Funktion foreward() aufgerufen wird. Das Ergebnis der Vorwärtsaktivierung wird in „output" gespeichert. Anschließend wird der Fehler berechnet. Dazu wird von der tatsächlichen Ausgabe des neuronalen Netzes die erwartete Ausgabe abgezogen. Falls beide Werte übereinstimmen, ist der Fehler gleich null. Nun wird der Fehler zurück durch das neuronale Netz propagiert und der Fehler für jede Schicht berechnet. Abschließend wird für jede Schicht das Gewicht im Gradientenabstieg angepasst.

```python
def train(self, x, target, learning_rate=0.01):
    output = self.forward(x)
    error = output - target

    # Backpropagation
    delta2 = error * leaky_relu_derivative(self.z2)
    delta1 = np.dot(self.W2.T, delta2) * leaky_relu_derivative(self.z1)

    # Update output layer weights
    self.W2 -= learning_rate * np.outer(delta2, self.a1)
    self.b2 -= learning_rate * delta2

    # Update hidden layer weights
    self.W1 -= learning_rate * np.outer(delta1, self.input)
    self.b1 -= learning_rate * delta1
```

**Quellcode 5.15**: Methode train zum Trainieren des neuronalen Netzes

Diese Klasse dient als Grundlage, ein einfaches neuronales Netz aufzubauen. Über den Konstruktor der Klasse kann die Größe der drei Schichten variabel eingestellt werden. Im Falle des Trainings mittels RBQL wird ein neuronales Netz mit einer Eingabeschicht von 5 Neuronen, einer versteckten Schicht von 128 Neuronen und einer Ausgabeschicht mit 2 Neuronen erstellt. Quellcode 5.16 zeigt, wie eine Instanz der Klasse und somit das neuronale Netz erstellt wird.

```python
neural = NeuralNet.NeuralNet(5, 128, 2)
```

**Quellcode 5.16**: Erstellung einer Instanz der Klasse NeuralNet

Um das neuronale Netz mittels RBQL trainieren zu können, muss gleichzeitig auch die Q-Funktion des RBQL optimiert werden. Die Aktionsauswahl erfolgt durch das neuronale Netz, mit einer Wahrscheinlichkeit Epsilon wird jedoch eine zufällige Aktion ausgewählt. Epsilon wird mit jeder Episode um einen festen Betrag reduziert. Dadurch wird zu Beginn
