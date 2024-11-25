import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

def analyze_habitat_complexity():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    
    # Read the CSV file
    df = pd.read_csv(data_dir / 'Benthos-Habitat-Complexity-25-26-6-83.csv')
    
    # Clean the data
    # Replace '#N/A' with np.nan
    df = df.replace('#N/A', np.nan)
    
    # Convert numeric columns to float
    numeric_cols = df.columns[2:]  # All columns after Category
    df[numeric_cols] = df[numeric_cols].astype(float)
    
    # Basic summary statistics by category
    print("\n1. Summary Statistics by Habitat Category:")
    category_summary = df.groupby('Category').agg({
        'Seagrass Wt (gms)': ['count', 'mean', 'std', 'min', 'max']
    })
    print(category_summary)
    
    # Species abundance by habitat category
    species_cols = df.columns[3:]  # All columns after Seagrass Wt
    abundance_by_category = df.groupby('Category')[species_cols].sum()
    print("\n2. Total Species Abundance by Habitat Category:")
    print(abundance_by_category)
    
    # Calculate species richness and diversity indices
    diversity_metrics = calculate_diversity_metrics(df, species_cols)
    print("\n3. Diversity Metrics by Habitat Category:")
    print(diversity_metrics)
    
    # Correlation analysis
    print("\n4. Correlation between Seagrass Weight and Species Abundance:")
    correlations = calculate_correlations(df)
    print(correlations)
    
    # Create visualizations
    
    # 1. Seagrass weight distribution by category
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Category', y='Seagrass Wt (gms)', data=df)
    plt.title('Seagrass Weight Distribution by Habitat Category')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(data_dir / 'seagrass_weight_distribution.png')
    plt.close()
    
    # 2. Species abundance patterns
    plt.figure(figsize=(12, 6))
    abundance_by_category.plot(kind='bar', stacked=True)
    plt.title('Species Abundance by Habitat Category')
    plt.xlabel('Habitat Category')
    plt.ylabel('Total Abundance')
    plt.legend(title='Species', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(data_dir / 'species_abundance_by_category.png')
    plt.close()
    
    # 3. Correlation heatmap
    plt.figure(figsize=(12, 10))
    correlation_matrix = df[numeric_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='RdBu_r', center=0)
    plt.title('Correlation Matrix of Seagrass Weight and Species Abundance')
    plt.tight_layout()
    plt.savefig(data_dir / 'correlation_heatmap.png')
    plt.close()
    
    # 4. Species composition by category
    plt.figure(figsize=(12, 6))
    composition = abundance_by_category.div(abundance_by_category.sum(axis=1), axis=0) * 100
    composition.plot(kind='bar', stacked=True)
    plt.title('Species Composition by Habitat Category (%)')
    plt.xlabel('Habitat Category')
    plt.ylabel('Percentage')
    plt.legend(title='Species', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(data_dir / 'species_composition_percentage.png')
    plt.close()

def calculate_diversity_metrics(df, species_cols):
    """Calculate diversity metrics for each habitat category"""
    diversity_metrics = []
    
    for category in df['Category'].unique():
        category_data = df[df['Category'] == category][species_cols]
        
        # Calculate metrics
        richness = (category_data > 0).sum(axis=1).mean()  # Average number of species
        
        # Shannon diversity
        abundances = category_data.sum()
        total = abundances.sum()
        proportions = abundances[abundances > 0] / total
        shannon = -np.sum(proportions * np.log(proportions))
        
        # Simpson diversity
        simpson = 1 - np.sum((proportions) ** 2)
        
        # Evenness
        evenness = shannon / np.log(len(proportions)) if len(proportions) > 1 else 0
        
        diversity_metrics.append({
            'Category': category,
            'Species_Richness': richness,
            'Shannon_Diversity': shannon,
            'Simpson_Diversity': simpson,
            'Evenness': evenness
        })
    
    return pd.DataFrame(diversity_metrics).set_index('Category')

def calculate_correlations(df):
    """Calculate correlations between seagrass weight and species abundance"""
    # Get species columns
    species_cols = df.columns[3:]
    
    correlations = []
    seagrass_wt = df['Seagrass Wt (gms)']
    
    for species in species_cols:
        # Create a temporary dataframe with only the columns we need
        temp_df = pd.DataFrame({
            'Seagrass': seagrass_wt,
            'Species': df[species]
        }).dropna()  # Remove any rows with NaN values
        
        if len(temp_df) > 1:  # Only calculate if we have at least 2 points
            correlation = stats.spearmanr(
                temp_df['Seagrass'],
                temp_df['Species']
            )
            
            correlations.append({
                'Species': species,
                'Correlation': correlation.correlation,
                'P_value': correlation.pvalue,
                'Sample_Size': len(temp_df)
            })
    
    return pd.DataFrame(correlations).sort_values('Correlation', ascending=False)

if __name__ == "__main__":
    analyze_habitat_complexity()
