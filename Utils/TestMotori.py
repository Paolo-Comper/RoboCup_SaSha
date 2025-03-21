from gpiozero import Motor
import numpy as np
from time import sleep

PWM_FREQUENCY = 100
VelocitaMin = 30
Motori = [[18, 19], [13, 12]] #primo DX secondo SX
kv = 1.3 #usa valori max di 2

# Definizione dei motori
motorDX = Motor(forward=Motori[0][0], backward=Motori[0][1])
motorSX = Motor(forward=Motori[1][0], backward=Motori[1][1])

def setup_pins():
    # Non � necessario configurare i pin con gpiozero
    pass

def cleanup():
    # gpiozero non richiede una specifica funzione di cleanup
    pass

def controlloMotoreDX(potenza):
    if potenza > 0:
        motorDX.forward(np.clip(potenza * kv / 100, 0, 1))
    elif potenza < 0:
        motorDX.backward(np.clip(abs(potenza) * kv / 100, 0, 1))
    else:
        motorDX.stop()

def controlloMotoreSX(potenza):
    if potenza > 0:
        motorSX.forward(np.clip(potenza * kv / 100, 0, 1))
    elif potenza < 0:
        motorSX.backward(np.clip(abs(potenza) * kv / 100, 0, 1))
    else:
        motorSX.stop()

#non eliminare sta fottutissima funzione
def ControlloMotori(direzione, velocita):
    print(direzione)
    direzione = np.clip(direzione, -100, 100)
    VelocitaDX = velocita * (1 - direzione / 100)
    VelocitaSX = velocita * (1 + direzione / 100)

    #controllo motore destro
    controlloMotoreDX(VelocitaDX)

    #controllo motore sinistro
    controlloMotoreSX(VelocitaSX)

# Main
if __name__ == "__main__":
    try:
        setup_pins()
        # Esempio di utilizzo di ControlloMotori
        ControlloMotori(0, 50)
        sleep(2)
        ControlloMotori(0, 0)
    except KeyboardInterrupt:
        print("Interrotto dall'utente")
    finally:
        cleanup()
        print("Pulizia dei pin completata")
