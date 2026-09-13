import json
import sys

data = json.load(open('coverage_backend.json'))
files = data['files']

print('Per-file Coverage Report:')
print('-' * 70)
print(f'{"File Name":<45} {"Coverage":>10}')
print('-' * 70)

files_below_80 = []
for k, v in sorted(files.items()):
    fname = k.replace('\\', '/')
    coverage = v['summary']['percent_covered']
    print(f'{fname:<45} {coverage:>10.2f}%')
    if coverage < 80 and '__pycache__' not in fname:
        files_below_80.append((fname, coverage))

print('-' * 70)
total_covered = sum(f['summary']['covered_lines'] for f in files.values())
total_statements = sum(f['summary']['num_statements'] for f in files.values())
overall_coverage = (total_covered / total_statements * 100) if total_statements > 0 else 0
print(f'OVERALL: {overall_coverage:.2f}%')

if files_below_80:
    print('\nFiles BELOW 80% coverage:')
    for fname, coverage in files_below_80:
        print(f'  - {fname}: {coverage:.2f}%')
    sys.exit(1)
else:
    print('\nAll files are at or above 80% coverage.')
    sys.exit(0)
