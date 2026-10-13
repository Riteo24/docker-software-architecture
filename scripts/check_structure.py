from pathlib import Path
import ast
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]

def imports(path):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node,ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node,ast.ImportFrom):
            yield node.module or ''

rules = {
    'monolith/app/presentation':('app.infrastructure',),
    'monolith/app/application':('app.infrastructure','app.presentation'),
    'monolith/app/domain':('app.infrastructure','app.presentation','app.application',
                           'fastapi','pydantic','psycopg','redis','sqlalchemy'),
    'hexagonal/core':('adapters','config','fastapi','pydantic','psycopg','csv'),
}
for directory,forbidden in rules.items():
    for path in (ROOT/directory).rglob('*.py'):
        for module in imports(path):
            assert not any(module==prefix or module.startswith(prefix+'.') for prefix in forbidden), (path,module)

for path in ROOT.rglob('*.py'):
    if '__pycache__' not in path.parts:
        ast.parse(path.read_text(),filename=str(path))

for architecture in ['monolith','hexagonal','microservices','event-driven']:
    config=yaml.safe_load((ROOT/architecture/'docker-compose.yml').read_text())
    for name,service in config['services'].items():
        if 'build' in service:
            context = service['build'] if isinstance(service['build'],str) else service['build']['context']
            dockerfile=ROOT/architecture/context/'Dockerfile'
            assert dockerfile.is_file(),dockerfile
        for dependency in service.get('depends_on',{}):
            assert dependency in config['services'],dependency

for architecture in ['monolith','hexagonal']:
    text=(ROOT/architecture/'Dockerfile').read_text()
    assert 'AS builder' in text and 'AS runtime' in text
    assert 'USER app' in text and 'HEALTHCHECK' in text
    config=yaml.safe_load((ROOT/architecture/'docker-compose.yml').read_text())
    assert config['services']['db']['image']=='postgres:16'
    assert config['services']['db']['volumes']
    assert config['services']['api']['depends_on']['db']['condition']=='service_healthy'

ms=yaml.safe_load((ROOT/'microservices/docker-compose.yml').read_text())
assert set(ms['services'])=={'catalog','users','orders','gateway'}
assert 'ms-net' in ms['networks']
for name,service in ms['services'].items():
    assert 'healthcheck' in service and 'restart' in service
    if name!='gateway':
        assert 'ports' not in service
        assert not any(module.startswith(('httpx','requests','urllib')) for module in imports(ROOT/'microservices/services'/name/'main.py'))
    document=yaml.safe_load((ROOT/'microservices/services'/name/'openapi.yaml').read_text()) if name!='gateway' else None
    if document:
        assert document['openapi'].startswith('3.')

for path in (ROOT/'event-driven/schemas').glob('*.json'):
    document=json.loads(path.read_text())
    assert document['title'] in {'OrderCreated','PaymentCaptured','EmailSent'}

print('PASS: architecture dependencies, Python syntax, build paths, Compose structure, OpenAPI and schemas')
