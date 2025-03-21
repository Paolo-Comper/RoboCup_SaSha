import cv2
import numpy as np
from picamera2 import Picamera2

# Inizializza Picamera2
picam2 = Picamera2()
Dimensioni = (480, 640, 3)
# Configura la fotocamera per la visualizzazione in anteprima
preview_config = picam2.create_preview_configuration(main={"size": (Dimensioni[1], Dimensioni[0])})
picam2.configure(preview_config)

# Avvia la fotocamera
picam2.start()

print("Premi 's' per scattare la foto, oppure 'q' per uscire.")

i = 0
images = ["foto0.jpg"]

while True:
    # Cattura un frame dalla fotocamera
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.line(frame, (int(Dimensioni[1]/2), 0), (int(Dimensioni[1]/2), Dimensioni[0]), (255, 0, 255), 3)
    cv2.line(frame, (0, Dimensioni[0]-20), (Dimensioni[1], Dimensioni[0]-20), (255, 0, 255), 3)
    cv2.line(frame, (0, 20), (Dimensioni[1], 20), (255, 0, 255), 3)
    # Mostra il frame in una finestra di anteprima
    cv2.imshow("Anteprima", frame)

    # Aspetta un tasto premuto
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):  # Premi 's' per scattare la foto
        filename = f"foto{i}.jpg"
        picam2.capture_file(filename)
        print(f"Foto salvata come: {filename}")
        images.append(filename)
        i += 1

    elif key == ord('q'):  # Premi 'q' per uscire
        print("Uscita.")
        break

# Ferma la fotocamera e chiudi la finestra
picam2.stop()
cv2.destroyAllWindows()

# Carica l'ultima immagine scattata per selezionare i punti
if images:
    img = cv2.imread(images[-1])
    print("Seleziona manualmente 9 punti sull'immagine.")

    # Lista per memorizzare i punti selezionati
    points = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # Quando clicchi con il tasto sinistro
            points.append((x, y))
            print(f"Punto selezionato: {x}, {y}")
            # Disegna un cerchio sul punto selezionato
            cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Seleziona i punti", img)

    # Mostra l'immagine e attendi la selezione dei punti
    cv2.imshow("Seleziona i punti", img)
    cv2.setMouseCallback("Seleziona i punti", mouse_callback)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(points) == 9:
        print("Punti selezionati:", points)

        # Organizza i punti in una matrice 3x3
        points_matrix = np.array(points, dtype="float32").reshape(3, 3, 2)
        print("Matrice 3x3 dei punti selezionati:")
        print(points_matrix)

    else:
        print("Non sono stati selezionati 9 punti. Operazione annullata.")
else:
    print("Nessuna immagine scattata.")
