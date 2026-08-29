from pathlib import Path


def test_release_workflow_has_versioning_smoke_rollback_and_security_checks():
    text = Path('.github/workflows/step28-release.yml').read_text(encoding='utf-8')
    for expected in ('docker build', 'GITHUB_RUN_NUMBER', '/health', '/ready', '/metrics', 'rollback-candidate', 'id -u'):
        assert expected in text


def test_release_environment_template_is_safe_and_non_secret():
    text = Path('deploy/release.env.example').read_text(encoding='utf-8')
    assert 'APP_ENV=production' in text
    assert 'IMAGE_TAG=' in text
    assert 'SECRET' not in text.upper()
    assert 'PASSWORD' not in text.upper()
