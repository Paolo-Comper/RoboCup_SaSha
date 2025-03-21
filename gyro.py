import time
import smbus2
import numpy as np
import random
import tqdm

MPU_ADDRESS = 0x68
PWR_MGMT_1 = 0x6B
GYRO_CONFIG = 0x1B  # Registro per la configurazione del giroscopio
GYRO_XOUT_H = 0x43

bus = smbus2.SMBus(1)
bus.write_byte_data(MPU_ADDRESS, PWR_MGMT_1, 0)
# Configura il giroscopio per una scala a �250�/sec
bus.write_byte_data(MPU_ADDRESS, GYRO_CONFIG, 0x00)

angle_x, angle_y, angle_z = 0, 0, 0

def calibra():
    """ 
    Calibra il giroscopio per compensare gli errori di deriva.
    :return: le costanti di calibrazione per ciascun asse.
    """
    valori_x, valori_y, valori_z = [], [], []
    
    print("Calibrazione in corso...")
    for _ in tqdm(range(1000), desc="Calibrazione"):  # Raccogliamo tante letture per una media piu stabile
        gyroX, gyroY, gyroZ = getGyro()
        valori_x.append(gyroX)
        valori_y.append(gyroY)
        valori_z.append(gyroZ)
        time.sleep(random.uniform(0.05, 0.06))  # Piccola pausa tra le letture per evitare rumore eccessivo

    # Calcoliamo la media degli errori di deriva
    offset_x = np.mean(valori_x)
    offset_y = np.mean(valori_y)
    offset_z = np.mean(valori_z)

    print(f"Offset calcolati: X={offset_x:.2f}, Y={offset_y:.2f}, Z={offset_z:.2f}")
    return offset_x, offset_y, offset_z

def leggiMisura(cX : float, cY : float, cZ : float):
    """
    Ottiene il valore corretto dell'angolo in gradi per ciascun asse.
    :param cX: Costante di calibrazione per l'asse X.
    :param cY: Costante di calibrazione per l'asse Y.
    :param cZ: Costante di calibrazione per l'asse Z.
    :return: gli angoli del giroscopio.
    """
    global angle_x, angle_y, angle_z, tempo
    gyroX, gyroY, gyroZ = getGyro()
    now = time.perf_counter()
    dt = now - tempo
    tempo = now

    # Integra le velocit� angolari per ottenere gli angoli
    angle_x += (gyroX - cX) * dt
    angle_y += (gyroY - cY) * dt
    angle_z += (gyroZ - cZ) * dt
    return angle_x, angle_y, angle_z  # Sottraiamo gli offset calcolati

def getGyro(): #usa la funzine read_word per leggere i valori del giroscopio e li trasforma in gradi al secondo
    """
    Legge i vlori grezzi del giroscopio e li converte in gradi al secondo.
    :return: i valori grezzi del giroscopio sulle tre assi in gradi al secondo.
    """
    return (read_word(GYRO_XOUT_H) / 131.0), (read_word(GYRO_XOUT_H + 2) / 131.0), (read_word(GYRO_XOUT_H + 4) / 131.0)

def read_word(adr):
    """
    Legge dai reglistri del giroscopio 2 byte e li combina in un valore a 16 bit.
    :param adr: Indirizzo del primo registro da leggere.
    """
    high = bus.read_byte_data(MPU_ADDRESS, adr)
    low = bus.read_byte_data(MPU_ADDRESS, adr + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return value

def main():
    cX, cY, cZ = calibra()  # Calibrazione iniziale

    while True:
        gyroX, gyroY, gyroZ = leggiMisura(cX, cY, cZ)  # Lettura compensata

        print(f"Angoli corretti - X: {gyroX:.2f}, Y: {gyroY:.2f}, Z: {gyroZ:.2f}")

        time.sleep(0.5)  # Ritardo per stabilizzare le letture

if __name__ == "__main__":
    main()
