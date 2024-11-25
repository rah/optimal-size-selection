import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
from pathlib import Path

def analyze_head_depth_length():
    # Get the project root directory (parent of src directory)
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    
    # Read the CSV file
    df = pd.read_csv(data_dir / 'AMA_HeadDepth_Length.csv')
    
    # Basic statistical analysis
    print("\nBasic Statistics:")
    print(df.describe())
    
    # Calculate correlation coefficient
    correlation = df['Length'].corr(df['Head Depth'])
    print(f"\nCorrelation coefficient between Length and Head Depth: {correlation:.3f}")
    
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(df['Length'], df['Head Depth'])
    print(f"\nLinear Regression Results:")
    print(f"Slope: {slope:.4f}")
    print(f"Intercept: {intercept:.4f}")
    print(f"R-squared: {r_value**2:.4f}")
    print(f"P-value: {p_value:.4f}")
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Length', y='Head Depth', alpha=0.6)
    
    # Add regression line
    x = df['Length']
    plt.plot(x, slope * x + intercept, color='red', label=f'Regression line (R² = {r_value**2:.3f})')
    
    plt.title('Length vs Head Depth Analysis')
    plt.xlabel('Length')
    plt.ylabel('Head Depth')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save the plot
    plt.savefig(data_dir / 'length_vs_head_depth_analysis.png')
    plt.close()

if __name__ == "__main__":
    analyze_head_depth_length()
