from pathlib import Path


def test_production_dockerfile_is_non_root_and_has_healthcheck():
    text = Path('Dockerfile').read_text(encoding='utf-8')
    assert 'USER appuser' in text
    assert 'HEALTHCHECK' in text
    assert 'src.inference_service:app' in text


def test_step27_workflow_has_mandatory_auth_docker_and_smoke_validation():
    text = Path('.github/workflows/step27-cd.yml').read_text(encoding='utf-8')
    for expected in (
        'docker build', 'docker run', '/health', '/ready', '/model-info',
        'INFERENCE_API_KEY', '401', 'X-API-Key', 'id -u'
    ):
        assert expected in text
