"""
Visualize power curves for Spanish merger experiment.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

RESULTS_DIR = 'analysis/analysis_results/'


def power_for_independent_samples(d, n1, n2=None, alpha=0.05):
    """
    Estimate power for independent samples t-test given effect size and N.
    """
    if n2 is None:
        n2 = n1
    
    # Non-centrality parameter
    nc = d * np.sqrt((n1 * n2) / (2 * (n1 + n2)))
    
    # Degrees of freedom
    df = n1 + n2 - 2
    
    # Critical t-value (two-tailed)
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    
    # Power
    power = 1 - stats.nct.cdf(t_crit, df, nc) + stats.nct.cdf(-t_crit, df, nc)
    
    return power


def create_power_curves():
    """Create power curve visualization."""
    # Load summary data
    summary_df = pd.read_csv(f'{RESULTS_DIR}power_analysis_summary.csv')
    
    # Create figure with single plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Select top 3 effects by Cohen's d (excluding negligible effects)
    top_effects = summary_df[summary_df['cohens_d'].abs() > 0.15].nlargest(3, 'cohens_d')
    
    sample_sizes = np.arange(10, 501, 10)
    
    colors_curves = ['#e41a1c', '#377eb8', '#4daf4a']
    
    for idx, (_, effect_row) in enumerate(top_effects.iterrows()):
        d = effect_row['cohens_d']
        effect_name = effect_row['effect'].replace('_', ' ').title()
        
        powers_curve = [power_for_independent_samples(d, n) for n in sample_sizes]
        
        ax.plot(sample_sizes, powers_curve, linewidth=2.5, label=effect_name, 
                color=colors_curves[idx], marker='o', markersize=5, alpha=0.8)
    
    ax.axhline(y=0.80, color='black', linestyle='--', linewidth=2, label='80% Power Target')
    ax.axhline(y=0.90, color='black', linestyle=':', linewidth=1.5, alpha=0.6, label='90% Power Target')
    ax.axvline(x=50, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Current N=50')
    
    ax.set_xlabel('Sample Size (N per group)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Power', fontsize=12, fontweight='bold')
    ax.set_title('Power Analysis: Spanish Merger Experiment', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='lower right', fontsize=11, framealpha=0.95)
    
    plt.tight_layout()
    
    # Save figure
    output_file = f'{RESULTS_DIR}power_analysis_figure.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_file}")
    plt.close()


if __name__ == '__main__':
    create_power_curves()
