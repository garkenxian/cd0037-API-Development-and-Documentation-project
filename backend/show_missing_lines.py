import json

data = json.load(open('coverage_backend.json'))
files = data['files']

controllers = ['controllers\\categories.py', 'controllers\\games.py', 'controllers\\questions.py', 'controllers\\users.py']

print('UNCOVERED LINES BY CONTROLLER')
print('=' * 80)

for controller in controllers:
    if controller in files:
        info = files[controller]
        missing = info.get('missing_lines', [])
        coverage = info['summary']['percent_covered']
        print(f'\n{controller.replace(chr(92), "/")}')
        print(f'Coverage: {coverage:.2f}%')
        print(f'Missing lines: {sorted(missing) if missing else "None"}')
