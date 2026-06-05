"""
Power analysis for Spanish merger matched-guise experiment.
Assesses whether N=50 participants provides adequate power (0.80).
"""

import json
import numpy as np
import pandas as pd
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

PARSER_OUTPUT = 'analysis/parsed_experiment_data.json'
RESULTS_DIR = 'analysis/analysis_results/'


def load_analysis_dataframe():
    """Load the processed analysis dataframe."""
    df = pd.read_csv(f'{RESULTS_DIR}analysis_dataframe.csv')
    return df


def calculate_cohens_d(group1, group2):
    """Calculate Cohen's d effect size between two groups."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    d = (np.mean(group1) - np.mean(group2)) / pooled_sd
    return d


def calculate_paired_cohens_d(paired_diff):
    """Calculate Cohen's d for paired samples from differences."""
    d = np.mean(paired_diff) / np.std(paired_diff, ddof=1)
    return d


def extract_effect_sizes(df):
    """Extract effect sizes for main outcomes from the data."""
    effects = {}
    
    # Filter to critical trials only (exclude control and filler)
    df_critical = df[df['condition'].isin(['ceceo', 'seseo'])].copy()
    
    for outcome in ['formality_z', 'urban_z', 'status_score']:
        # Variant effect: ceceo vs seseo
        ceceo_data = df_critical[df_critical['variant'] == 'ceceo'][outcome].dropna()
        seseo_data = df_critical[df_critical['variant'] == 'seseo'][outcome].dropna()
        
        if len(ceceo_data) > 0 and len(seseo_data) > 0:
            variant_d = calculate_cohens_d(seseo_data, ceceo_data)
            effects[f'{outcome}_variant'] = {
                'cohen_d': variant_d,
                'seseo_mean': seseo_data.mean(),
                'ceceo_mean': ceceo_data.mean(),
                'n_seseo': len(seseo_data),
                'n_ceceo': len(ceceo_data)
            }
        
        # Gender effect: female vs male speakers
        female_data = df_critical[df_critical['speaker_gender'] == 'female'][outcome].dropna()
        male_data = df_critical[df_critical['speaker_gender'] == 'male'][outcome].dropna()
        
        if len(female_data) > 0 and len(male_data) > 0:
            gender_d = calculate_cohens_d(male_data, female_data)
            effects[f'{outcome}_gender'] = {
                'cohen_d': gender_d,
                'male_mean': male_data.mean(),
                'female_mean': female_data.mean(),
                'n_male': len(male_data),
                'n_female': len(female_data)
            }
    
    return effects


def power_for_independent_samples(d, n1, n2=None, alpha=0.05):
    """
    Estimate power for independent samples t-test given effect size and N.
    Uses approximate method based on non-centrality parameter.
    """
    if n2 is None:
        n2 = n1
    
    # Non-centrality parameter
    nc = d * np.sqrt((n1 * n2) / (2 * (n1 + n2)))
    
    # Degrees of freedom
    df = n1 + n2 - 2
    
    # Critical t-value (two-tailed)
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    
    # Power is P(|t| > t_crit) under the alternative hypothesis
    power = 1 - stats.nct.cdf(t_crit, df, nc) + stats.nct.cdf(-t_crit, df, nc)
    
    return power


def required_sample_size_per_group(d, target_power=0.80, alpha=0.05):
    """
    Estimate sample size per group needed to achieve target power.
    Uses iterative search.
    """
    for n in range(10, 5000):
        power = power_for_independent_samples(d, n, n, alpha)
        if power >= target_power:
            return n
    return None


def conduct_power_analysis(effects):
    """Conduct comprehensive power analysis."""
    results = []
    
    for effect_name, effect_data in effects.items():
        d = effect_data['cohen_d']
        
        # Current study: estimate effective N (accounting for repeated measures)
        # Rough approximation: effective N ≈ N_participants * (ICC effect)
        # Using conservative estimate
        current_n = 50
        
        # Power with current design
        power_current = power_for_independent_samples(d, current_n)
        
        # Sample size for 80% power
        n_for_80 = required_sample_size_per_group(d, 0.80)
        
        # Sample size for 90% power
        n_for_90 = required_sample_size_per_group(d, 0.90)
        
        effect_interpretation = {
            0.2: 'small',
            0.5: 'medium',
            0.8: 'large'
        }
        
        def get_effect_size_label(d):
            d_abs = abs(d)
            if d_abs < 0.2:
                return 'negligible'
            elif d_abs < 0.5:
                return 'small'
            elif d_abs < 0.8:
                return 'medium'
            else:
                return 'large'
        
        results.append({
            'effect': effect_name,
            'cohens_d': d,
            'effect_size_label': get_effect_size_label(d),
            'power_current_n50': power_current,
            'n_for_80pct_power': n_for_80,
            'n_for_90pct_power': n_for_90,
            **effect_data
        })
    
    return results


