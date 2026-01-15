
import numpy as np
import pandas as pd

def simulate_entropy_decay():
    time = np.arange(0, 200)
    entropy = 100 * np.exp(-0.01 * time)
    pd.DataFrame({'time': time, 'entropy': entropy}).to_csv('entropy_sim_test.csv', index=False)

if __name__ == '__main__':
    simulate_entropy_decay()
