import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def analyze_seasonal_variation():
    # Get the project root directory (parent of src directory)
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    
    # Read the CSV file
    df = pd.read_csv(data_dir / 'Seasonal_Variation.csv')
    
    # Calculate monthly totals for each species
    monthly_totals = df.groupby('MONTH').sum()
    
    # Calculate total abundance per species
    species_totals = df.sum(numeric_only=True).sort_values(ascending=False)
    
    # Calculate species richness (number of species present) per month
    species_richness = df.groupby('MONTH').apply(
        lambda x: (x.iloc[:, 1:] > 0).sum(axis=1).mean()
    ).round(2)
    
    # Basic statistics
    print("\nOverall Species Abundance:")
    print(species_totals)
    
    print("\nSpecies Richness by Month (average number of species present):")
    print(species_richness)
    
    # Calculate diversity indices by month
    monthly_diversity = df.groupby('MONTH').apply(calculate_diversity_indices)
    print("\nDiversity Indices by Month:")
    print(monthly_diversity)
    
    # Create visualizations
    fig = plt.figure(figsize=(15, 10))
    
    # Plot 1: Monthly species abundance
    ax1 = plt.subplot(221)
    monthly_totals.plot(kind='bar', ax=ax1)
    ax1.set_title('Monthly Species Abundance')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Total Count')
    plt.xticks(rotation=45)
    
    # Plot 2: Species composition
    ax2 = plt.subplot(222)
    species_totals.plot(kind='bar', ax=ax2)
    ax2.set_title('Total Abundance by Species')
    ax2.set_xlabel('Species')
    ax2.set_ylabel('Total Count')
    plt.xticks(rotation=45)
    
    # Plot 3: Heatmap of species abundance by month
    ax3 = plt.subplot(223)
    sns.heatmap(monthly_totals, cmap='YlOrRd', ax=ax3)
    ax3.set_title('Species Abundance Heatmap')
    plt.xticks(rotation=45)
    
    # Plot 4: Species richness by month
    ax4 = plt.subplot(224)
    species_richness.plot(kind='bar', ax=ax4)
    ax4.set_title('Species Richness by Month')
    ax4.set_xlabel('Month')
    ax4.set_ylabel('Average Number of Species')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(data_dir / 'seasonal_variation_analysis.png')
    plt.close()
    
    # Create a detailed monthly composition plot
    plt.figure(figsize=(15, 8))
    monthly_totals_pct = monthly_totals.div(monthly_totals.sum(axis=1), axis=0) * 100
    monthly_totals_pct.plot(kind='bar', stacked=True)
    plt.title('Monthly Species Composition (%)')
    plt.xlabel('Month')
    plt.ylabel('Percentage')
    plt.legend(title='Species', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(data_dir / 'monthly_composition.png')
    plt.close()

def calculate_diversity_indices(group):
    # Remove the month column and get only the counts
    counts = group.iloc[:, 1:]
    
    # Calculate total abundance
    total = counts.sum().sum()
    
    # Calculate proportions for each species
    proportions = counts.sum() / total
    proportions = proportions[proportions > 0]  # Remove species with zero abundance
    
    # Shannon diversity index
    shannon = -np.sum(proportions * np.log(proportions))
    
    # Simpson diversity index
    simpson = 1 - np.sum(proportions ** 2)
    
    # Species richness
    richness = (counts > 0).sum().sum()
    
    # Pielou's evenness
    evenness = shannon / np.log(richness) if richness > 1 else 0
    
    return pd.Series({
        'Shannon_Diversity': round(shannon, 3),
        'Simpson_Diversity': round(simpson, 3),
        'Species_Richness': richness,
        'Evenness': round(evenness, 3)
    })

if __name__ == "__main__":
    analyze_seasonal_variation()
