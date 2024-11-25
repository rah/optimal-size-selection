import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Read the CSV file
df = pd.read_csv('data/Feeding-Experiments-Initial.csv')

def analyze_feeding_data():
    # Basic statistics
    print("\n=== Basic Statistics ===")
    print("\nNumber of observations:", len(df))
    print("\nSummary statistics for Fish Length:")
    print(df['Fish Length (mm)'].describe())
    print("\nSummary statistics for Prey Length:")
    print(df['Prey Length (mm)'].describe())
    
    # Count of prey types
    print("\n=== Prey Type Distribution ===")
    prey_counts = df['Prey'].value_counts()
    print(prey_counts)
    
    # Create figures directory if it doesn't exist
    import os
    if not os.path.exists('figures'):
        os.makedirs('figures')
    
    # Plotting
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Experiment', y='Fish Length (mm)', data=df)
    plt.title('Fish Length Distribution by Experiment')
    plt.savefig('figures/fish_length_by_experiment.png')
    plt.close()
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Experiment', y='Prey Length (mm)', data=df)
    plt.title('Prey Length Distribution by Experiment')
    plt.savefig('figures/prey_length_by_experiment.png')
    plt.close()
    
    # Relationship between fish length and prey length
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Fish Length (mm)', y='Prey Length (mm)', hue='Prey')
    plt.title('Fish Length vs Prey Length')
    plt.savefig('figures/fish_vs_prey_length.png')
    plt.close()
    
    # Calculate correlation
    correlation = df[['Fish Length (mm)', 'Prey Length (mm)']].corr().iloc[0,1]
    print(f"\n=== Correlation Analysis ===")
    print(f"Correlation between fish length and prey length: {correlation:.3f}")
    
    # Prey type analysis
    print("\n=== Prey Selection Analysis ===")
    prey_by_exp = pd.crosstab(df['Experiment'], df['Prey'])
    print("\nPrey counts by experiment:")
    print(prey_by_exp)
    
    # Average prey length by fish length
    avg_prey_length = df.groupby('Fish Length (mm)')['Prey Length (mm)'].mean()
    print("\nAverage prey length for each fish length:")
    print(avg_prey_length)

if __name__ == "__main__":
    analyze_feeding_data()
