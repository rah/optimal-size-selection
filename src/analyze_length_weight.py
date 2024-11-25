import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np
from pathlib import Path

def analyze_length_weight():
    # Get the project root directory (parent of src directory)
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    
    # Read the CSV file
    df = pd.read_csv(data_dir / 'AMA_Length_Weight.csv')
    
    # Basic statistical analysis
    print("\nBasic Statistics:")
    print(df.describe())
    
    # Calculate correlation coefficient
    correlation = df['Length'].corr(df['Weight'])
    print(f"\nCorrelation coefficient between Length and Weight: {correlation:.3f}")
    
    # Log transform the data (common in length-weight relationships)
    df['Log_Length'] = np.log(df['Length'])
    df['Log_Weight'] = np.log(df['Weight'])
    
    # Perform linear regression on log-transformed data
    # This follows the equation: log(W) = log(a) + b*log(L)
    # Which is equivalent to W = a*L^b
    slope, intercept, r_value, p_value, std_err = stats.linregress(df['Log_Length'], df['Log_Weight'])
    
    print(f"\nLength-Weight Relationship Analysis:")
    print(f"Log-Linear Regression Results:")
    print(f"Slope (b): {slope:.4f}")  # This is the scaling factor
    print(f"Intercept (log a): {intercept:.4f}")
    print(f"a coefficient: {np.exp(intercept):.4f}")  # Back-transformed intercept
    print(f"R-squared: {r_value**2:.4f}")
    print(f"P-value: {p_value:.4f}")
    
    # Create visualizations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Original scale plot
    sns.scatterplot(data=df, x='Length', y='Weight', alpha=0.6, ax=ax1)
    x = np.linspace(df['Length'].min(), df['Length'].max(), 100)
    y = np.exp(intercept) * x**slope
    ax1.plot(x, y, color='red', label=f'Power law fit\nW = {np.exp(intercept):.4f}*L^{slope:.4f}')
    ax1.set_title('Length vs Weight (Original Scale)')
    ax1.set_xlabel('Length')
    ax1.set_ylabel('Weight')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Log-log plot
    sns.scatterplot(data=df, x='Log_Length', y='Log_Weight', alpha=0.6, ax=ax2)
    x_log = np.linspace(df['Log_Length'].min(), df['Log_Length'].max(), 100)
    ax2.plot(x_log, intercept + slope * x_log, color='red', 
             label=f'Linear fit\nlog(W) = {intercept:.4f} + {slope:.4f}*log(L)')
    ax2.set_title('Log(Length) vs Log(Weight)')
    ax2.set_xlabel('Log(Length)')
    ax2.set_ylabel('Log(Weight)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(data_dir / 'length_weight_analysis.png')
    plt.close()

if __name__ == "__main__":
    analyze_length_weight()
