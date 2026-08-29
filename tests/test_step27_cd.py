from pathlib import Path

def test_production_dockerfile_is_non_root_and_has_healthcheck():
    text=Path('Dockerfile').read_text(encoding='utf-8')
    assert 'USER appuser' in text
    assert 'HEALTHCHECK' in text
    assert 'uvicorn src.inference_service:app' in text

def test_step27_workflow_has_docker_and_smoke_validation():
    text=Path('.github/workflows/step27-cd.yml').read_text(encoding='utf-8')
    assert 'docker build' in text
    assert 'docker run' in text
    assert '/health' in text
    assert '/metrics' in text
    assert 'id -u' in text
