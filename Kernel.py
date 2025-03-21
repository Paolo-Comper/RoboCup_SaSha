import numpy as np
import cv2

def rounded_square_kernel(size, radius):
    """
    Crea un kernel quadrato con bordi arrotondati.
    
    :param size: Dimensione del kernel (size x size).
    :param radius: Raggio di arrotondamento degli angoli.
    :return: Kernel binario con forma quadrata e angoli arrotondati.
    """
    kernel = np.ones((size, size), dtype=np.uint8)

    # Creiamo una maschera circolare per arrotondare gli angoli
    mask = np.zeros((size, size), dtype=np.uint8)
    cv2.circle(mask, (radius, radius), radius, 1, -1)
    cv2.circle(mask, (size - radius - 1, radius), radius, 1, -1)
    cv2.circle(mask, (radius, size - radius - 1), radius, 1, -1)
    cv2.circle(mask, (size - radius - 1, size - radius - 1), radius, 1, -1)

    # Sovrapponiamo la maschera al kernel
    kernel = np.bitwise_and(kernel, mask)

    return kernel