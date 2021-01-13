from flask import Flask, request, abort, jsonify
from flask_bcrypt import Bcrypt
from shemas import ClientSchema, BudgetSchema, CreditSchema
from marshmallow import ValidationError
from models import Client, Budget, Credit, session
from flask_jwt import JWT, jwt_required, current_identity

# curl -X POST http://127.0.0.1:5000/clients -H "Content-Type: application/json" --data "{\"first_name\": \"Alina\", \"surname\": \"Dz\", \"email\": \"kmpopiv@gmail.com\", \"age
# \": \"15\", \"password\": \"1234\",\"client_id\": \"3\"}"

app = Flask(__name__)
bcrypt = Bcrypt(app)
session = session()
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SECRET_KEY'] = 'ilsvhjlbvaeljkbvlvbefjvbnvafjbvafsklvberjvbjlwb'
app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
app.config['JWT_AUTH_URL_RULE'] = '/clients/login'

#curl -X POST -H "Content-Type: application/json" -d '{"email" : "kmpopiv@gmail.com" , "password" : "1234"}' http://localhost:5000/clients/login


def authenticate(username, password):
    client = session.query(Client).filter(Client.email == username).one_or_none()
    if client and bcrypt.check_password_hash(client.password, password):
        return client


def identity(payload):
    id = payload['identity']
    return session.query(Client).filter(Client.id == id).one_or_none()


jwt = JWT(app, authenticate, identity)


@app.route('/clients/<client_id>')
@jwt_required()
def find_client(client_id):
    found_client = session.query(Client).filter(Client.id == client_id).one_or_none()
    schema = ClientSchema()
    schema.dump(found_client)
    if found_client is None:
        return 'client not found', 404
    if found_client.id != current_identity.id:
        return 'Access denied', 403
    client_schema = ClientSchema(exclude=['password'])
    client = client_schema.dump(found_client)
    return client

#curl -X GET -H "Authorization: JWT <token>" http://localhost:5000/clients/<client_id>

@app.route('/clients', methods=['POST'])
def create_clients():
    data = request.get_json()
    client_schema = ClientSchema()
    parsed_data = {'first_name': data['first_name'],
                   'surname': data['surname'],
                   'email': data['email'],
                   'age': data['age'],
                   'password': bcrypt.generate_password_hash(data['password']).decode('utf-8'),
                   'id': data['id']}
    try:
        client = client_schema.load(parsed_data)
    except ValidationError as err:
        return abort(400, err.messages)
    session.add(client)
    session.commit()
    return 'Client is registred'
#curl -X POST -H "Content-Type: application/json" --data '{"first_name": "Alina", "surname": "Dz","email": "kmpopiv@gmail.com", "age": "15", "password": "1234","id": "3"}' http://127.0.0.1:5000/clients

@app.route('/clients/<client_id>', methods=['DELETE'])
@jwt_required()
def del_user(client_id):
    found_client = session.query(Client).filter(Client.id == client_id).one_or_none()
    if found_client is None:
        return 'invalid id', 400
    if found_client.id != current_identity.id:
        return 'Access denied', 401
    session.delete(found_client)
    session.commit()
    return ''
#curl -X DELETE -H "Authorization: JWT <token>" http://localhost:5000/clients/<client_id>


@app.route('/clients/<client_id>', methods=['PUT'])
@jwt_required()
def edit_user(client_id):
    found_client = session.query(Client).filter(Client.id == client_id).one_or_none()
    if found_client is None:
        raise ValidationError(message='invalid id')
    if found_client.id != current_identity.id:
        return 'Access denied', 403
    data = request.json

    found_client.first_name = data['first_name']
    found_client.surname = data['surname']
    found_client.email = data['email']
    found_client.age = data['age']
    session.commit()
    return_schema = ClientSchema(exclude=['password'])
    return_client = return_schema.dump(found_client)
    return return_client
# curl -X PUT -H "Authorization: JWT <token>" -H "Content-Type: application/json" -d'{"first_name": "Alina", "surname": "Dz", "email": "kmpopiv@gmail.com", "age": "18"}' http://localhost:5000/clients/<client_id>

@app.route('/clients', methods=['GET'])
@jwt_required()
def clients():
    clients_list = session.query(Client)
    if clients_list:
        return jsonify(ClientSchema(exclude=['password'], many=True).dump(clients_list))
    else:
        return 'There is no clients'
#curl -X GET -H "Authorization: JWT <token>" http://localhost:5000/clients


@app.route('/credit/<client_id>')
@jwt_required()
def find_credit(client_id):
    found_client = session.query(Client).filter(Client.id == client_id).one_or_none()
    if found_client is None:
        return 'invalid id', 400
    found_credit = session.query(Credit).filter(Credit.fk_client_id == client_id)
    if found_credit:
        if found_client.id != current_identity.id:
            return 'Access denied', 403
        return jsonify(CreditSchema(many=True, exclude=['fk_client_id']).dump(found_credit))
    else:
        return 'There is no credit'
