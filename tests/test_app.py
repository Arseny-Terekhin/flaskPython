import pytest
from main import app, db, User, Task
from flask import g

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def register(client, username, password):
    return client.post('/register', data={'userName': username, 'password': password}, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={'userName': username, 'password': password}, follow_redirects=True)

def test_register_and_login(client):
    response = client.post("/register", data={
        "userName": "testuser",
        "password": "testpass"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Авторизация" in response.data.decode("utf-8")

def test_add_task(client):
    register(client, "user1", "pass")
    login(client, "user1", "pass")
    response = client.post('/base', data={'titleTask': 'Test Task', 'textTask': 'Test Content'}, follow_redirects=True)
    assert b"Test Task" in response.data

def test_update_task(client):
    register(client, "user2", "pass")
    login(client, "user2", "pass")
    client.post('/base', data={'titleTask': 'Old Title', 'textTask': 'Old Content'}, follow_redirects=True)
    with app.app_context():
        task_id = Task.query.first().id
    response = client.post(f'/base/{task_id}', data={'titleTask': 'New Title', 'textTask': 'New Content'}, follow_redirects=True)
    assert b'New Title' in response.data

def test_delete_task(client):
    register(client, "user3", "pass")
    login(client, "user3", "pass")
    client.post('/base', data={'titleTask': 'Delete Me', 'textTask': 'Bye'}, follow_redirects=True)
    with app.app_context():
        task_id = Task.query.first().id
    response = client.get(f'/base/delete/{task_id}', follow_redirects=True)
    assert b'Delete Me' not in response.data
