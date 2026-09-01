from pathlib import Path


def test_release_workflow_has_versioning_auth_rollback_and_security_checks():
    text = Path('.github/workflows/step28-release.yml').read_text(encoding='utf-8')
    for expected in (
        'docker build',
        'RELEASE_VERSION: v1.1.0',
        'PREVIOUS_VERSION: v1.0.0',
        '/health',
        '/ready',
        '/model-info',
        'INFERENCE_API_KEY',
        'STEP28_SMOKE_API_KEY',
        'X-API-Key',
        '401',
        'docker pull',
        'previous-release',
        'id -u',
    ):
        assert expected in text


def test_release_environment_template_is_safe_and_non_secret():
    text = Path('deploy/release.env.example').read_text(encoding='utf-8')
    assert 'APP_ENV=production' in text
    assert 'IMAGE_TAG=' in text
    assert 'SECRET' not in text.upper()
    assert 'PASSWORD' not in text.upper()
