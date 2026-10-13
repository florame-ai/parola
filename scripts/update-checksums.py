"""Refresh checksums for repository files, excluding ignored files and this index."""
import hashlib
import pathlib
import subprocess

root = pathlib.Path(__file__).resolve().parents[1]
files = subprocess.check_output(
    ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root
).decode('utf-8').split('\0')
lines = []
for name in sorted(set(files)):
    file = root / name
    if name and name != 'CHECKSUMS.sha256' and file.is_file():
        lines.append(f'{hashlib.sha256(file.read_bytes()).hexdigest()}  {name}')
(root / 'CHECKSUMS.sha256').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
print(f'Checksums: {len(lines)} files')
