import cv2
import numpy as np
from picamera2 import Picamera2
import Motori 
from SeguiLinea import *
from Object import Punto, PuntoReal
from Kernel import rounded_square_kernel
import time


# +----------------------------------------+
# | COSTANTI E PARAMETRI DI CONFIGURAZIONE |
# +----------------------------------------+

# Dimensioni immagine: (altezza, larghezza, canali)
HEIGHT, WIDTH, CHANNELS = 480, 640, 3
ALTEZZA_LINEA_INIZIALE = HEIGHT - 40

# Parametri per la selezione del semicerchio
RAGGIO = 80
SEMI_RANGE = 214
DIM_SEMICERCHIO = SEMI_RANGE * 2 + 1
N_CERCHI = 4
arrayp_angolo = np.zeros(N_CERCHI+1, dtype=np.float32)

# Parametri per il line following
VELOCITA = 35
KE = 3.0    # Contributo della distanza della linea
K1 = 2.5    # Influenza dell'angolo immediato (piu vicino al robot)
K2 = 1.0    # Influenza della prima predizione
K3 = 0.3    # Influenza della seconda predizione (minore, per anticipare meno)

# Variabili Main
controllo = None

# Debug
VISUALIZZA = True

# Avviare i motori
MOTORI = True

# Matrice per trasformazione omografica
MAT_OMO = np.array([
    0.0015952, -0.0000101, -0.5088364,
    0.0000158, -0.0018789,  0.8608532,
   -0.0000002,  0.0000089,  0.0033609 ])

# Kernel per dilatazione dell'immagine
KERNEL_DILATE = np.array(rounded_square_kernel(10, 2), np.uint8)

# Array globali per memorizzare i punti rilevati
punti = [Punto(0, 0) for _ in range(N_CERCHI + 1)]
punti[0].setY(ALTEZZA_LINEA_INIZIALE)
punti_real = [PuntoReal((0, 0)) for _ in range(N_CERCHI + 1)]

img = None

# +-------------------------------+
# | INIZIALIZZAZIONE DELLA CAMERA |
# +-------------------------------+

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (WIDTH, HEIGHT)})
picam2.configure(config)
picam2.start()

# +----------+
# | FUNZIONI |
# +----------+

def img_capture():
    # Cattura un'immagine e la converte nello spazio colore BGR
    img = picam2.capture_array()
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

