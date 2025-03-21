import cv2
import numpy as np
from Motori import *

HEIGHT, WIDTH, CHANNELS = 480, 640, 3

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Converti in scala di grigi
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Sfocatura per ridurre il rumore
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

    # Migliora il contrasto con una soglia adattiva
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Rilevamento cerchi con HoughCircles
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
        param1=80, param2=50, minRadius=20, maxRadius=80
    )

    x = 0
    y = 0
    if circles is not None:
        circles = np.uint16(np.around(circles))  # Arrotonda i valori
        for i in circles[0, :]:
            if 20 < i[2] < 80:  # Filtra per raggio (evita falsi positivi troppo piccoli o grandi)
                cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)  # Disegna il cerchio
                cv2.putText(frame, f"X: {i[0]} Y: {i[1]}", (i[0] - 30, i[1] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                x = ((i[0] / WIDTH) * 200) - 100
                y = ((i[1] / HEIGHT) * 200) - 100
    
    ControlloMotori(x, 50)
    # Se siamo vicini col sensore di distanza, ferma il robottino e fai la manovra per l'aggancio palline!

    cv2.imshow("Ball Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
