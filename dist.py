import time
import smbus2

VL53L0X_ADDRESS = 0x29  # Indirizzo del sensore di distanza
REG_MEASURE = 0x00  # Registro per iniziare la misura (ipotetico, vedere datasheet)
REG_RESULT = 0x1E  # Registro dove leggere il valore della distanza

bus = smbus2.SMBus(1)

def write_byte(address, register, value):
    bus.write_byte_data(address, register, value)

def read_word(address, register):
    high = bus.read_byte_data(address, register)
    low = bus.read_byte_data(address, register + 1)
    value = (high << 8) + low
    return value

def get_distanza():
    """ Ottiene la distanza dal sensore VL53L0X in millimetri. """
    write_byte(VL53L0X_ADDRESS, REG_MEASURE, 0x01)  # Avvia misura
    time.sleep(0.05)  # Attendi completamento misura
    distanza = read_word(VL53L0X_ADDRESS, REG_RESULT)
    
    # Filtra i valori errati
    if distanza == 20 or distanza > 500:  # Se valore sospetto o troppo grande
        return 9999  # Valore arbitrario alto per indicare "nessun ostacolo"
    
    return distanza


def main():
    while True:
        distanza = get_distanza()
        print(f"Distanza: {distanza:.2f} mm")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