def line_processing():
    # Elabora l'immagine per calcolare il percorso della linea
    global punti, img, arrayp_angolo
    p_angolo = 0  # Angolo iniziale

    # Conversione in scala di grigi e applicazione della dilatazione
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.dilate(img_gray, KERNEL_DILATE, iterations=1)

    rad_step = np.pi / (DIM_SEMICERCHIO - 1)
    
    # Ciclo per ciascun semicerchio
    for j in range(N_CERCHI):
        punto = punti[j]

        if j == 0:
            # Aggiorna il punto iniziale analizzando la riga orizzontale
            riga = img_gray[ALTEZZA_LINEA_INIZIALE, :]
            grad = np.gradient(riga)
            grad = np.where((-10 <= grad) & (grad <= 10), 0, grad)
            
            #Se la linea Ã¨ vuota
            if np.count_nonzero(grad):
                punto.setX((np.argmax(grad) + np.argmin(grad)) / 2)
            else:
                punto.setX(WIDTH / 2)

            
            if VISUALIZZA: #* DEBUG
                cv2.circle(img, (punto.getX(), punto.getY()), 5, (255, 0, 0), -1)

        
        semicerchio = np.zeros(DIM_SEMICERCHIO, dtype=np.uint16)
        
        # Calcola il raggio massimo consentito dai bordi dell'immagine
        max_radius = min(
            RAGGIO,
            abs(punto.getY()),
            (RAGGIO if j == 0 else abs(HEIGHT - 5 - punto.getY())),
            abs(punto.getX()),
            abs(WIDTH - 5 - punto.getX())
        )
        
        
        # Pre-computa gli angoli per il semicerchio corrente
        angles = p_angolo + rad_step * np.arange(DIM_SEMICERCHIO)
        p_y = np.round(punto.getY() - max_radius * np.sin(angles)).astype(int)
        p_x = np.round(punto.getX() + max_radius * np.cos(angles)).astype(int)

        semicerchio[:] = img_gray[p_y, p_x]

        
        if VISUALIZZA: #* DEBUG
            img[p_y, p_x] = [255, 0, 0]

        # Individua il punto significativo lungo il semicerchio tramite la derivata
        semicerchio_grad = np.gradient(semicerchio)

        # Elimina i valori non significativi fra -25 e 25
        semicerchio_grad = np.where((-10 <= semicerchio_grad) & (semicerchio_grad <= 10), 0, semicerchio_grad)

        # Va dritto se non trova nulla
        if np.count_nonzero(semicerchio_grad):
            indice = int(round((np.argmax(semicerchio_grad) + np.argmin(semicerchio_grad)) / 2))
            p_angolo += rad_step * indice
            arrayp_angolo[j] = p_angolo
        else:
            p_angolo = arrayp_angolo[j]
        
        
        punti[j+1] = Punto(punto.getX() + max_radius * np.cos(p_angolo),
                           punto.getY() - max_radius * np.sin(p_angolo))
        
        if VISUALIZZA: #* DEBUG
            cv2.circle(img, (int(punto.getX() + max_radius * np.cos(p_angolo)), int(punto.getY() - max_radius * np.sin(p_angolo))), 5, (255, 0, 0), -1)
            cv2.circle(img, (punto.getX(), punto.getY()), max_radius, (0, 0, 255), 1)

        p_angolo -= np.pi / 2
    
    if VISUALIZZA: #* DEBUG
        cv2.line(img, (0, ALTEZZA_LINEA_INIZIALE), (WIDTH, ALTEZZA_LINEA_INIZIALE), (0, 255, 0), 3)
        cv2.line(img, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), (255, 0, 255), 3)
        cv2.line(img, (0, 20), (WIDTH, 20), (255, 0, 255), 3)
        cv2.imshow('Normale', img)

def omografico(x, y):
    # Converte le coordinate (x, y) utilizzando la matrice di omografia
    denom = x * MAT_OMO[6] + y * MAT_OMO[7] + MAT_OMO[8]
    x1 = (x * MAT_OMO[0] + y * MAT_OMO[1] + MAT_OMO[2]) / denom
    y1 = (x * MAT_OMO[3] + y * MAT_OMO[4] + MAT_OMO[5]) / denom
    return (x1, y1)

def calc_direction(index, punti_r):
    direction = np.degrees(np.arctan2(
        punti_r[index+2].getX() - punti_r[index].getX(),
        punti_r[index+2].getY() - punti_r[index].getY()
    ))
    return direction

def line_following():
    global punti, punti_real, controllo, K1, K2, KE

    # Calcola l'errore di direzione basato sui punti rilevati
    punti_real = list(map(lambda punto: PuntoReal(omografico(punto.getX(), punto.getY())), punti))
    
    distanza_linea = punti_real[0].getX()
    direzioni = list(map(lambda x: calc_direction(x, punti_real), list(range(3))))

    valori = [distanza_linea * KE, 
                direzioni[0] * K1,
                (direzioni[1] - direzioni[0]) * K2,
                (direzioni[2] - direzioni[1]) * K3]

    print("distanza linea =", round(distanza_linea, 2),
          " angolo direzioni =", direzioni)

    return sum(valori)

def main():
    global controllo, img

    try:
        while True:
            start_time = time.perf_counter()
            img = img_capture()
            #// SeguiLinea.greenDetect(img, punti, VISUALIZZA)
            line_processing()
            controllo = line_following()
            if MOTORI:
                Motori.ControlloMotori(controllo, VELOCITA)
            #//print(controllo) #* DEBUG
            print(time.perf_counter() - start_time) #* DEBUG
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    except KeyboardInterrupt:
        print("Interrotto dall'utente.")

if __name__ == "__main__":
    main()
    picam2.stop()