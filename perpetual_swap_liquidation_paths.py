import numpy as np
import matplotlib.pyplot as plt

# Set style
plt.style.use('dark_background')

# Parameters
initial_price = 100
leverage = 10
n_paths = 100
n_steps = 90  # Number of time steps (days)
dt = 1/365  # Daily steps
volatility = 0.5  # 50% annual volatility
drift = 0.0  # Neutral drift

# Calculate liquidation price
liquidation_price = initial_price * (1 - 1/leverage)

print(f"Initial Price: ${initial_price}")
print(f"Leverage: {leverage}x")
print(f"Liquidation Price: ${liquidation_price:.2f}")
print(f"Distance to Liquidation: {(1/leverage)*100:.1f}%")

# Simulate paths
np.random.seed(42)
paths = []
liquidated = []
liquidation_times = []

for i in range(n_paths):
    # Generate random walk
    returns = np.random.normal(drift * dt, volatility * np.sqrt(dt), n_steps)
    price_path = initial_price * np.exp(np.cumsum(returns))
    price_path = np.insert(price_path, 0, initial_price)
    
    # Check for liquidation
    liquidation_idx = np.where(price_path <= liquidation_price)[0]
    
    if len(liquidation_idx) > 0:
        # Path was liquidated
        liq_time = liquidation_idx[0]
        # Set all prices after liquidation to NaN for plotting
        price_path[liq_time:] = np.nan
        liquidated.append(True)
        liquidation_times.append(liq_time)
    else:
        liquidated.append(False)
        liquidation_times.append(n_steps)
    
    paths.append(price_path)

# Convert to numpy arrays
paths = np.array(paths)
liquidated = np.array(liquidated)
liquidation_times = np.array(liquidation_times)

# Calculate statistics
n_liquidated = np.sum(liquidated)
pct_liquidated = (n_liquidated / n_paths) * 100
avg_liquidation_time = np.mean(liquidation_times[liquidated]) if n_liquidated > 0 else n_steps

print(f"\nSimulation Results:")
print(f"Paths Liquidated: {n_liquidated}/{n_paths} ({pct_liquidated:.1f}%)")
print(f"Average Time to Liquidation: {avg_liquidation_time:.1f} days")

# Create the main plot
plt.figure(figsize=(14, 8))
time_axis = np.arange(n_steps + 1)

# Plot surviving paths
for i, path in enumerate(paths):
    if not liquidated[i]:
        plt.plot(time_axis, path, alpha=0.5, linewidth=1.2, color='cyan')

# Plot liquidated paths
for i, path in enumerate(paths):
    if liquidated[i]:
        plt.plot(time_axis, path, alpha=0.7, linewidth=1.5, color='red')

# Add liquidation line
plt.axhline(y=liquidation_price, color='yellow', linestyle='--', linewidth=2, 
            label=f'Liquidation Level (${liquidation_price:.2f})')
plt.axhline(y=initial_price, color='white', linestyle='-', alpha=0.5, linewidth=1, 
            label=f'Initial Price (${initial_price})')

# Styling
plt.xlabel('Time (days)', fontsize=12)
plt.ylabel('Price ($)', fontsize=12)
plt.title(f'Path Dependence in {leverage}x Leveraged Perpetual Swaps\n{n_paths} Simulated Paths, {volatility*100:.0f}% Volatility\n{pct_liquidated:.1f}% Liquidated | Avg Liquidation Time: {avg_liquidation_time:.1f} days', 
          fontsize=14, pad=20)
plt.grid(True, alpha=0.3)
plt.legend(loc='upper right', fontsize=10)
plt.xlim(0, n_steps)
plt.ylim(liquidation_price - 10, initial_price + 60)

# Add annotation
plt.annotate(f'{n_liquidated} paths\nliquidated', 
             xy=(50, liquidation_price - 5), 
             fontsize=10, 
             color='red',
             ha='left')

plt.tight_layout()

# Save the figure with high DPI
plt.savefig('perpetual_swap_liquidation_paths.png', dpi=300, bbox_inches='tight', facecolor='black')
print(f"\nFigure saved as 'perpetual_swap_liquidation_paths.png' with 300 DPI")

plt.show()