schwindigkeit eins das Ergebnis eins. Diese angepasste Geschwindigkeit wird in „vx_idx" und „vy_idx" gespeichert. Anschließend wird die Berechnung des Zustandes wie bisher auch fortgeführt.

```python
def getState(x_ball, y_ball, vx_ball, vy_ball, x_racket):
    vx_idx = {-2: 0, -1: 1, 1: 2, 2: 3}[vx_ball]
    vy_idx = {-2: 0, -1: 1, 1: 2, 2: 3}[vy_ball]
    return (((x_ball * 13 + y_ball) * 2 + vx_idx) * 2 + vy_idx ) * 12 + x_racket
```

**Quellcode 5.10**: Für nicht deterministische Umgebung angepasste getState Funktion

## 5.7 Integration des neuronalen Netzwerks

Zur Umsetzung des neuronalen Netzes wird eine Klasse angelegt, mit der ein einfaches neuronales Netz mit Eingabeschicht, versteckter Schicht und Ausgabeschicht erzeugt werden kann. Quellcode 5.11 zeigt den Konstruktor zur Erstellung des neuronalen Netzes. Die benötigten Eingabeparameter sind dabei die Größe der Eingabeschicht, die Größe der versteckten Sicht und die Größe der Ausgabeschicht. Die Gewichte und Biases werden zufällig zwischen -1 und 1 initialisiert.

```python
def __init__(self, input_size, hidden_size, output_size):
    # Initialisierung der Gewichte und Biases
    self.W1 = np.random.uniform(-1, 1, (hidden_size, input_size))
    self.b1 = np.random.uniform(-1, 1, (hidden_size,))
    self.W2 = np.random.uniform(-1, 1, (output_size, hidden_size))
    self.b2 = np.random.uniform(-1, 1, (output_size,))
```

**Quellcode 5.11**: Konstruktor zur Erzeugung des neuronalen Netzes

In einem ersten Ansatz wird die ReLU-Funktion als Aktivierungsfunktion eingesetzt. Diese ist mit ihrer Ableitung in Quellcode 5.12 dargestellt.

```python
def relu(x):
    return np.where(x>=0, x, 0)

def relu_derivative(x):
    return np.where(x>=0, 1, 0)
```

**Quellcode 5.12**: Aktivierungsfunktion und Ableitung der Aktivierungsfunktion

Die ReLU-Funktion ist weit verbreitet und aufgrund ihrer Einfachheit effizient implementierbar. Allerdings zeigt sich, dass das neuronale Netz mit dieser Aktivierungsfunktion nicht lernt. Erste Vermutungen deuten auf ein Problem mit absterbenden Neuronen hin. Die Wahl geeigneter Aktivierungsfunktionen ist entscheidend für den Lernerfolg neuronaler Netze. ReLU ist aufgrund ihrer Einfachheit und Effizienz weit verbreitet, bringt
