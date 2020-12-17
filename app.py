from flask import Flask, request, abort, jsonify
from flask_bcrypt import Bcrypt
from LABS_Application_Programming.shemas import ClientSchema, BudgetSchema, CreditSchema
from marshmallow import ValidationError
from LABS_Application_Programming.models import Client, Budget, Credit, session
import datetime

# curl -X POST http://127.0.0.1:5000/clients -H "Cont
# ent-Type: application/json" --data "{\"first_name\": \"Alina\", \"surname\": \"Dz\", \"email\": \"kmpopiv@gmail.com\", \"age
# \": \"15\", \"password\": \"1234\",\"client_id\": \"3\"}"

app = Flask(__name__)
bcrypt = Bcrypt(app)
session = session()


@app.route('/clients/<client_id>')
def find_client(client_id):
    found_client = session.query(Client).filter(Client.client_id == client_id).one_or_none()
    schema = ClientSchema()
    try:
        schema.dump(found_client)
    except ValidationError as err:
        return abort(400, 'invalid id')
    if found_client is None:
        return 'client not found', 404
    client_schema = ClientSchema(exclude=['password'])
    client = client_schema.dump(found_client)
    return client


@app.route('/clients', methods=['POST'])
def create_clients():
    data = request.json
    client_schema = ClientSchema()
    parsed_data = {'first_name': data['first_name'],
                   'surname': data['surname'],
                   'email': data['email'],
                   'age': data['age'],
                   'password': bcrypt.generate_password_hash(data['password']).decode('utf-8'),
                   'client_id': data['client_id']}
    try:
        client = client_schema.load(parsed_data)
    except ValidationError as err:
        return abort(400, err.messages)
    session.add(client)
    session.commit()
    return 'token placeholder'


@app.route('/clients/<client_id>', methods=['DELETE'])
def del_user(client_id):
    found_client = session.query(Client).filter(Client.client_id == client_id).one_or_none()
    if found_client is None:
        return 'invalid id', 400
    session.delete(found_client)
    session.commit()
    return ''


@app.route('/clients/<client_id>', methods=['PUT'])
def edit_user(client_id):
    found_client = session.query(Client).filter(Client.client_id == client_id).one_or_none()
    if found_client is None:
        raise ValidationError(message='invalid id')
    data = request.json

    found_client.first_name = data['first_name']
    found_client.surname = data['surname']
    found_client.email = data['email']
    found_client.age = data['age']
    session.commit()
    return_schema = ClientSchema(exclude=['password'])
    return_client = return_schema.dump(found_client)
    return return_client


@app.route('/clients', methods=['GET'])
def clients():
    clients_list = session.query(Client)
    if clients_list:
        return jsonify(ClientSchema(exclude=['password'], many=True).dump(clients_list))
    else:
        return 'There is no clients'


@app.route('/credit/<client_id>')
def find_credit(client_id):
    found_client = session.query(Client).filter(Client.client_id == client_id).one_or_none()
    if found_client is None:
        return 'invalid id', 400
    found_credit = session.query(Credit).filter(Credit.fk_client_id == client_id)
    if found_credit:
        return jsonify(CreditSchema(many=True, exclude=['fk_client_id']).dump(found_credit))
    else:
        return 'There is no credit'


@app.route('/credit/<credit_id>', methods=['POST'])
def create_credit(credit_id):
    found_credit = session.query(Credit).filter(Credit.credit_id == credit_id).one_or_none()
    if found_credit: raise ValidationError(message='invalid id')
    data = request.json
    credit_schema = CreditSchema()
    parsed_data = {'credit_id': credit_id, 'sum_take': data['sum_take'],
                   'sum_pay': 0,
                   'pay_off': False,
                   'month_sum': data['month_sum'],
                   'sum_paid': 0,
                   'sum_left': int(data['sum_take']) * 1.3,
                   'month_paid': 0,
                   'percent': 30,
                   'start_date': data['start_date'],
                   'finish_date': data['finish_date'],
                   'fk_client_id': data['fk_client_id']
                   }
    found_cl = session.query(Client) \
        .filter(Client.client_id == parsed_data['fk_client_id']).one_or_none()
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
        return 'token placeholder'
    else:
        raise ValidationError(message='There is no cost')
    # budget = session.query(Budget).filter(Budget.available_sum.isnot(None)).one_or_none()
    #
    # budget.available_sum -= credit.sum_take


@app.route('/credit/<credit_id>', methods=['PUT'])
def pay_credit(credit_id):
    found_credit = session.query(Credit).filter(Credit.credit_id == credit_id).one_or_none()
    if found_credit is None:
        raise ValidationError(message='Credit does not exist')
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


# @app.route('/clients/<credit_id>/credit', methods=['DELETE'])
# def del_credit(credit_id):
#     found_credit = session.query(Credit).filter(Credit.credit_id == credit_id).one_or_none()
#     if found_credit is None:
#         return 'invalid id', 400
#     elif found_credit.sum_left <= 0:
#         session.delete(found_credit)
#         session.commit()
#         return 'sucseed'
#     else:
#         return 'credit can not be delete'


@app.route('/budget')
def budget_info():
    budget_found = session.query(Budget).filter(Budget.available_sum.isnot(None)).one_or_none()
    schema = BudgetSchema()
    if budget_found is None:
        return 'budget not found', 404
    budget_schema = BudgetSchema()
    budget = budget_schema.dump(budget_found)
    return budget


if __name__ == "__main__":
    app.run()

# curl -X POST http://127.0.0.1:5000/clients -H "Content-Type: application/json" --data "{\"first_name\": \"Alina\", \"surname\": \"Dz\", \"email\": \"kmpopiv@gmail.com\", \"age\": \"15\", \"password\": \"1234\",\"client_id\": \"4\"}"
# curl -X PUT http://127.0.0.1:5000/credit/3 -H "Content-Type: application/json" --data "{\"sum_pay\": \"1000\"}"
# curl -X DELETE http://127.0.0.1:5000/clients/2/credit
# curl -X GET http://127.0.0.1:5000/budget
# curl -X PUT http://127.0.0.1:5000/clients/4 -H "Content-Type: application/json" --data "{\"first_name\": \"Alina\", \"surname\": \"Dz\", \"email\": \"kmpopiv@gmail.com\", \"age\": \"15\"}"

# curl-X POST http://127.0.0.1:5000/credit/5 -H "Content-Type: application/json" --data "{ \"sum_take\": \"500\", \"month_sum\": \"100\", \"start_date\": \"2021-12-24\", \"finish_date\": \"2021-12-30\",\"fk_client_id\": \"4\"}"