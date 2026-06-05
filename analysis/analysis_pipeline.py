#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from factor_analyzer import FactorAnalyzer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
import statsmodels.formula.api as smf


PARSER_OUTPUT = Path(__file__).resolve().parent / 'parsed_experiment_data.json'
RESULTS_DIR = Path(__file__).resolve().parent / 'analysis_results'
RESULTS_DIR.mkdir(exist_ok=True)

PRESTIGE_MAP = {
    'trabaja en el campo': 1,
    'trabaja en un bar/restaurante': 2,
    'trabaja en la construcción': 2,
    'trabaja en una tienda': 3,
    'es administrador/a': 4,
    'es maestro/a': 4,
    'es médico/a o abogado/a': 5,
}

AGE_MAP = {
    '< 30': 1,
    '30-39': 2,
    '40-49': 3,
    '50-59': 4,
    '≥ 60': 5,
}

ORIGIN_MAP = {
    'Huelva': 'Huelva',
    'Sevilla': 'Sevilla',
    'Otro lugar': 'Otro lugar',
    'otro lugar': 'Otro lugar',
}

GENDER_MAP = {
    'I': 'female',
    'Isa': 'female',
    'L': 'female',
    'M': 'male',
    'R': 'male',
    'V': 'male',
}

Q1_FIELDS = {
    'formality': 'q1_s1',
    'socioeconomic': 'q1_s2',
    'education': 'q1_s3',
    'masculinity': 'q1_s4',
    'friendliness': 'q1_s5',
    'urban': 'q1_s6',
    'naturalness': 'q1_s7',
}

CONTINUOUS_LABELS = [
    'formality',
    'socioeconomic',
    'education',
    'masculinity',
    'friendliness',
    'urban',
    'occupational_prestige',
    'age_scale',
]


def parse_speaker_from_audio(audio: Optional[str]) -> Optional[str]:
    if not audio:
        return None
    name = Path(audio).stem
    parts = name.split('-')
    if len(parts) >= 2:
        return '-'.join(parts[1:])
    return name


def speaker_gender_from_code(code: Optional[str]) -> Optional[str]:
    if code is None:
        return None
    return GENDER_MAP.get(code)


def build_dataframe(parsed_json: Dict) -> pd.DataFrame:
    records: List[Dict] = []
    for source_file, trials in parsed_json.get('files', {}).items():
        for trial in trials:
            if trial.get('task') != 'audio_questions':
                continue
            response = trial.get('response', {}) or {}
            if not response:
                continue
            row: Dict = {
                'source_file': source_file,
                'participant_id': trial.get('participant_id'),
                'trial_index': trial.get('trial_index'),
                'item_id': trial.get('item_id'),
                'condition': trial.get('condition'),
                'audio': trial.get('audio'),
                'variant': trial.get('condition'),
                'speaker': parse_speaker_from_audio(trial.get('audio')),
            }
            # q1 scales: handle both 7-scale (no attention check) and 8-scale (with attention check) formats
            # When attention check is present, s4 is the check itself, so s5-s8 map to the actual dimensions
            has_attention_check = trial.get('attention_check') is not None
            for label, key in Q1_FIELDS.items():
                if has_attention_check and label == 'masculinity':
                    # When attention check present, masculinity is at s5 instead of s4
                    value = response.get('q1_s5')
                elif has_attention_check and label in ('friendliness', 'urban', 'naturalness'):
                    # When attention check present, shift these fields up by one position
                    key_num = int(key.split('_s')[1])
                    new_key = f'q1_s{key_num + 1}'
                    value = response.get(new_key)
                else:
                    # Standard case: no attention check
                    value = response.get(key)
                row[label] = int(value) if value not in (None, '') else np.nan
            # derived measures
            row['occupational_prestige'] = PRESTIGE_MAP.get(response.get('q2'))
            row['age_scale'] = AGE_MAP.get(response.get('q3'))
            origin = response.get('q4')
            row['perceived_origin'] = ORIGIN_MAP.get(origin, origin)
            row['speaker_gender'] = speaker_gender_from_code(row['speaker'])
            row['condition_type'] = 'critical' if row['condition'] in ('ceceo', 'seseo') else 'other'
            records.append(row)
    df = pd.DataFrame.from_records(records)
    # normalize condition labels for modeling convenience
    df['variant'] = df['variant'].astype('category')
    df['perceived_origin'] = pd.Categorical(df['perceived_origin'], categories=['Huelva', 'Sevilla', 'Otro lugar'])
    return df


