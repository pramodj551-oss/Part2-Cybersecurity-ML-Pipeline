from pathlib import Path


def test_step29_e2e_contract_and_deployment_assets():
    readme = Path('README.md').read_text(encoding='utf-8')
    assert 'Raw Dataset' in readme
    assert 'Best Regression Model' in readme
    assert 'Prediction' in readme
    assert Path('run_pipeline.py').exists()
    assert Path('Dockerfile').exists()


def test_step29_ci_covers_pipeline_lifecycle():
    workflows = list(Path('.github/workflows').glob('*.yml')) + list(Path('.github/workflows').glob('*.yaml'))
    text = '\n'.join(p.read_text(encoding='utf-8') for p in workflows)
    assert 'run_pipeline.py' in text
    assert 'pytest' in text
    assert 'docker build' in text
