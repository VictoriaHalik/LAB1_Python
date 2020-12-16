from sqlalchemy import Column, Integer, String, DATE, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.scoping import scoped_session

engine = create_engine("postgresql://postgres:1q2w3e4r5t@localhost:5432/postgres")

sessionFactory = sessionmaker(bind=engine)
session = scoped_session(sessionFactory)

BaseModel = declarative_base()


class Client(BaseModel):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    surname = Column(String)
    email = Column(String)
    password = Column(String)
    age = Column(Integer)

    credits = relationship('Credit', lazy='dynamic', backref='clients')


class Credit(BaseModel):
    __tablename__ = "credits"

    credit_id = Column(Integer, primary_key=True)
    sum_take = Column(Integer)
    sum_pay = Column(Integer)
    period_month = Column(Integer)
    month_sum = Column(Integer)
    sum_paid = Column(Integer)
    sum_left = Column(Integer)
    month_paid = Column(Integer)
    start_date = Column(DATE)
    finish_date = Column(DATE)
    percent = Column(Integer)

    fk_client_id = Column(Integer, ForeignKey("clients.client_id"))


class Budget(BaseModel):
    __tablename__ = "budget"

    id = Column(Integer, primary_key=True)
    is_empty = Column(Boolean)
    available_sum = Column(Integer)


BaseModel.metadata.create_all(engine)
