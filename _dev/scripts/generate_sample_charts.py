import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# When running from _dev/scripts, place images into gold_standard/docs/images
OUT = Path(__file__).resolve().parents[2] / 'gold_standard' / 'docs' / 'images'
OUT.mkdir(parents=True, exist_ok=True)

# Chart 1 - Structure (price with support/resistance)
np.random.seed(0)
x = np.arange(0, 200)
price = np.cumsum(np.random.randn(200)) + 100
plt.figure(figsize=(6,3))
plt.plot(x, price, color='black')
plt.fill_between(x, price-2, price+2, color='#f0f0f0')
plt.title('Price Structure')
plt.savefig(OUT / 'chart_structure.png', bbox_inches='tight')
plt.close()

# Chart 2 - Volatility
vol = np.abs(np.random.randn(200))*2
plt.figure(figsize=(6,3))
plt.plot(x, vol, color='red')
plt.title('Volatility')
plt.savefig(OUT / 'chart_volatility.png', bbox_inches='tight')
plt.close()

# Chart 3 - Range / Expansion
window = 10
range_ = [np.max(price[i:i+window]) - np.min(price[i:i+window]) for i in range(len(price)-window)]
plt.figure(figsize=(6,3))
plt.plot(range_, color='blue')
plt.title('Range / Expansion')
plt.savefig(OUT / 'chart_range.png', bbox_inches='tight')
plt.close()

# Chart 4 - Multi-timeframe context
plt.figure(figsize=(6,3))
plt.plot(x, price, label='1m')
plt.plot(x[::5], price[::5], label='5m')
plt.legend()
plt.title('Multi-timeframe Context')
plt.savefig(OUT / 'chart_multi_tf.png', bbox_inches='tight')
plt.close()

# Chart 5 - Risk profile (histogram)
returns = np.diff(price)/price[:-1]
plt.figure(figsize=(6,3))
plt.hist(returns, bins=30, color='purple')
plt.title('Risk Profile (Returns)')
plt.savefig(OUT / 'chart_risk.png', bbox_inches='tight')
plt.close()

# Chart 6 - Comparative behavior
plt.figure(figsize=(6,3))
plt.plot(x, np.cumsum(np.random.randn(200))+80, label='Asset A')
plt.plot(x, np.cumsum(np.random.randn(200))+100, label='Asset B')
plt.legend()
plt.title('Comparative Behavior')
plt.savefig(OUT / 'chart_comparative.png', bbox_inches='tight')
plt.close()

def main():
    print('Charts generated in', OUT)

if __name__ == '__main__':
    main()
