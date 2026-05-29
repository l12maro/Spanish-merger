#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

QUESTION_ITEMS = {
    'q1': {
        'question': 'Esta persona suena...',
        'scales': [
            {'id': 'q1_s1', 'prompt': 'informal — formal'},
            {'id': 'q1_s2', 'prompt': 'de nivel socioeconómico bajo — de nivel socioeconómico alto'},
            {'id': 'q1_s3', 'prompt': 'con menos estudios — con más estudios'},
            {'id': 'q1_s4', 'prompt': 'menos masculina — más masculina'},
            {'id': 'q1_s5', 'prompt': 'menos simpática — más simpática'},
            {'id': 'q1_s6', 'prompt': 'más rural — más urbana'},
            {'id': 'q1_s7', 'prompt': 'poco natural — natural'},
        ],
    },
    'q2': {'question': '¿A qué crees que se dedica esta persona?'},
    'q3': {'question': '¿Qué edad crees que tiene?'},
    'q4': {'question': '¿De dónde crees que es esta persona?'},
    'q5': {'question': '¿Algo más que se te ocurre de esta persona?'},
}
EXPECTED_Q1_SCALE_COUNT = len(QUESTION_ITEMS['q1']['scales'])


def collect_csv_paths(paths):
    csv_paths = []
    for input_path in paths:
        p = Path(input_path)
        if p.is_dir():
            csv_paths.extend(sorted(p.glob('*.csv')))
        elif p.is_file() and p.suffix.lower() == '.csv':
            csv_paths.append(p)
        else:
            print(f'Warning: skipped unsupported path {input_path}', file=sys.stderr)
    return csv_paths


def parse_response(response_text):
    if not response_text:
        return {}
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            return {}


def get_attention_check(response_obj):
    q1_keys = sorted(k for k in response_obj if k.startswith('q1_s'))
    if len(q1_keys) <= EXPECTED_Q1_SCALE_COUNT:
        return None
    attention_field = q1_keys[(len(q1_keys) - 1) // 2]
    value = response_obj.get(attention_field)
    return {
        'field': attention_field,
        'value': str(value) if value is not None else None,
        'passed': value == 1 or value == '1',
    }


def build_trial(row, source_file):
    response_obj = parse_response(row.get('response', ''))
    trial = {
        'source_file': str(source_file),
        'participant_id': row.get('prolific_id') or None,
        'trial_index': int(row['trial_index']) if row.get('trial_index') else None,
        'item_id': row.get('item_id') or None,
        'condition': row.get('condition') or None,
        'audio': row.get('audio') or None,
        'task': row.get('task') or None,
        'response_type': row.get('trial_type') or None,
        'time_elapsed': int(row['time_elapsed']) if row.get('time_elapsed') else None,
        'response': response_obj,
        'questions': [],
        'attention_check': None,
    }

    if trial['task'] != 'audio_questions':
        return trial

    q1_keys = sorted(k for k in response_obj if k.startswith('q1_s'))
    q1_scales = []
    attention_index = None
    if len(q1_keys) == EXPECTED_Q1_SCALE_COUNT + 1:
        attention_index = (len(q1_keys) - 1) // 2

    for index, key in enumerate(q1_keys):
        if attention_index is not None and index == attention_index:
            prompt = 'Atención (control)'
        elif attention_index is not None and index > attention_index:
            prompt = QUESTION_ITEMS['q1']['scales'][index - 1]['prompt']
        else:
            prompt = QUESTION_ITEMS['q1']['scales'][index]['prompt'] if index < len(QUESTION_ITEMS['q1']['scales']) else 'Atención (control)'
        q1_scales.append({'field': key, 'prompt': prompt, 'value': str(response_obj.get(key, ''))})

    attention_check = get_attention_check(response_obj)
    if attention_check:
        trial['attention_check'] = attention_check

    trial['questions'].append({
        'question_id': 'q1',
        'question_text': QUESTION_ITEMS['q1']['question'],
        'scales': q1_scales,
        'attention_check': attention_check,
    })

    for qid in ['q2', 'q3', 'q4', 'q5']:
        if qid in response_obj:
            trial['questions'].append({
                'question_id': qid,
                'question_text': QUESTION_ITEMS[qid]['question'],
                'response': response_obj[qid],
            })

    return trial


def parse_csv_file(file_path):
    trials = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            trials.append(build_trial(row, file_path))
    return trials


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 analysis/parse_experiment_data.py <csv-file|folder> [more files/folders]')
        sys.exit(1)

    input_paths = sys.argv[1:]
    csv_paths = collect_csv_paths(input_paths)

    if not csv_paths:
        print('No CSV files found to parse.', file=sys.stderr)
        sys.exit(1)

    dataset = {}
    errors = 0
    warnings = 0

    for csv_path in csv_paths:
        trials = []
        for trial in parse_csv_file(csv_path):
            if trial['task'] == 'audio_questions':
                if trial['attention_check'] and not trial['attention_check']['passed']:
                    warnings += 1
                    print(
                        f"WARNING: attention check failed in {csv_path.name} "
                        f"participant={trial['participant_id']} item={trial['item_id']} "
                        f"condition={trial['condition']} field={trial['attention_check']['field']} "
                        f"value={trial['attention_check']['value']}",
                        file=sys.stderr,
                    )
                trials.append(trial)
        dataset[csv_path.name] = trials

    output_path = Path(__file__).resolve().parent / 'parsed_experiment_data.json'
    output_data = {
        'metadata': {
            'parsed_at': __import__('datetime').datetime.now().isoformat(),
            'files': [str(p.resolve()) for p in csv_paths],
        },
        'files': dataset,
    }
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(output_data, outfile, indent=2, ensure_ascii=False)

    total_trials = sum(len(trials) for trials in dataset.values())
    print(f'Parsed {total_trials} audio question trials from {len(csv_paths)} file(s).')
    if warnings:
        print(f'Attention check warnings: {warnings}. See stderr output for details.')
    else:
        print('No attention check failures were detected.')
    print(f'Parsed output written to {output_path}')


if __name__ == '__main__':
    main()
