import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns

# Set style
plt.style.use('dark_background')
sns.set_palette("husl")

# Parameters
initial_price = 100
position_size = 1000  # $1000 position
leverages = [2, 5, 10, 20]  # Different leverage levels to compare

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Leveraged Perpetual Swap Payoff: Option-Like Profile Due to Liquidation', 
             fontsize=16, y=1.02)

# Price range for x-axis
price_range = np.linspace(50, 150, 1000)

for idx, (ax, leverage) in enumerate(zip(axes.flat, leverages)):
    # Calculate key values
    initial_margin = position_size / leverage
    liquidation_price = initial_price * (1 - 1/leverage)
    
    # Calculate payoffs
    payoffs = []
    colors = []
    
    for price in price_range:
        if price <= liquidation_price:
            # Liquidated - lose entire margin
            payoff = -initial_margin
            colors.append('red')
        else:
            # Not liquidated - linear payoff
            price_change_pct = (price - initial_price) / initial_price
            payoff = price_change_pct * position_size
            colors.append('cyan' if payoff >= 0 else 'orange')
        
        payoffs.append(payoff)
    
    # Create scatter plot
    ax.scatter(price_range, payoffs, c=colors, alpha=0.6, s=2)
    
    # Add reference lines
    ax.axhline(y=0, color='white', linestyle='-', alpha=0.3, linewidth=1)
    ax.axvline(x=initial_price, color='white', linestyle='-', alpha=0.3, linewidth=1)
    ax.axvline(x=liquidation_price, color='yellow', linestyle='--', linewidth=2)
    
    # Add shaded regions
    ax.fill_between([50, liquidation_price], -initial_margin*1.1, initial_margin*5, 
                    alpha=0.2, color='red', label='Liquidation Zone')
    
    # Annotations
    ax.annotate(f'Liquidation\n${liquidation_price:.1f}', 
                xy=(liquidation_price, -initial_margin*0.5), 
                xytext=(liquidation_price-10, -initial_margin*0.3),
                arrowprops=dict(arrowstyle='->', color='yellow', alpha=0.7),
                fontsize=10, color='yellow', ha='right')
    
    ax.annotate(f'Max Loss\n-${initial_margin:.0f}', 
                xy=(70, -initial_margin), 
                fontsize=10, color='red', ha='center')
    
    # Add comparison with regular spot position
    spot_payoffs = [(p - initial_price) / initial_price * initial_margin for p in price_range]
    ax.plot(price_range, spot_payoffs, 'gray', linestyle=':', alpha=0.5, 
            linewidth=1, label='Unleveraged (1x)')
    
    # Styling
    ax.set_xlabel('Price ($)', fontsize=11)
    ax.set_ylabel('P&L ($)', fontsize=11)
    ax.set_title(f'{leverage}x Leverage (Margin: ${initial_margin:.0f})', fontsize=12, pad=10)
    ax.grid(True, alpha=0.2)
    ax.set_xlim(60, 140)
    ax.set_ylim(-initial_margin*1.2, initial_margin*5)
    
    # Add key metrics
    breakeven_move = 100 / leverage
    ax.text(0.02, 0.98, f'Liquidation: -{100/leverage:.1f}%\nBreakeven: +{breakeven_move:.1f}%', 
            transform=ax.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

plt.tight_layout()

# Save with high DPI
plt.savefig('leveraged_perpetual_payoff.png', dpi=300, bbox_inches='tight', facecolor='black')
print("Saved as 'leveraged_perpetual_payoff.png'")

# Create a second figure comparing to actual options
plt.figure(figsize=(12, 8))

# Parameters for comparison
leverage = 10
initial_margin = position_size / leverage
liquidation_price = initial_price * (1 - 1/leverage)

# Calculate perpetual payoff
perp_payoffs = []
for price in price_range:
    if price <= liquidation_price:
        perp_payoffs.append(-initial_margin)
    else:
        price_change_pct = (price - initial_price) / initial_price
        perp_payoffs.append(price_change_pct * position_size)

# Calculate equivalent call option payoff
# Strike at liquidation price, premium equals margin
option_strike = liquidation_price
option_premium = initial_margin
option_payoffs = []
for price in price_range:
    intrinsic_value = max(price - option_strike, 0) * leverage
    option_payoffs.append(intrinsic_value - option_premium)

# Plot both
plt.scatter(price_range[::5], perp_payoffs[::5], color='cyan', alpha=0.7, s=30, label='10x Perpetual Swap')
plt.plot(price_range, option_payoffs, color='magenta', linewidth=2.5, label=f'Equivalent Call Option (Strike ${option_strike:.0f})')

# Add reference lines
plt.axhline(y=0, color='white', linestyle='-', alpha=0.3, linewidth=1)
plt.axvline(x=initial_price, color='white', linestyle='-', alpha=0.3, linewidth=1)
plt.axvline(x=liquidation_price, color='yellow', linestyle='--', linewidth=2, label='Liquidation Price')

# Highlight the similarity
plt.fill_between(price_range, perp_payoffs, option_payoffs, 
                 where=(np.array(price_range) > liquidation_price), 
                 alpha=0.2, color='green', label='Difference')

# Annotations
plt.annotate('Option-like\nlimited downside', 
             xy=(80, -initial_margin), 
             xytext=(75, -initial_margin*0.5),
             arrowprops=dict(arrowstyle='->', color='white', alpha=0.7),
             fontsize=12, color='white', ha='center')

plt.annotate('Linear upside\n(leveraged)', 
             xy=(120, 200), 
             xytext=(125, 250),
             arrowprops=dict(arrowstyle='->', color='white', alpha=0.7),
             fontsize=12, color='white', ha='center')

# Styling
plt.xlabel('Price ($)', fontsize=14)
plt.ylabel('P&L ($)', fontsize=14)
plt.title('Leveraged Perpetual Swap vs Call Option Payoff\nShowing Option-Like Characteristics', 
          fontsize=16, pad=20)
plt.grid(True, alpha=0.3)
plt.legend(loc='upper left', fontsize=12)
plt.xlim(60, 140)
plt.ylim(-150, 400)

# Add info box
info_text = (f"10x Leverage Perpetual:\n"
             f"• Initial Margin: ${initial_margin:.0f}\n"
             f"• Max Loss: ${initial_margin:.0f}\n"
             f"• Liquidation at: ${liquidation_price:.0f}\n"
             f"• Breakeven at: ${initial_price + initial_price/leverage:.0f}")
plt.text(0.02, 0.5, info_text, transform=plt.gca().transAxes, fontsize=10,
         bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))