def center_scales(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for label in ['formality', 'socioeconomic', 'education', 'masculinity', 'friendliness', 'urban', 'naturalness']:
        if label in out:
            out[f'{label}_c'] = out[label] - 3.5
    for label in ['occupational_prestige', 'age_scale']:
        if label in out:
            out[f'{label}_c'] = out[label] - 3.0
    return out


def standardize_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    scaler = StandardScaler()
    scaled = scaler.fit_transform(df[columns].astype(float))
    scaled_df = pd.DataFrame(scaled, columns=[f'{col}_z' for col in columns], index=df.index)
    return pd.concat([df, scaled_df], axis=1)


def pca_summary(df: pd.DataFrame, columns: List[str], n_components: int = None):
    if n_components is None:
        n_components = len(columns)
    scaler = StandardScaler()
    X = scaler.fit_transform(df[columns].astype(float).dropna())
    pca = PCA(n_components=n_components)
    pca.fit(X)
    result = pd.DataFrame(
        np.column_stack((pca.explained_variance_, pca.explained_variance_ratio_)),
        columns=['eigenvalue', 'explained_variance_ratio'],
        index=[f'PC{i+1}' for i in range(pca.n_components_)]
    )
    result['cumulative_variance_ratio'] = result['explained_variance_ratio'].cumsum()
    loadings = pd.DataFrame(
        pca.components_.T,
        index=columns,
        columns=[f'PC{i+1}' for i in range(pca.n_components_)]
    )
    return result, pca, loadings


def factor_analysis(df: pd.DataFrame, columns: List[str], n_factors: int = 3) -> Dict:
    X = StandardScaler().fit_transform(df[columns].astype(float).dropna())
    fa = FactorAnalyzer(n_factors=n_factors, rotation='varimax')
    fa.fit(X)
    loadings = pd.DataFrame(fa.loadings_, index=columns, columns=[f'Factor{i+1}' for i in range(n_factors)])
    communalities = pd.Series(fa.get_communalities(), index=columns)
    return {
        'model': fa,
        'loadings': loadings,
        'communalities': communalities,
        'eigenvalues': pd.Series(fa.get_eigenvalues()[0], index=columns),
    }


def compute_status_composite(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    status_vars = ['socioeconomic_z', 'education_z', 'occupational_prestige_z']
    for col in status_vars:
        if col not in df.columns:
            raise KeyError(f'Missing standardized column: {col}')
    df['status_score'] = df[status_vars].mean(axis=1)
    return df


def fit_mixedlm(df: pd.DataFrame, outcome: str, formula: str, group_col: str, vc: Dict[str, str]):
    df = df.copy()
    try:
        # Random intercepts for participant and speaker, random slope of variant by participant
        model = smf.mixedlm(formula, df, groups=df[group_col], vc_formula=vc, re_formula='1 + variant_code')
        result = model.fit(reml=False, method='lbfgs')
        return result
    except (np.linalg.LinAlgError, ValueError) as first_error:
        try:
            # Fallback: keep random intercepts and slope structure but simplify variance components
            model = smf.mixedlm(formula, df, groups=df[group_col], vc_formula=vc, re_formula='1 + variant_code')
            result = model.fit(reml=False, method='lbfgs')
            return result
        except (np.linalg.LinAlgError, ValueError):
            # Last resort: OLS if mixed model fails entirely
            ols_result = smf.ols(formula, df).fit()
            return ols_result


def _formula_predictor_names(predictors: str) -> List[str]:
    tokens = predictors.replace('*', ' ').replace(':', ' ').replace('+', ' ').split()
    return sorted({t for t in tokens if t and t.isidentifier()})


def fit_multinomial_origin(df: pd.DataFrame, predictors: str):
    df2 = df.dropna(subset=['perceived_origin']).copy()
    df2 = df2[df2['perceived_origin'].isin(['Huelva', 'Sevilla', 'Otro lugar'])].copy()
    df2['perceived_origin'] = df2['perceived_origin'].astype('category')
    df2 = pd.get_dummies(df2, columns=['variant', 'speaker_gender'], drop_first=True)
    target = df2['perceived_origin'].cat.codes.astype(int)
    exog_cols = [c for c in df2.columns if c.startswith('variant_') or c.startswith('speaker_gender_')]
    exog = df2[exog_cols].astype(float)
    exog = exog.loc[:, exog.std(axis=0) > 0.0]
    model = sm.MNLogit(target, exog)
    result = model.fit(method='newton', maxiter=100, disp=False)
    return result


def main() -> None:
    parsed = json.loads(PARSER_OUTPUT.read_text(encoding='utf-8'))
    df = build_dataframe(parsed)
    df = center_scales(df)
    df = standardize_columns(df, [
        'formality', 'socioeconomic', 'education', 'masculinity',
        'friendliness', 'urban', 'occupational_prestige', 'age_scale',
    ])
    df = compute_status_composite(df)

    print('Data summary:')
    print(df[['variant', 'speaker_gender', 'perceived_origin']].describe(include='all'))
    print(f'Total trials processed: {len(df)}')

    critical = df[df['condition_type'] == 'critical'].dropna(subset=CONTINUOUS_LABELS)
    print(f'Critical trials used for PCA/FA: {len(critical)}')

    print('\nInitial PCA on eight continuous measures:')
    pca8_summary, pca8, pca8_loadings = pca_summary(critical, ['formality', 'socioeconomic', 'education', 'masculinity', 'friendliness', 'urban', 'occupational_prestige', 'age_scale'])
    print(pca8_summary)
    print('\nPCA loadings for eight measures:')
    print(pca8_loadings)
    pca8_summary.to_csv(RESULTS_DIR / 'pca_8measures_summary.csv')
    pca8_loadings_export = pd.concat([
        pca8_loadings,
        pd.DataFrame(
            [pca8_summary['explained_variance_ratio'].values, pca8_summary['cumulative_variance_ratio'].values],
            index=['explained_variance_ratio', 'cumulative_variance_ratio'],
            columns=pca8_summary.index,
        ),
    ])
    pca8_loadings_export.to_csv(RESULTS_DIR / 'pca_8measures_loadings.csv')

    print('\nInitial Factor Analysis on eight continuous measures:')
    fa8 = factor_analysis(critical, ['formality', 'socioeconomic', 'education', 'masculinity', 'friendliness', 'urban', 'occupational_prestige', 'age_scale'], n_factors=3)
    print(fa8['loadings'])
    print('\nCommunalities:')
    print(fa8['communalities'])
    fa8['loadings'].to_csv(RESULTS_DIR / 'fa_8measures_loadings.csv')
    fa8['communalities'].to_csv(RESULTS_DIR / 'fa_8measures_communalities.csv')

    reduced = critical.dropna(subset=['formality', 'socioeconomic', 'education', 'masculinity', 'urban', 'occupational_prestige'])
    print('\nReduced PCA on the six retained measures:')
    pca6_summary, pca6, pca6_loadings = pca_summary(reduced, ['formality', 'socioeconomic', 'education', 'masculinity', 'urban', 'occupational_prestige'])
    print(pca6_summary)
    print('\nPCA loadings for six measures:')
    print(pca6_loadings)
    pca6_summary.to_csv(RESULTS_DIR / 'pca_6measures_summary.csv')
    pca6_loadings_export = pd.concat([
        pca6_loadings,
        pd.DataFrame(
            [pca6_summary['explained_variance_ratio'].values, pca6_summary['cumulative_variance_ratio'].values],
            index=['explained_variance_ratio', 'cumulative_variance_ratio'],
            columns=pca6_summary.index,
        ),
    ])
    pca6_loadings_export.to_csv(RESULTS_DIR / 'pca_6measures_loadings.csv')

    print('\nReduced Factor Analysis on the six retained measures:')
    fa6 = factor_analysis(reduced, ['formality', 'socioeconomic', 'education', 'masculinity', 'urban', 'occupational_prestige'], n_factors=3)
    print(fa6['loadings'])
    print('\nCommunalities:')
    print(fa6['communalities'])
    fa6['loadings'].to_csv(RESULTS_DIR / 'fa_6measures_loadings.csv')
    fa6['communalities'].to_csv(RESULTS_DIR / 'fa_6measures_communalities.csv')

    modeling_df = df[df['condition_type'] == 'critical'].copy()
    modeling_df['variant'] = modeling_df['variant'].cat.remove_unused_categories()
    modeling_df['speaker_gender'] = modeling_df['speaker_gender'].astype('category')
    modeling_df['variant_code'] = modeling_df['variant'].map({'ceceo': 0, 'seseo': 1})

    for outcome in ['status_score', 'urban_z', 'formality_z']:
        model_df = modeling_df.dropna(subset=[outcome, 'variant_code', 'speaker_gender'])
        if len(model_df) < 1:
            continue
        print(f'\nMixed effects model for {outcome}:')
        formula = f'{outcome} ~ variant * speaker_gender'
        try:
            result = fit_mixedlm(model_df, outcome, formula, 'participant_id', {'speaker': '0 + C(speaker)'})
            print(result.summary())
            with open(RESULTS_DIR / f'mixedlm_{outcome}.txt', 'w', encoding='utf-8') as fh:
                fh.write(str(result.summary()))
        except Exception as exc:
            print(f'Failed to fit mixed model for {outcome}: {exc}')

    print('\nMultinomial logistic regression for perceived origin:')
    origin_df = df.dropna(subset=['perceived_origin', 'variant', 'speaker_gender'])
    try:
        origin_df = origin_df[origin_df['perceived_origin'].isin(['Huelva', 'Sevilla', 'Otro lugar'])]
        origin_df['variant_code'] = origin_df['variant'].map({'ceceo': 0, 'seseo': 1, 'control': 2})
        origin_model = fit_multinomial_origin(origin_df, 'variant + speaker_gender')
        print(origin_model.summary())
        with open(RESULTS_DIR / 'multinomial_origin_summary.txt', 'w', encoding='utf-8') as fh:
            fh.write(str(origin_model.summary()))
    except Exception as exc:
        print(f'Failed to fit multinomial origin model: {exc}')

    df.to_csv(RESULTS_DIR / 'analysis_dataframe.csv', index=False)
    plot_gender_interaction_boxplots(df, RESULTS_DIR)
    print(f'Analysis artifacts written to {RESULTS_DIR}')


def plot_gender_interaction_boxplots(df: pd.DataFrame, output_dir: Path) -> None:
    subset = df[df['condition'].isin(['ceceo', 'seseo'])].copy()
    subset = subset.dropna(subset=['speaker_gender', 'formality', 'urban', 'status_score'])
    if subset.empty:
        print('No ceceo/seseo data available for gender-variant interaction boxplots.')
        return

    measures = [
        ('formality', 'Perceived Formality'),
        ('urban', 'Perceived Urbanness'),
        ('status_score', 'Perceived Status Score'),
    ]
    genders = sorted(subset['speaker_gender'].dropna().unique())
    variants = ['ceceo', 'seseo']
    n_groups = len(genders)
    n_variants = len(variants)
    width = 0.35
    positions = np.arange(n_groups)

    fig, axes = plt.subplots(1, len(measures), figsize=(18, 5), sharey=False)
    if len(measures) == 1:
        axes = [axes]

    for ax, (col, title) in zip(axes, measures):
        for i, variant in enumerate(variants):
            offset = (i - 0.5) * width
            variant_data = [
                subset.loc[(subset['speaker_gender'] == gender) & (subset['variant'] == variant), col].dropna().values
                for gender in genders
            ]
            if any(len(values) > 0 for values in variant_data):
                box = ax.boxplot(
                    variant_data,
                    positions=positions + offset,
                    widths=width,
                    patch_artist=True,
                    boxprops=dict(facecolor='#1f77b4' if variant == 'ceceo' else '#ff7f0e', color='black'),
                    medianprops=dict(color='black'),
                    labels=[''] * n_groups,
                )
                for patch in box['boxes']:
                    patch.set_alpha(0.7)

            for j, gender in enumerate(genders):
                values = subset.loc[(subset['speaker_gender'] == gender) & (subset['variant'] == variant), col].dropna().values
                if values.size > 0:
                    x = np.full_like(values, positions[j] + offset, dtype=float)
                    x += np.random.normal(scale=width / 6, size=values.shape)
                    ax.scatter(x, values, alpha=0.6, s=20,
                               color='#1f77b4' if variant == 'ceceo' else '#ff7f0e',
                               edgecolor='black', linewidth=0.3)
        ax.set_title(title)
        ax.set_xlabel('Speaker gender')
        ax.set_xticks(positions)
        ax.set_xticklabels(genders)
        ax.set_ylabel(title)
        ax.legend([Line2D([0], [0], color='#1f77b4', lw=10), Line2D([0], [0], color='#ff7f0e', lw=10)], variants, title='Variant')

    fig.tight_layout()
    out_path = output_dir / 'gender_variant_formality_urban_status_boxplots.png'
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f'Gender-variant interaction boxplots saved to {out_path}')


if __name__ == '__main__':
    main()
