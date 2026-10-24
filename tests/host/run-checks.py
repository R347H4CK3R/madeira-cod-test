#!/usr/bin/env python3
"""Run every host check and the IPA validator regressions, retaining failures.

Run from any directory with Python 3. Host checks need their documented native
dependencies (Swift, a C/C++ compiler, and configured Wine/FFmpeg where used).
Logs contain each check's combined stdout/stderr; results.json records its
original exit code. Missing dependencies and SKIP-FAIL results remain failures.
Use --exclude NAME only when that check is explicitly delegated to another job;
the report retains the complete discovered count and excluded names.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    host = Path(__file__).resolve().parent
    root = host.parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=root / 'build/host-check-results',
                        help='directory for per-check logs and results.json')
    parser.add_argument('--exclude', action='append', default=[], metavar='NAME',
                        help='delegate this exact check filename to another job (repeatable)')
    args = parser.parse_args()

    # Keep the validator explicit so deleting or renaming it cannot silently
    # remove its regressions from the suite.
    discovered = sorted(host.glob('check-*.py')) + [host / 'test-validate-ipa.py']
    excluded = sorted(set(args.exclude))
    unknown = set(excluded) - {script.name for script in discovered}
    if unknown:
        parser.error('unknown check for --exclude: ' + ', '.join(sorted(unknown)))
    if 'test-validate-ipa.py' in excluded:
        parser.error('the required IPA validator cannot be excluded')
    scripts = [script for script in discovered if script.name not in excluded]
    if not any(script.name.startswith('check-') for script in scripts):
        parser.error('--exclude must leave at least one host check selected')

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    results = {
        'started_at': datetime.now(timezone.utc).isoformat(),
        'python_version': sys.version.split()[0],
        'platform': sys.platform,
        'discovered_total': len(discovered),
        'excluded': excluded,
        'checks': [],
        'summary': {'total': len(scripts), 'passed': 0, 'failed': 0},
    }
    if excluded:
        print('Delegated checks (--exclude): ' + ', '.join(excluded), flush=True)

    for script in scripts:
        command = [sys.executable, '-u', str(script)]
        log = output / (script.stem + '.log')
        started = time.monotonic()
        print(f'RUN {script.name}', flush=True)
        with log.open('w', encoding='utf-8') as stream:
            stream.write(f'Check: {script.name}\n\n')
            stream.flush()
            try:
                process = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT)
                exit_code = process.returncode
            except OSError as error:
                exit_code = 127
                stream.write(f'Could not start check: {error}\n')
            duration = round(time.monotonic() - started, 3)
            stream.write(f'\nExit code: {exit_code}\nDuration seconds: {duration}\n')

        results['checks'].append({
            'name': script.name,
            'command': command,
            'exit_code': exit_code,
            'duration_seconds': duration,
            'log': log.name,
        })
        results['summary']['passed' if exit_code == 0 else 'failed'] += 1
        # Update after each check so an interrupted CI job retains results
        # already produced. No environment values are added to the report.
        (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
        status = 'PASS' if exit_code == 0 else 'FAIL'
        print(f'{status} {script.name}: exit {exit_code}, {duration:.3f}s; {log}', flush=True)

    results['finished_at'] = datetime.now(timezone.utc).isoformat()
    (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    summary = results['summary']
    print(f"{summary['passed']}/{summary['total']} checks passed; {summary['failed']} failed. Results: {output / 'results.json'}")
    return 1 if summary['failed'] else 0


if __name__ == '__main__':
    sys.exit(main())
