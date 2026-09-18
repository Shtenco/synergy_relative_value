import importlib, tomllib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_enterprise_release_metadata_is_consistent():
    py=tomllib.loads((ROOT/'pyproject.toml').read_text())
    mod=importlib.import_module('synergy_relative_value')
    assert py['project']['version']=='2.0.0'
    assert mod.__version__=='2.0.0'
    assert 'Version: `2.0.0`' in (ROOT/'README.md').read_text()
    assert '## 2.0.0' in (ROOT/'CHANGELOG.md').read_text()
    assert (ROOT/'docs/ENTERPRISE_ARCHITECTURE.md').exists()
    assert (ROOT/'docs/CUSTOMER_ACCEPTANCE.md').exists()
