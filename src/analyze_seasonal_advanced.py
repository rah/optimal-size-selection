import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist, squareform

def analyze_seasonal_patterns_advanced():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    
    # Read the CSV file
    df = pd.read_csv(data_dir / 'Seasonal_Variation.csv')
    
    # 1. Species Co-occurrence Analysis
    print("\n1. Species Co-occurrence Analysis:")
    species_cols = df.columns[1:]  # All columns except MONTH
    cooccurrence = calculate_cooccurrence(df[species_cols])
    print("\nTop 5 Strongest Positive Associations:")
    print(get_top_associations(cooccurrence, n=5, positive=True))
    print("\nTop 5 Negative Associations:")
    print(get_top_associations(cooccurrence, n=5, positive=False))
    
    # 2. Temporal Stability Analysis
    print("\n2. Temporal Stability Analysis:")
    stability_metrics = calculate_temporal_stability(df)
    print(stability_metrics)
    
    # 3. Dominance Patterns
    print("\n3. Dominance Analysis:")
    dominance_metrics = analyze_dominance(df)
    print(dominance_metrics)
    
    # 4. Beta Diversity Analysis
    print("\n4. Beta Diversity Between Months:")
    beta_diversity = calculate_beta_diversity(df)
    print(beta_diversity)
    
    # Visualizations
    
    # 1. Species Co-occurrence Heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(cooccurrence, cmap='RdBu_r', center=0, 
                xticklabels=species_cols, yticklabels=species_cols)
    plt.title('Species Co-occurrence Patterns')
    plt.tight_layout()
    plt.savefig(data_dir / 'species_cooccurrence.png')
    plt.close()
    
    # 2. Species Accumulation Curve
    plt.figure(figsize=(10, 6))
    plot_species_accumulation(df[species_cols])
    plt.savefig(data_dir / 'species_accumulation.png')
    plt.close()
    
    # 3. Hierarchical Clustering of Species
    plt.figure(figsize=(12, 8))
    plot_species_clustering(df[species_cols])
    plt.savefig(data_dir / 'species_clustering.png')
    plt.close()
    
    # 4. Rank-Abundance Curves by Month
    plt.figure(figsize=(12, 6))
    plot_rank_abundance(df)
    plt.savefig(data_dir / 'rank_abundance.png')
    plt.close()

def calculate_cooccurrence(df):
    """Calculate species co-occurrence using Spearman correlation"""
    return df.corr(method='spearman')

def get_top_associations(corr_matrix, n=5, positive=True):
    """Get top n positive or negative associations between species"""
    # Convert correlation matrix to long format
    corr_long = corr_matrix.unstack()
    # Remove self-correlations and duplicates
    corr_long = corr_long[corr_long.index.get_level_values(0) != corr_long.index.get_level_values(1)]
    corr_long = corr_long.sort_values(ascending=not positive)
    return corr_long.head(n)

def calculate_temporal_stability(df):
    """Calculate temporal stability metrics"""
    monthly_totals = df.groupby('MONTH').sum()
    
    # Calculate CV (Coefficient of Variation) for each species
    cv = monthly_totals.std() / monthly_totals.mean()
    
    # Calculate community stability
    community_cv = monthly_totals.sum(axis=1).std() / monthly_totals.sum(axis=1).mean()
    
    return pd.Series({
        'Community_Stability': 1/community_cv,
        'Most_Stable_Species': cv.idxmin(),
        'Most_Variable_Species': cv.idxmax(),
        'Average_Species_CV': cv.mean()
    })

def analyze_dominance(df):
    """Analyze species dominance patterns"""
    monthly_totals = df.groupby('MONTH').sum()
    
    # Calculate Berger-Parker dominance index for each month
    berger_parker = monthly_totals.max(axis=1) / monthly_totals.sum(axis=1)
    
    # Calculate proportion of total abundance represented by top 3 species
    top_3_dominance = monthly_totals.apply(lambda x: x.nlargest(3).sum() / x.sum(), axis=1)
    
    return pd.DataFrame({
        'Berger_Parker_Dominance': berger_parker,
        'Top_3_Species_Dominance': top_3_dominance
    })

def calculate_beta_diversity(df):
    """Calculate Bray-Curtis dissimilarity between months"""
    monthly_totals = df.groupby('MONTH').sum()
    
    def bray_curtis(x, y):
        return np.sum(np.abs(x - y)) / np.sum(x + y)
    
    beta_div = pd.DataFrame(index=monthly_totals.index, columns=monthly_totals.index)
    for m1 in monthly_totals.index:
        for m2 in monthly_totals.index:
            beta_div.loc[m1, m2] = bray_curtis(monthly_totals.loc[m1], monthly_totals.loc[m2])
    
    return beta_div

def plot_species_accumulation(df):
    """Plot species accumulation curve"""
    n_samples = len(df)
    accumulation = []
    
    for i in range(1, n_samples + 1):
        # Randomly sample i rows and count unique species
        n_species = np.mean([
            len(df.iloc[np.random.choice(n_samples, i, replace=False)].astype(bool).sum(axis=1))
            for _ in range(10)  # 10 random permutations
        ])
        accumulation.append(n_species)
    
    plt.plot(range(1, n_samples + 1), accumulation)
    plt.xlabel('Number of Samples')
    plt.ylabel('Number of Species')
    plt.title('Species Accumulation Curve')

def plot_species_clustering(df):
    """Plot hierarchical clustering of species based on co-occurrence"""
    # Calculate distance matrix using correlation
    # Replace NaN values with 0 to handle species with no occurrences
    df_clean = df.fillna(0)
    dist_matrix = pdist(df_clean.T, metric='correlation')
    
    # Replace infinite values with maximum finite value
    dist_matrix[~np.isfinite(dist_matrix)] = np.nanmax(dist_matrix[np.isfinite(dist_matrix)])
    
    # Perform hierarchical clustering
    linkage_matrix = hierarchy.linkage(dist_matrix, method='average')
    # Plot dendrogram
    hierarchy.dendrogram(linkage_matrix, labels=df.columns, leaf_rotation=90)
    plt.title('Hierarchical Clustering of Species')
    plt.ylabel('Distance')

def plot_rank_abundance(df):
    """Plot rank-abundance curves for each month"""
    monthly_totals = df.groupby('MONTH').sum()
    
    for month in monthly_totals.index:
        abundances = sorted(monthly_totals.loc[month][monthly_totals.loc[month] > 0], reverse=True)
        ranks = range(1, len(abundances) + 1)
        plt.plot(ranks, np.log10(abundances), 'o-', label=month)
    
    plt.xlabel('Rank')
    plt.ylabel('Log10 Abundance')
    plt.title('Rank-Abundance Curves by Month')
    plt.legend()

if __name__ == "__main__":
    analyze_seasonal_patterns_advanced()
