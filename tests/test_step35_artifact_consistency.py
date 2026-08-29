from pathlib import Path

import src.model_lifecycle as lifecycle


def test_promotion_requires_matching_preprocessor(tmp_path, monkeypatch):
    model = tmp_path / "candidate_model.pkl"
    preprocessor = tmp_path / "candidate_preprocessor.pkl"
    best_model = tmp_path / "best_model.pkl"
    best_preprocessor = tmp_path / "preprocessor.pkl"
    metadata = tmp_path / "model_metadata.json"

    model.write_bytes(b"candidate-model")
    best_model.write_bytes(b"current-model")
    best_preprocessor.write_bytes(b"current-preprocessor")

    monkeypatch.setattr(lifecycle, "BEST_MODEL_FILE", best_model)
    monkeypatch.setattr(lifecycle, "PREPROCESSOR_FILE", best_preprocessor)
    monkeypatch.setattr(lifecycle, "MODEL_METADATA_FILE", metadata)

    try:
        lifecycle.promote_candidate(model, {"model_name": "candidate"}, ["f1"], preprocessor)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("promotion must require a candidate preprocessor")

    assert best_model.read_bytes() == b"current-model"
    assert best_preprocessor.read_bytes() == b"current-preprocessor"


def test_promotion_replaces_model_and_preprocessor_together(tmp_path, monkeypatch):
    model = tmp_path / "candidate_model.pkl"
    preprocessor = tmp_path / "candidate_preprocessor.pkl"
    best_model = tmp_path / "best_model.pkl"
    best_preprocessor = tmp_path / "preprocessor.pkl"
    metadata = tmp_path / "model_metadata.json"

    model.write_bytes(b"candidate-model")
    preprocessor.write_bytes(b"candidate-preprocessor")
    best_model.write_bytes(b"current-model")
    best_preprocessor.write_bytes(b"current-preprocessor")

    monkeypatch.setattr(lifecycle, "BEST_MODEL_FILE", best_model)
    monkeypatch.setattr(lifecycle, "PREPROCESSOR_FILE", best_preprocessor)
    monkeypatch.setattr(lifecycle, "MODEL_METADATA_FILE", metadata)

    lifecycle.promote_candidate(
        model,
        {"model_name": "candidate"},
        ["f1"],
        preprocessor,
    )

    assert best_model.read_bytes() == b"candidate-model"
    assert best_preprocessor.read_bytes() == b"candidate-preprocessor"
    saved = metadata.read_text(encoding="utf-8")
    assert '"artifact_consistency": "model_and_preprocessor_promoted_together"' in saved
    assert not Path(str(best_model) + ".candidate").exists()
    assert not Path(str(best_preprocessor) + ".candidate").exists()
