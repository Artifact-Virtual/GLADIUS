import pytest


@pytest.fixture
def client():
    from ingest_bot.dashboard import app
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c
