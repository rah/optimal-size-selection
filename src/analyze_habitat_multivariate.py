import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import chi2_contingency
from statsmodels.stats.multitest import multipletests

def analyze_habitat_multivariate():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    
    # Read and clean the data
    df = pd.read_csv(data_dir / 'Benthos-Habitat-Complexity-25-26-6-83.csv')
    df = df.replace('#N/A', np.nan)
    
    # Convert numeric columns to float
    numeric_cols = df.columns[2:]  # All columns after Category
    df[numeric_cols] = df[numeric_cols].astype(float)
    
    # 1. Multivariate Analysis
    print("\n1. Principal Component Analysis of Species Composition:")
    pca_results = perform_pca(df)
    print(pca_results)
    
    # 2. Species Association Analysis
    print("\n2. Species Association Patterns:")
    associations = analyze_species_associations(df)
    print("\nSignificant Species Associations (p < 0.05):")
    print(associations[associations['Adjusted_P_value'] < 0.05])
    
    # 3. Habitat Preference Analysis
    print("\n3. Habitat Preference Analysis:")
    preferences = analyze_habitat_preferences(df)
    print(preferences)
    
    # 4. Community Similarity Analysis
    print("\n4. Community Similarity Between Habitat Categories:")
    similarities = analyze_community_similarity(df)
    print(similarities)
    
    # Create visualizations
    
    # 1. PCA Biplot
    plt.figure(figsize=(12, 8))
    plot_pca_biplot(df, pca_results)
    plt.savefig(data_dir / 'pca_biplot.png')
    plt.close()
    
    # 2. Species Network
    plt.figure(figsize=(12, 8))
    plot_species_network(associations)
    plt.savefig(data_dir / 'species_network.png')
    plt.close()
    
    # 3. Habitat Preference Heatmap
    plt.figure(figsize=(12, 8))
    plot_habitat_preferences(preferences)
    plt.savefig(data_dir / 'habitat_preferences.png')
    plt.close()
    
    # 4. NMDS Ordination
    plt.figure(figsize=(10, 8))
    plot_nmds_ordination(df)
    plt.savefig(data_dir / 'nmds_ordination.png')
    plt.close()

def perform_pca(df):
    """Perform PCA on species composition data"""
    species_cols = df.columns[3:]  # All columns after Seagrass Wt
    
    # Prepare data for PCA
    X = df[species_cols].fillna(0)
    X_scaled = StandardScaler().fit_transform(X)
    
    # Perform PCA
    pca = PCA()
    pca_result = pca.fit_transform(X_scaled)
    
    # Calculate explained variance
    explained_var = pca.explained_variance_ratio_
    
    # Create loadings dataframe
    loadings = pd.DataFrame(
        pca.components_.T,
        columns=[f'PC{i+1}' for i in range(len(pca.components_))],
        index=species_cols
    )
    
    return {
        'explained_variance': explained_var,
        'loadings': loadings,
        'transformed_data': pca_result
    }

def analyze_species_associations(df):
    """Analyze pairwise species associations using chi-square tests"""
    species_cols = df.columns[3:]
    associations = []
    
    for i, sp1 in enumerate(species_cols):
        for j, sp2 in enumerate(species_cols[i+1:], i+1):
            # Create contingency table
            presence_data = pd.DataFrame({
                'sp1': df[sp1] > 0,
                'sp2': df[sp2] > 0
            }).dropna()
            
            if len(presence_data) > 0:
                contingency = pd.crosstab(presence_data['sp1'], presence_data['sp2'])
                
                if contingency.shape == (2, 2):  # Only perform test if we have 2x2 table
                    chi2, p_value, _, _ = chi2_contingency(contingency)
                    
                    associations.append({
                        'Species1': sp1,
                        'Species2': sp2,
                        'Chi2': chi2,
                        'P_value': p_value
                    })
    
    # Convert to dataframe and adjust p-values
    assoc_df = pd.DataFrame(associations)
    if len(assoc_df) > 0:
        reject, pvals_corrected, _, _ = multipletests(assoc_df['P_value'], method='fdr_bh')
        assoc_df['Adjusted_P_value'] = pvals_corrected
    
    return assoc_df.sort_values('Adjusted_P_value')

