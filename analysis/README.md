The `analysis` subdirectory contains notebooks and scripts for analyzing data. 

For new projects, plain-text [quarto](https://quarto.org/) notebooks are recommended.

Every figure and statistic in the published paper should be reproducible from these notebooks. 

e.g. 

``` 
experiment1.qmd
experiment2.qmd
experiment3.qmd
```
A new data extraction helper is available for the jsPsych CSV output from `experiments/experiment.js`:

```bash
python3 analysis/parse_experiment_data.py data/pilotC
```

This script:
- parses the raw jsPsych CSV files
- maps survey responses to the original question IDs and prompts
- extracts attention-check responses from filler trials
- prints a warning if an attention check was not answered with `1`
- writes a readable `analysis/parsed_experiment_data.json` output file

A new analysis pipeline is available in `analysis/analysis_pipeline.py`. It:
- loads `analysis/parsed_experiment_data.json`
- converts perceived character ratings to centered numeric scales
- maps perceived occupation to a five-point occupational prestige scale
- maps perceived age to a five-point age scale
- performs PCA and factor analysis on the eight continuous measures and on the six retained measures after excluding friendliness and age
- derives three dependent social measures: status, urban-ness, and formality
- fits mixed-effects linear regression models for each social measure using speaker and listener identifiers when available
- fits a multinomial logistic regression model for perceived speaker origin

Usage:

```bash
python3 analysis/analysis_pipeline.py
```

Results are written to `analysis/analysis_results/`.
