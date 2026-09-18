from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_enterprise_sql_and_compose_exist():
    pg=(ROOT/'deploy/postgres/001_audit.sql').read_text()
    ch=(ROOT/'deploy/clickhouse/001_audit.sql').read_text()
    compose=(ROOT/'deploy/docker-compose.enterprise.yml').read_text()
    assert 'CREATE TABLE IF NOT EXISTS audit_events' in pg
    assert 'request_id' in pg and 'tenant_id' in pg
    assert 'ENGINE = MergeTree' in ch and 'PARTITION BY' in ch
    assert 'postgres:' in compose and 'clickhouse:' in compose and 'healthcheck:' in compose
    assert (ROOT/'.env.enterprise.example').exists()


def test_enterprise_image_installs_optional_drivers_and_secret_file_is_ignored():
    docker=(ROOT/'Dockerfile').read_text()
    compose=(ROOT/'deploy/docker-compose.enterprise.yml').read_text()
    ignore=(ROOT/'.gitignore').read_text()
    assert '.[enterprise]' in docker
    assert '../.env.enterprise' in compose
    assert '../.env.enterprise.example' not in compose
    assert '.env.enterprise' in ignore
