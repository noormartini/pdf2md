schwindigkeit eins das Ergebnis eins. Diese angepasste Geschwindigkeit wird in „vx_idx“
und „vy_idx“ gespeichert. Anschließend wird die Berechnung des Zustandes wie bisher
auch fortgeführt.
1 def getState(x_ball, y_ball, vx_ball, vy_ball, x_racket):
2
vx_idx = {-2: 0, -1: 1, 1: 2, 2: 3}[vx_ball]
3
vy_idx = {-2: 0, -1: 1, 1: 2, 2: 3}[vy_ball]
4
return (((x_ball * 13 + y_ball) * 2 + vx_idx) * 2 + vy_idx ) * 12 +
x_racket
Quellcode 5.10: Für nicht deterministische Umgebung angepasste getState Funktion
5.7 Integration des neuronalen Netzwerks
Zur Umsetzung des neuronalen Netzes wird eine Klasse angelegt, mit der ein einfaches
neuronales Netz mit Eingabeschicht, versteckter Schicht und Ausgabeschicht erzeugt wer-
den kann. Quellcode 5.11 zeigt den Konstruktor zur Erstellung des neuronalen Netzes.
Die benötigten Eingabeparameter sind dabei die Größe der Eingabeschicht, die Größe der
versteckten Sicht und die Größe der Ausgabeschicht. Die Gewichte und Biases werden
zufällig zwischen -1 und 1 initialisiert.
1
def __init__(self, input_size, hidden_size, output_size):
2
# Initialisierung der Gewichte und Biases
3
self.W1 = np.random.uniform(-1, 1, (hidden_size, input_size))
4
self.b1 = np.random.uniform(-1, 1, (hidden_size,))
5
self.W2 = np.random.uniform(-1, 1, (output_size, hidden_size))
6
self.b2 = np.random.uniform(-1, 1, (output_size,))
Quellcode 5.11: Konstruktor zur Erzeugung des neuronalen Netzes
In einem ersten Ansatz wird die ReLU-Funktion als Aktivierungsfunktion eingesetzt. Die-
se ist mit ihrer Ableitung in Quellcode 5.12 dargestellt.
1 def relu(x):
2
return np.where(x>=0,x,0)
3
4 def relu_derivative(x):
5
return np.where(x>=0,1,0)
Quellcode 5.12: Aktivierungsfunktion und Ableitung der Aktivierungsfunktion
Die ReLU-Funktion ist weit verbreitet und aufgrund ihrer Einfachheit effizient implemen-
tierbar. Allerdings zeigt sich, dass das neuronale Netz mit dieser Aktivierungsfunktion
nicht lernt. Erste Vermutungen deuten auf ein Problem mit absterbenden Neuronen hin.
Die Wahl geeigneter Aktivierungsfunktionen ist entscheidend für den Lernerfolg neu-
ronaler Netze. ReLU ist aufgrund ihrer Einfachheit und Effizienz weit verbreitet, bringt
22