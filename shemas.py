from marshmallow import Schema, fields, post_load
from LABS_Application_Programming.models import *


class ClientSchema(Schema):
    client_id = fields.Int()
    first_name = fields.Str()
    surname = fields.Str()
    email = fields.Str()
    password = fields.Str()
    age = fields.Int()

    @post_load
    def create_user(self, data, **kwargs):
        return Client(**data)


class CreditSchema(Schema):
    credit_id = fields.Int()
    sum_take = fields.Int()
    sum_pay = fields.Int()
    pay_off = fields.Bool()
    month_sum = fields.Int()
    sum_paid = fields.Int()
    sum_left = fields.Int()
    month_paid = fields.Int()
    start_date = fields.Date()
    finish_date = fields.Date()
    percent = fields.Int()
    fk_client_id = fields.Int()

    @post_load
    def create_user(self, data, **kwargs):
        return Credit(**data)


class BudgetSchema(Schema):
    is_empty = fields.Bool()
    available_sum = fields.Int()

    @post_load
    def create_user(self, data, **kwargs):
        return Client(**data)