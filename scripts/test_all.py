from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
projects = ['monolith','hexagonal','microservices/services/catalog',
            'microservices/services/users','microservices/services/orders','event-driven']
for project in projects:
    print('Testing '+project,flush=True)
    subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider'],
                   cwd=ROOT/project,check=True)
print('All unit and HTTP contract tests passed')