plt.tight_layout()

# Save the comparison
plt.savefig('perpetual_vs_option_payoff.png', dpi=300, bbox_inches='tight', facecolor='black')
print("Saved as 'perpetual_vs_option_payoff.png'")

plt.show()

# Print analysis
print("\n" + "="*60)
print("LEVERAGED PERPETUAL SWAP: OPTION-LIKE PAYOFF ANALYSIS")
print("="*60)

for leverage in leverages:
    margin = position_size / leverage
    liq_price = initial_price * (1 - 1/leverage)
    print(f"\n{leverage}x Leverage:")
    print(f"  - Initial Margin: ${margin:.0f}")
    print(f"  - Position Size: ${position_size:.0f}")
    print(f"  - Liquidation Price: ${liq_price:.2f} (-{100/leverage:.1f}%)")
    print(f"  - Max Loss: ${margin:.0f} (same as option premium)")
    print(f"  - Breakeven Move: +{100/leverage:.1f}%")
    print(f"  - Effective Delta at Entry: {leverage}")

print("\n" + "="*60)
print("KEY INSIGHT: Leveraged perpetuals have option-like payoffs!")
print("="*60)
print("1. LIMITED DOWNSIDE: Can only lose your margin (like option premium)")
print("2. UNLIMITED UPSIDE: Linear gains above liquidation (like deep ITM option)")
print("3. BINARY OUTCOME: Below liquidation = total loss (like OTM option expiry)")
print("4. HIGHER LEVERAGE = MORE OPTION-LIKE: Tighter liquidation = more binary")