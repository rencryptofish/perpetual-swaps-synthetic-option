import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import matplotlib.patches as mpatches

# Set style
plt.style.use('dark_background')

# Function to calculate expected time to liquidation
def expected_liquidation_time(leverage, volatility, drift=0, funding=0):
    """
    Calculate expected time to liquidation in days
    
    Parameters:
    - leverage: Leverage ratio (e.g., 10 for 10x)
    - volatility: Annual volatility as decimal (e.g., 0.5 for 50%)
    - drift: Annual drift rate as decimal
    - funding: Annual funding rate as decimal
    """
    # Net drift after funding
    mu = drift - funding
    
    # Liquidation distance
    liquidation_distance = 1 / leverage
    
    # Calculate expected time
    denominator = mu + 0.5 * volatility**2
    
    if denominator <= 0:
        # If drift is very negative, liquidation is almost certain and quick
        return 365 / (leverage * volatility**2)
    
    expected_time = -np.log(1 - liquidation_distance) / denominator
    return expected_time * 365  # Convert to days

# Create the main heatmap
def create_liquidation_heatmap(drift=0, funding=0, save_path='liquidation_heatmap.png'):
    # Define leverage and volatility ranges
    leverages = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 50, 100]
    volatilities = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 175, 200, 250, 300]
    
    # Create matrix for heatmap
    liquidation_times = np.zeros((len(volatilities), len(leverages)))
    
    for i, vol in enumerate(volatilities):
        for j, lev in enumerate(leverages):
            days = expected_liquidation_time(lev, vol/100, drift/100, funding/100)
            liquidation_times[i, j] = days
    
    # Create custom colormap
    colors = ['#8b0000', '#ff4444', '#ff8844', '#ffcc44', '#88ff88', '#00aa00']
    n_bins = 6
    cmap = LinearSegmentedColormap.from_list('liquidation', colors, N=n_bins)
    
    # Define boundaries for color mapping
    bounds = [0, 1, 7, 30, 90, 365, np.inf]
    norm = BoundaryNorm(bounds, cmap.N)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create heatmap with log scale
    # Use log scale for better visualization
    log_times = np.log10(liquidation_times + 1)  # Add 1 to avoid log(0)
    
    im = ax.imshow(log_times, cmap=cmap, aspect='auto', 
                   norm=BoundaryNorm(np.log10(np.array(bounds[:-1]) + 1), cmap.N))
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(leverages)))
    ax.set_yticks(np.arange(len(volatilities)))
    ax.set_xticklabels([f'{lev}x' for lev in leverages])
    ax.set_yticklabels([f'{vol}%' for vol in volatilities])
    
    # Rotate the tick labels and set their alignment
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add text annotations
    for i in range(len(volatilities)):
        for j in range(len(leverages)):
            days = liquidation_times[i, j]
            if days < 1:
                text = f'{days*24:.0f}h'
            elif days < 7:
                text = f'{days:.1f}d'
            elif days < 30:
                text = f'{days/7:.1f}w'
            elif days < 365:
                text = f'{days/30:.0f}mo'
            else:
                text = f'{days/365:.1f}y'
            
            # Choose text color based on background
            text_color = 'white' if days < 30 else 'black'
            ax.text(j, i, text, ha="center", va="center", 
                   color=text_color, fontsize=8, fontweight='bold')
    
    # Labels and title
    ax.set_xlabel('Leverage', fontsize=14, fontweight='bold')
    ax.set_ylabel('Volatility', fontsize=14, fontweight='bold')
    
    title_text = 'Expected Time to Liquidation Analysis\n'
    if drift != 0 or funding != 0:
        title_text += f'(Drift: {drift}% | Funding: {funding}%)'
    else:
        title_text += '(Zero Drift, Zero Funding)'
    ax.set_title(title_text, fontsize=16, fontweight='bold', pad=20)
    
    # Create custom legend
    legend_elements = [
        mpatches.Patch(color='#8b0000', label='< 1 day (Extreme Risk)'),
        mpatches.Patch(color='#ff4444', label='1-7 days (Very High Risk)'),
        mpatches.Patch(color='#ff8844', label='1-4 weeks (High Risk)'),
        mpatches.Patch(color='#ffcc44', label='1-3 months (Medium Risk)'),
        mpatches.Patch(color='#88ff88', label='3-12 months (Low Risk)'),
        mpatches.Patch(color='#00aa00', label='> 1 year (Safe)')
    ]
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Add grid
    ax.set_xticks(np.arange(len(leverages))-.5, minor=True)
    ax.set_yticks(np.arange(len(volatilities))-.5, minor=True)
    ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", size=0)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')
    plt.show()
    
    return liquidation_times

