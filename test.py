from flask import json
from app import app
from models import BaseModel, engine, session, Budget
import pytest


def set_budget():
    budget = Budget(available_sum=512000, is_empty=False)
    session.add(budget)
    session.commit()


@pytest.fixture
def client():
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)
    client = app.test_client()
    objects(client)
    return client


def auth(client):
    r = client.post('/clients/login',
                   data= json.dumps({"email": "example1@gmail.com", "password": "1q2w3e4r5t"}),
                    content_type= 'application/json').get_json()
    token = r["access_token"]
    return token


def objects(client):
    client.post('/clients', data=json.dumps({"id": 1, "first_name": "Name1", "surname": "Last_Name1",
                "email": "example1@gmail.com", "password": "1q2w3e4r5t", "age": 25}), content_type='application/json')

    client.post('/clients', data=json.dumps({'id': 2, "first_name": 'Name2', "surname": 'Last_Name2',
                "email": 'example2@gmail.com', "password": "1q2w3e4r5t", "age": 35}), content_type='application/json')


def test_post_client(client):
    req = client.post('/clients', json={"id": 3, "first_name": 'Name3', "surname": 'Last_Name3',
                                             "email": 'example3@gmail.com',"password": "1q2w3e4r5t",
                                             "age": 25}).status_code
    assert req == 200


def test_delete_client(client):
    user_token = auth(client)
    req1 = client.delete('/clients/1', headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req1 == 200
    req2 = client.delete('/clients/2', headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req2 == 401


def test_clients(client):
    user_token = auth(client)
    req = client.get('/clients', headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req == 200


def test_get_client(client):
    user_token = auth(client)
    req1 = client.get('/clients/1', headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req1 == 200
    req2 = client.get('/clients/2', headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req2 == 403
    req3 = client.get('/clients/123', headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req3 == 404


def test_put_client(client):
    user_token = auth(client)
    req1 = client.put('/clients/1', json={"first_name": 'Name10', "surname": 'Last_Name10',
                                             "email": 'example10@gmail.com', "age": 25},
                           headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req1 == 200

    req2 = client.put('/clients/2', json={"first_name": 'Name10', "surname": 'Last_Name10',
                                             "email": 'example10@gmail.com', "age": 25},
                           headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req2 == 403


def test_create_credit(client):
    user_token = auth(client)
    set_budget()
    req1 = client.post('/credit/1', json={ "sum_take": "500", "month_sum": "100",
                                          "start_date": "2021-12-24", "finish_date": "2021-12-30","fk_client_id": "1"},
                      headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req1 == 200
    req2 = client.post('/credit/2', json={ "sum_take": "1000500", "month_sum": "100000",
                                          "start_date": "2021-12-24", "finish_date": "2021-12-30","fk_client_id": "1"},
                      headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req2 == 400


def test_find_credit(client):
    user_token = auth(client)
    req1 = client.get('/credit/1', headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req1 == 200
    req2 = client.get('/credit/2', headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req2 == 403


def test_pay_credit(client):
    user_token = auth(client)
    # set_budget()
    test_create_credit(client)
    req = client.put('/credit/1', json={"sum_pay": "10"},
                      headers={'Authorization': f'JWT {user_token}'}).status_code
    assert req == 200


def test_budget(client):
    req1 = client.get('/budget').status_code
    assert req1 == 404
    set_budget()
    req2 = client.get('/budget').status_code
    assert req2 == 200
