from tqdm import tqdm
import time
from random import uniform

for _ in tqdm(range(1000), desc="Calibrazione"):
    time.sleep(uniform(0.05, 0.06))  # Simula un'operazione lunga