# Create scenario analysis table
def create_scenario_table(drift=0, funding=0, save_path='liquidation_scenarios.png'):
    scenarios = [
        ('Conservative Stock', 15, 2),
        ('Moderate Stock', 20, 3),
        ('Aggressive Stock', 30, 5),
        ('Conservative Crypto', 40, 2),
        ('Moderate Crypto', 50, 5),
        ('Aggressive Crypto', 70, 10),
        ('Altcoin Conservative', 80, 3),
        ('Altcoin Moderate', 100, 5),
        ('Altcoin Aggressive', 100, 10),
        ('Meme Coin', 150, 10),
        ('Ultra Degen', 200, 20)
    ]
    
    # Calculate times for each scenario
    results = []
    for name, vol, lev in scenarios:
        days = expected_liquidation_time(lev, vol/100, drift/100, funding/100)
        
        if days < 1:
            time_str = f'{days*24:.1f} hours'
            risk = 'EXTREME'
            color = '#ff0000'
        elif days < 7:
            time_str = f'{days:.1f} days'
            risk = 'VERY HIGH'
            color = '#ff4444'
        elif days < 30:
            time_str = f'{days/7:.1f} weeks'
            risk = 'HIGH'
            color = '#ff8844'
        elif days < 90:
            time_str = f'{days/30:.0f} months'
            risk = 'MEDIUM'
            color = '#ffcc44'
        elif days < 365:
            time_str = f'{days/30:.0f} months'
            risk = 'LOW'
            color = '#88ff88'
        else:
            time_str = f'{days/365:.1f} years'
            risk = 'SAFE'
            color = '#00aa00'
        
        results.append({
            'Scenario': name,
            'Volatility': f'{vol}%',
            'Leverage': f'{lev}x',
            'Expected Time': time_str,
            'Risk Level': risk,
            'Days': days,
            'Color': color
        })
    
    # Create figure for table
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table data
    df = pd.DataFrame(results)
    table_data = df[['Scenario', 'Volatility', 'Leverage', 'Expected Time', 'Risk Level']].values
    
    # Create table
    table = ax.table(cellText=table_data,
                     colLabels=['Scenario', 'Volatility', 'Leverage', 'Expected Time', 'Risk Level'],
                     cellLoc='center',
                     loc='center')
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    
    # Color code the cells
    for i, result in enumerate(results):
        # Color the risk level cell
        table[(i+1, 4)].set_facecolor(result['Color'])
        table[(i+1, 4)].set_text_props(weight='bold', color='black' if result['Days'] > 30 else 'white')
        
        # Color the expected time cell with lighter version
        table[(i+1, 3)].set_facecolor(result['Color'])
        table[(i+1, 3)].set_alpha(0.5)
    
    # Style header
    for i in range(5):
        table[(0, i)].set_facecolor('#4a9eff')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    plt.title('Liquidation Risk Scenarios\nCommon Trading Setups', 
              fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')
    plt.show()

# Create a 3D surface plot for better visualization
def create_3d_surface(drift=0, funding=0, save_path='liquidation_3d.png'):
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create mesh
    leverages = np.linspace(2, 50, 50)
    volatilities = np.linspace(10, 200, 50)
    L, V = np.meshgrid(leverages, volatilities)
    
    # Calculate liquidation times
    Z = np.zeros_like(L)
    for i in range(len(volatilities)):
        for j in range(len(leverages)):
            Z[i, j] = expected_liquidation_time(L[i, j], V[i, j]/100, drift/100, funding/100)
    
    # Cap at 365 days for visualization
    Z = np.minimum(Z, 365)
    
    # Create surface plot
    surf = ax.plot_surface(L, V, Z, cmap='RdYlGn_r', alpha=0.8, 
                          linewidth=0, antialiased=True)
    
    # Add contour lines
    contours = ax.contour(L, V, Z, levels=[1, 7, 30, 90, 365], 
                         colors='black', alpha=0.4, linewidths=2)
    ax.clabel(contours, inline=True, fontsize=10)
    
    # Labels
    ax.set_xlabel('Leverage', fontsize=12)
    ax.set_ylabel('Volatility (%)', fontsize=12)
    ax.set_zlabel('Expected Days to Liquidation', fontsize=12)
    ax.set_title(f'3D Liquidation Surface\n(Drift: {drift}%, Funding: {funding}%)', 
                fontsize=14, fontweight='bold')
    
    # Add colorbar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    # Adjust viewing angle
    ax.view_init(elev=25, azim=45)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')
    plt.show()

# Main execution
if __name__ == "__main__":
    # Create all visualizations with default parameters (zero drift, zero funding)
    print("Creating liquidation time heatmap...")
    liquidation_matrix = create_liquidation_heatmap(drift=0, funding=0)
    
    print("\nCreating scenario analysis table...")
    create_scenario_table(drift=0, funding=0)
    
    print("\nCreating 3D surface plot...")
    create_3d_surface(drift=0, funding=0)
    
    # Example with different parameters
    print("\nCreating heatmap with positive drift (bull market)...")
    create_liquidation_heatmap(drift=10, funding=5, save_path='liquidation_heatmap_bullish.png')
    
    # Print some example calculations
    print("\n" + "="*60)
    print("EXAMPLE CALCULATIONS")
    print("="*60)
    
    examples = [
        (10, 50, "10x leverage, 50% volatility (Bitcoin-like)"),
        (10, 100, "10x leverage, 100% volatility (Altcoin)"),
        (5, 50, "5x leverage, 50% volatility"),
        (20, 30, "20x leverage, 30% volatility")
    ]
    
    for lev, vol, desc in examples:
        days = expected_liquidation_time(lev, vol/100)
        print(f"{desc}: {days:.1f} days expected")