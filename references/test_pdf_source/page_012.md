$$\text{Ableitung der linearen Funktion:} \quad \frac{dF}{d\varphi} = 1 \tag{2.11}$$

$$\text{Ableitung der Leaky ReLU-Funktion:} \quad \frac{dF}{d\varphi} = \begin{cases} \alpha & \text{falls } \varphi < 0 \\ 1 & \text{falls } \varphi > 0 \end{cases} \tag{2.12}$$

Damit kann man nun anhand der entsprechenden Lernregel die Gewichtsänderung berechnen. Dies wird so lange gemacht, bis das neuronale Netz ein zufriedenstellendes Ergebnis liefert. [8, 12]