def analyze_habitat_preferences(df):
    """Analyze species habitat preferences using indicator value analysis"""
    species_cols = df.columns[3:]
    preferences = []
    
    for species in species_cols:
        # Calculate mean abundance in each habitat
        mean_abundance = df.groupby('Category')[species].mean()
        
        # Calculate frequency of occurrence
        frequency = df.groupby('Category')[species].apply(lambda x: (x > 0).mean())
        
        # Calculate indicator value (product of relative abundance and relative frequency)
        indicator_value = mean_abundance * frequency
        
        preferences.append({
            'Species': species,
            'Preferred_Habitat': indicator_value.idxmax(),
            'Indicator_Value': indicator_value.max(),
            'Mean_Abundance': mean_abundance[indicator_value.idxmax()],
            'Frequency': frequency[indicator_value.idxmax()]
        })
    
    return pd.DataFrame(preferences).sort_values('Indicator_Value', ascending=False)

def analyze_community_similarity(df):
    """Calculate community similarity between habitat categories using Bray-Curtis dissimilarity"""
    species_cols = df.columns[3:]
    
    # Calculate mean abundance per habitat
    habitat_means = df.groupby('Category')[species_cols].mean()
    
    # Calculate Bray-Curtis dissimilarity
    def bray_curtis(x, y):
        return np.sum(np.abs(x - y)) / np.sum(x + y)
    
    similarity_matrix = pd.DataFrame(
        index=habitat_means.index,
        columns=habitat_means.index
    )
    
    for h1 in habitat_means.index:
        for h2 in habitat_means.index:
            similarity_matrix.loc[h1, h2] = 1 - bray_curtis(
                habitat_means.loc[h1],
                habitat_means.loc[h2]
            )
    
    return similarity_matrix

def plot_pca_biplot(df, pca_results):
    """Create a biplot of PCA results"""
    # Plot sample points
    plt.scatter(
        pca_results['transformed_data'][:, 0],
        pca_results['transformed_data'][:, 1],
        c=pd.Categorical(df['Category']).codes,
        alpha=0.6
    )
    
    # Plot feature vectors
    loadings = pca_results['loadings']
    for i, species in enumerate(loadings.index):
        plt.arrow(
            0, 0,
            loadings.iloc[i, 0] * 5,
            loadings.iloc[i, 1] * 5,
            color='r',
            alpha=0.5
        )
        plt.text(
            loadings.iloc[i, 0] * 5.2,
            loadings.iloc[i, 1] * 5.2,
            species,
            color='r',
            alpha=0.7
        )
    
    plt.xlabel(f"PC1 ({pca_results['explained_variance'][0]:.2%} explained var.)")
    plt.ylabel(f"PC2 ({pca_results['explained_variance'][1]:.2%} explained var.)")
    plt.title('PCA Biplot of Species Composition')
    plt.legend(df['Category'].unique())

def plot_species_network(associations):
    """Plot network of significant species associations"""
    significant = associations[associations['Adjusted_P_value'] < 0.05]
    
    if len(significant) > 0:
        # Create adjacency matrix
        species = pd.unique(significant[['Species1', 'Species2']].values.ravel())
        adj_matrix = pd.DataFrame(0, index=species, columns=species)
        
        for _, row in significant.iterrows():
            adj_matrix.loc[row['Species1'], row['Species2']] = 1
            adj_matrix.loc[row['Species2'], row['Species1']] = 1
        
        # Plot using seaborn
        sns.heatmap(adj_matrix, cmap='YlOrRd', square=True)
        plt.title('Significant Species Associations')
    else:
        plt.text(0.5, 0.5, 'No significant associations found',
                ha='center', va='center')

def plot_habitat_preferences(preferences):
    """Plot heatmap of species habitat preferences"""
    pivot_data = preferences.pivot(
        index='Species',
        columns='Preferred_Habitat',
        values='Indicator_Value'
    ).fillna(0)
    
    sns.heatmap(pivot_data, cmap='YlOrRd')
    plt.title('Species Habitat Preferences')
    plt.ylabel('Species')
    plt.xlabel('Habitat Category')

def plot_nmds_ordination(df):
    """Create NMDS ordination plot"""
    from sklearn.manifold import MDS
    
    # Prepare species data
    species_data = df.iloc[:, 3:].fillna(0)
    
    # Calculate distance matrix
    dist_matrix = pdist(species_data, metric='braycurtis')
    dist_matrix_square = squareform(dist_matrix)
    
    # Perform NMDS
    nmds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    nmds_coords = nmds.fit_transform(dist_matrix_square)
    
    # Plot
    plt.scatter(
        nmds_coords[:, 0],
        nmds_coords[:, 1],
        c=pd.Categorical(df['Category']).codes,
        alpha=0.6
    )
    plt.title('NMDS Ordination of Communities')
    plt.xlabel('NMDS1')
    plt.ylabel('NMDS2')
    plt.legend(df['Category'].unique())

if __name__ == "__main__":
    analyze_habitat_multivariate()
