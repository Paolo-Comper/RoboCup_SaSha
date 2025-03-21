import cv2
import numpy as np
from picamera2 import Picamera2
from Motori import *

def img_capture():
    img = picam2.capture_array()
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

def rileva_cerchi(img, WIDTH, HEIGHT):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
        param1=80, param2=50, minRadius=20, maxRadius=80
    )
    x, y = 0, 0
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            if 20 < i[2] < 80:
                cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
                cv2.putText(img, f"X: {i[0]} Y: {i[1]}", (i[0] - 30, i[1] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                x = ((i[0] / WIDTH) * 200) - 100
                y = ((i[1] / HEIGHT) * 200) - 100
    return x, y, img

def rileva_argento(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # soglie per vedere dove minchia sta l'argento! (modificare)
    lower_silver = np.array([50, 50, 150])
    upper_silver = np.array([200, 40, 255])
    silver_mask = cv2.inRange(hsv, lower_silver, upper_silver)
    contours, _ = cv2.findContours(silver_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    silver_x, silver_y = None, None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:
            x, y, w, h = cv2.boundingRect(contour)
            if area > max_area:
                max_area = area
                silver_x = x + w // 2
                silver_y = y + h // 2
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(img, "Argento", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    return silver_x, silver_y, img

HEIGHT, WIDTH, CHANNELS = 480, 640, 3
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (WIDTH, HEIGHT)})
picam2.configure(config)
picam2.start()

while True:
    img = img_capture()
    x_cerchio, y_cerchio, img = rileva_cerchi(img, WIDTH, HEIGHT)
    x_argento, y_argento, img = rileva_argento(img)
    if (y_cerchio > 70):
        while(True):
            ControlloMotori(x_cerchio, 0)
    if x_cerchio is not None and y_cerchio is not None:
        ControlloMotori(x_cerchio, 40)
    elif x_argento is not None and y_argento is not None:
        ControlloMotori(x_argento, 35)
    else:
        ControlloMotori(0, 30)
    cv2.imshow("immagine", img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
