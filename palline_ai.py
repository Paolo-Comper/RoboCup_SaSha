import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

# Inizializzazione videocamera USB
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Errore nell'apertura della videocamera")
    exit()

# Caricamento di un modello PyTorch lightweight (esempio: MobileNetV2)
model = torch.hub.load('ultralytics/yolov5', 'yolov5n')  # YOLOv5 Nano, leggero per Raspberry Pi
model.eval()

# Ciclo principale
try:
    while True:
        # Cattura del frame dalla videocamera
        ret, frame = camera.read()
        if not ret:
            print("Errore nella lettura del frame dalla videocamera")
            break

        # Conversione del frame in RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Esegui rilevamento oggetti utilizzando il modello
        results = model(frame_rgb)

        # Ottieni le coordinate delle palline rilevate
        detections = results.pandas().xyxy[0]  # DataFrame con i risultati

        for _, detection in detections.iterrows():
            x_min, y_min, x_max, y_max, conf, class_id, label = detection
            if label == "sports ball":  # Sostituisci con il nome corretto se necessario
                cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
                cv2.putText(frame, label, (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Mostra il frame elaborato
        cv2.imshow("Rilevamento palline", frame)
        
        # Premi 'q' per uscire
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrotto manualmente dall'utente")

# Chiusura della videocamera e delle finestre
camera.release()
cv2.destroyAllWindows()
