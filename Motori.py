from gpiozero import Motor
import numpy as np

# +-----------------------+
# | CONFIGURAZIONE MOTORI |
# +-----------------------+

PWM_FREQUENCY = 100
VELMIN = 0.3
VELSTOP = 0.05

# Definizione dei pin dei motori (prima coppia: destro, seconda: sinistro)
MOTOR_PINS = {
    'dx': (18, 19),  # (forward, backward)
    'sx': (13, 12)
}

# Inizializzazione dei motori
motorDX = Motor(forward=MOTOR_PINS['dx'][0], backward=MOTOR_PINS['dx'][1])
motorSX = Motor(forward=MOTOR_PINS['sx'][0], backward=MOTOR_PINS['sx'][1])

def controlloMotore(motor, potenza):
    # Controlla un motore in base alla potenza espressa in percentuale.
    # Calcola il valore normalizzato (tra 0 e 1)
    power = np.clip(abs(potenza) / 100, 0, 1)
    power = (power-VELSTOP)*(1-VELMIN)/(1-VELSTOP)+VELMIN
    if potenza > 5:
        motor.forward(power)
    elif potenza < -5:
        motor.backward(power)
    else:
        motor.stop()

def ControlloMotori(direzione, velocita):
    """
    Gestisce il controllo simultaneo dei motori destro e sinistro in base
    """
    # Gestisce il controllo simultaneo dei motori destro e sinistro in base 
    # al parametro 'direzione' (tra -100 e 100) e alla velocita base.
    
    direzione = np.clip(direzione, -100, 100)
    print("MotoreDX =", velocita - direzione, "MotoreSX =", velocita + direzione)
    controlloMotore(motorDX, velocita - direzione)
    controlloMotore(motorSX, velocita + direzione)
