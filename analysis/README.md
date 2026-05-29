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