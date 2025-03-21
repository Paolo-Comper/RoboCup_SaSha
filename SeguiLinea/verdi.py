import math
import cv2
import numpy as np

# Constant greenDetect 
GREENUP = (90, 255, 255)
GREENDOWN = (30, 100, 40)
ALTEZZAIMG = 200
X1 = 0
X2 = 1
contorno = None
sto_girando = False

# Var greenDetect
KY = 5
KX = 50
nVerdi = None

def greenDetect(img):
    global nVerdi, contorno

    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Converte in HSV
    maskGreen = cv2.inRange(imgHSV, GREENDOWN, GREENUP)  # Crea una maschera con i Verdi
    
    contorno, _ = cv2.findContours(maskGreen, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Rimuovi i contorni con area inferiore a 400
    contorno = [c for c in contorno if cv2.contourArea(c) >= 400]

    # Ordina i contorni in base alla loro posizione (dal basso verso l'alto)
    contorno = sorted(contorno, key=lambda c: cv2.boundingRect(c)[1], reverse=True)

    nVerdi = False  # Inizializza nVerdi a False

    if not contorno:
        nVerdi = 0
        return nVerdi

    M = cv2.moments(contorno[0])
    if M['m00'] == 0:
        nVerdi = 0
        return nVerdi

    #// cxp = int(M['m10'] / M['m00'])
    cyp = int(M['m01'] / M['m00'])

    contorno = [c for c in contorno if cv2.moments(c)['m00'] != 0 and abs(cyp - int(cv2.moments(c)['m01'] / cv2.moments(c)['m00'])) <= 80]

    return (len(contorno))

def greenFollowing(punto, p_angolo):
    global nVerdi, contorno, sto_girando

    match nVerdi:
        case 1:
            M = cv2.moments(contorno[0])
            if M['m00'] == 0: #* DEBUG
                return p_angolo
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            if sto_girando is False:
                if cy > punto.getY():
                    if cx > punto.getX():
                        cx = cx - KX
                    else:
                        cx = cx + KX
                    cy = cy - KY
                    
                    cx = cx - punto.getX()
                    cy = cy - punto.getY()

                    angolo_rad = -math.atan2(cx, cy)
                    sto_girando = True
                    #//angolo_deg = math.degrees(angolo_rad)
                    return angolo_rad
                    
                else:
                    return p_angolo
                
            else:
                if cx > punto.getX():
                    cx = cx - KX
                else:
                    cx = cx + KX
                    
                cx = cx - punto.getX()
                cy = cy - punto.getY()

                angolo_rad = -math.atan2(cx, cy)
                #//angolo_deg = math.degrees(angolo_rad)
                return angolo_rad
            
        case 2:
            return None
        
        case _:
            sto_girando = False
            return p_angolo