def format_power_report(results):
    """Format power analysis results for display."""
    report = []
    report.append("=" * 90)
    report.append("POWER ANALYSIS FOR SPANISH MERGER MATCHED-GUISE EXPERIMENT")
    report.append("=" * 90)
    report.append(f"\nCurrent Study Design: N = 50 participants")
    report.append(f"Design: Repeated measures mixed effects model")
    report.append(f"  - Random intercepts: participant + speaker")
    report.append(f"  - Random slopes: variant by participant")
    report.append(f"  - Fixed effects: variant × speaker_gender interaction\n")
    
    # Summary table
    report.append("\n" + "-" * 90)
    report.append("POWER SUMMARY")
    report.append("-" * 90)
    cohens_d_label = "Cohen's d"
    report.append(f"{'Effect':<35} {cohens_d_label:<12} {'Effect Size':<12} {'Power @ N=50':<15}")
    report.append("-" * 90)
    
    for result in results:
        report.append(
            f"{result['effect']:<35} {result['cohens_d']:>10.3f}  "
            f"{result['effect_size_label']:<12} {result['power_current_n50']:>12.1%}"
        )
    
    # Detailed results
    report.append("\n" + "-" * 90)
    report.append("DETAILED RESULTS")
    report.append("-" * 90)
    
    for result in results:
        report.append(f"\n{result['effect']}:")
        report.append(f"  Cohen's d: {result['cohens_d']:.3f} ({result['effect_size_label']} effect)")
        report.append(f"  Current power (N=50): {result['power_current_n50']:.1%}")
        report.append(f"  Sample size needed for 80% power: {result['n_for_80pct_power']} per group")
        report.append(f"  Sample size needed for 90% power: {result['n_for_90pct_power']} per group")
        
        if result['power_current_n50'] >= 0.80:
            report.append(f"  ✓ Study is ADEQUATELY POWERED for this effect")
        elif result['power_current_n50'] >= 0.70:
            report.append(f"  ⚠ Study has MARGINAL power; some risk of Type II error")
        else:
            report.append(f"  ✗ Study is UNDERPOWERED; high risk of Type II error")
    
    # Overall summary
    report.append("\n" + "=" * 90)
    report.append("OVERALL ASSESSMENT")
    report.append("=" * 90)
    
    adequately_powered = sum(1 for r in results if r['power_current_n50'] >= 0.80)
    total_effects = len(results)
    
    report.append(f"\n{adequately_powered} of {total_effects} effects have ≥80% power at N=50")
    
    # Recommendations
    report.append("\n" + "-" * 90)
    report.append("RECOMMENDATIONS")
    report.append("-" * 90)
    
    underpowered = [r for r in results if r['power_current_n50'] < 0.80]
    
    if not underpowered:
        report.append(
            "\n✓ Your study appears well-powered with N=50 participants for all effects."
        )
    else:
        report.append(f"\n✗ {len(underpowered)} effect(s) are underpowered (< 80%):\n")
        for result in underpowered:
            report.append(
                f"  • {result['effect']}: Currently {result['power_current_n50']:.1%} power, "
                f"need N≈{result['n_for_80pct_power']} for 80% power"
            )
        
        # Calculate average N needed
        n_values = [r['n_for_80pct_power'] for r in underpowered if r['n_for_80pct_power'] is not None]
        if n_values:
            avg_n_needed = np.mean(n_values)
            report.append(
                f"\n  → Consider increasing to N≈{int(np.ceil(avg_n_needed))} participants "
                f"for adequate power across all effects"
            )
    
    report.append("\nNote: This analysis is approximate and based on independent samples t-tests.")
    report.append("Actual power in your mixed effects model may differ due to:")
    report.append("  - Repeated measures structure")
    report.append("  - Intraclass correlations (ICC) between observations")
    report.append("  - Random effects components")
    report.append("  - Design imbalance")
    
    report.append("\n" + "=" * 90)
    
    return "\n".join(report)


def main():
    print("Loading analysis data...")
    df = load_analysis_dataframe()
    
    print("Calculating effect sizes from current data...")
    effects = extract_effect_sizes(df)
    
    print("Conducting power analysis...")
    results = conduct_power_analysis(effects)
    
    # Format and display report
    report = format_power_report(results)
    print(report)
    
    # Save report
    output_file = f'{RESULTS_DIR}power_analysis_report.txt'
    with open(output_file, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {output_file}")
    
    # Save detailed results as CSV
    results_df = pd.DataFrame([
        {
            'effect': r['effect'],
            'cohens_d': r['cohens_d'],
            'effect_size_label': r['effect_size_label'],
            'power_at_n50': r['power_current_n50'],
            'n_for_80pct_power': r['n_for_80pct_power'],
            'n_for_90pct_power': r['n_for_90pct_power']
        }
        for r in results
    ])
    
    csv_output = f'{RESULTS_DIR}power_analysis_summary.csv'
    results_df.to_csv(csv_output, index=False)
    print(f"Summary CSV saved to: {csv_output}")


if __name__ == '__main__':
    main()