#curl -X GET -H "Authorization: JWT <token>" http://localhost:5000/credit/<client_id>

@app.route('/credit/<credit_id>', methods=['POST'])
@jwt_required()
def create_credit(credit_id):
    found_credit = session.query(Credit).filter(Credit.id == credit_id).one_or_none()
    if found_credit: raise ValidationError(message='invalid id')

    data = request.json
    credit_schema = CreditSchema()
    parsed_data = {'id': credit_id, 'sum_take': data['sum_take'],
                   'sum_pay': 0,
                   'pay_off': False,
                   'month_sum': data['month_sum'],
                   'sum_paid': 0,
                   'sum_left': int(data['sum_take']) * 1.3,
                   'month_paid': 0,
                   'percent': 30,
                   'start_date': data['start_date'],
                   'finish_date': data['finish_date'],
                   'fk_client_id': current_identity.id,
                   }
    found_cl = session.query(Client) \
        .filter(Client.id == parsed_data['fk_client_id']).one_or_none()
    if found_cl is None:
        return 'Client not found', 404
    try:
        credit = credit_schema.load(parsed_data)
    except ValidationError as err:
        return abort(400, err.messages)
    budget = session.query(Budget).filter(Budget.available_sum.isnot(None)).one_or_none()
    if budget.available_sum > credit.sum_take:
        budget.available_sum -= credit.sum_take
        session.add(credit)
        session.commit()
        return 'The credit is created'
    else:
        return 'There is no cost', 400
# curl -X POST -H "Content-Type: application/json" -d '{ "sum_take": "500", "month_sum": "100",
# "start_date": "2021-12-24", "finish_date": "2021-12-30","fk_client_id": "3"}'
# -H "Authorization: JWT <token>" http://localhost:5000/credit/<credit_id>


@app.route('/credit/<credit_id>', methods=['PUT'])
@jwt_required()
def pay_credit(credit_id):
    found_credit = session.query(Credit).filter(Credit.id == credit_id).one_or_none()
    if found_credit is None:
        raise ValidationError(message='Credit does not exist')
    if found_credit.fk_client_id != current_identity.id:
        return 'Access denied', 403
    data = request.json
    validation_schema = CreditSchema()
    got_data = {'sum_pay': data['sum_pay']}
    try:
        validation_schema.load(got_data)
    except ValidationError as err:
        return err.messages, 400
    if found_credit.sum_left <= 0: raise ValidationError(message='Credit paid off')
    found_credit.sum_pay = got_data['sum_pay']
    found_credit.month_paid += 1
    found_credit.sum_paid += int(found_credit.sum_pay)
    found_credit.sum_left = found_credit.sum_take - found_credit.sum_paid
    if found_credit.sum_left <= 0: found_credit.pay_off = True
    budget = session.query(Budget).filter(Budget.available_sum.isnot(None)).one_or_none()
    budget.available_sum += int(found_credit.sum_pay)
    session.commit()
    return_schema = CreditSchema()
    return_credit = return_schema.dump(found_credit)
    return return_credit

# curl -X PUT -H "Authorization: JWT <token>" -H "Content-Type: application/json" -d '{"sum_pay": "10"}' http://127.0.0.1:5000/credit/7


@app.route('/budget')
def budget_info():
    budget_found = session.query(Budget).filter(Budget.available_sum.isnot(None)).one_or_none()
    schema = BudgetSchema()
    if budget_found is None:
        return 'budget not found', 404
    budget_schema = BudgetSchema()
    budget = budget_schema.dump(budget_found)
    return budget


# curl -X POST http://127.0.0.1:5000/clients -H "Content-Type: application/json" --data "{\"first_name\": \"Alina\",
# \"surname\": \"Dz\", \"email\": \"kmpopiv@gmail.com\", \"age\": \"15\", \"password\": \"1234\",\"client_id\": \"4\"}"
# curl -X PUT http://127.0.0.1:5000/credit/3 -H "Content-Type: application/json" --data "{\"sum_pay\": \"1000\"}"
# curl -X DELETE http://127.0.0.1:5000/clients/2/credit
# curl -X GET http://127.0.0.1:5000/budget
# curl -X PUT http://127.0.0.1:5000/clients/4 -H "Content-Type: application/json" --data "{\"first_name\": \"Alina\",
# \"surname\": \"Dz\", \"email\": \"kmpopiv@gmail.com\", \"age\": \"15\"}"

# curl-X POST http://127.0.0.1:5000/credit/5 -H "Content-Type: application/json" --data "{ \"sum_take\": \"500\",
# \"month_sum\": \"100\", \"start_date\": \"2021-12-24\", \"finish_date\": \"2021-12-30\",\"fk_client_id\": \"4\"}"
