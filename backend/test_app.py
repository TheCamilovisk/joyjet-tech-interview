import json

import pytest

from app import create_app


@pytest.fixture()
def testing_client():
    app = create_app(config='test')

    test_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield test_client

    ctx.pop()


def _load_data(filepath):
    with open(filepath) as f:
        data = json.load(f)
    return data


def test_level1(testing_client):
    data = _load_data('./level1/data.json')

    response = testing_client.post('/checkout', json=data)
    assert response.status_code == 200

    output = _load_data('./level1/output.json')
    assert output == response.get_json()


def test_level2(testing_client):
    data = _load_data('./level2/data.json')

    response = testing_client.post('/checkout', json=data)
    assert response.status_code == 200

    output = _load_data('./level2/output.json')
    assert output == response.get_json()


def test_level3(testing_client):
    data = _load_data('./level3/data.json')

    response = testing_client.post('/checkout', json=data)
    assert response.status_code == 200

    output = _load_data('./level3/output.json')
    assert output == response.get_json()
