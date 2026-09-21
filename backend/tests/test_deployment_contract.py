import json
import stat
from pathlib import Path

import pytest
from app.platform.model_artifact import sha256, verify_and_install


def test_model_artifact_is_verified_before_install(tmp_path: Path) -> None:
    model = tmp_path / "candidate.joblib"
    manifest = tmp_path / "manifest.json"
    destination = tmp_path / "image" / "final_candidate.joblib"
    model.write_bytes(b"trusted-test-artifact")
    manifest.write_text(json.dumps({"artifact_sha256": sha256(model)}), encoding="utf-8")

    assert verify_and_install(model, manifest, destination) == sha256(model)
    assert destination.read_bytes() == model.read_bytes()
    assert stat.S_IMODE(destination.stat().st_mode) == 0o444


def test_model_artifact_mismatch_never_installs(tmp_path: Path) -> None:
    model = tmp_path / "candidate.joblib"
    manifest = tmp_path / "manifest.json"
    destination = tmp_path / "image" / "final_candidate.joblib"
    model.write_bytes(b"untrusted-test-artifact")
    manifest.write_text(json.dumps({"artifact_sha256": "0" * 64}), encoding="utf-8")

    with pytest.raises(RuntimeError, match="checksum"):
        verify_and_install(model, manifest, destination)
    assert not destination.exists()


def test_container_and_worker_reference_verified_artifact() -> None:
    root = Path(__file__).resolve().parents[2]
    dockerfile = (root / "infra/containers/backend.Dockerfile").read_text(encoding="utf-8")
    terraform = (root / "infra/terraform/aws/main.tf").read_text(encoding="utf-8")
    worker = (root / "backend/app/platform/worker.py").read_text(encoding="utf-8")
    config = (root / "backend/app/platform/config.py").read_text(encoding="utf-8")

    assert "id=growthpilot_model" in dockerfile and "required=true" in dockerfile
    assert "GP_MODEL_PATH=/app/models/final_candidate.joblib" in dockerfile
    assert "GP_MODEL_MANIFEST_PATH=/app/artifacts/ml/final_candidate.json" in dockerfile
    assert "--destination /app/models/final_candidate.joblib" in dockerfile
    assert "model_path: Path" in config and "model_manifest_path: Path" in config
    assert "app.platform.worker" in terraform
    assert 'command = ["dramatiq", "app.platform.jobs"]' not in terraform
    assert "@dramatiq.actor" in worker and "def deliver_event" in worker
