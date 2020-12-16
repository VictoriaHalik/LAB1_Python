from LABS_Application_Programming.models import *
from datetime import date

s = session()

# client = Client(client_id=1, first_name='Name', surname='Last_Name',
#               email='example@gmail.com', password="********", age=25)
client2 = Client(client_id=2, first_name='Name2', surname='Last_Name2',
              email='example2@gmail.com', password="************", age=35)


# credit1 = Credit(credit_id=1, sum_take=5000, sum_pay=6500,pay_off =False period_month=12,
#                 month_sum=550, sum_paid=0, sum_left=6500, month_paid=0, start_date=date(2020, 12, 1),
#                 finish_date=date(2021, 12, 1), percent=30, fk_client_id=client.client_id)

# credit2 = Credit(credit_id=2, sum_take=10000, sum_pay=16000, period_month=24,
#                 month_sum=670, sum_paid=8000, sum_left=8000, month_paid=12, start_date=date(2019, 11, 1),
#                 finish_date=date(2021, 11, 1), percent=30, fk_client_id=client2.client_id)
#
# credit3 = Credit(credit_id=3, sum_take=50000, sum_pay=65000, period_month=12,
#                 month_sum=5500, sum_paid=0, sum_left=65000, month_paid=0, start_date=date(2020, 12, 1),
#                 finish_date=date(2021, 12, 1), percent=30, fk_client_id=client2.client_id)
#
# credit4 = Credit(credit_id=4, sum_take=5000, sum_pay=6500, period_month=12,
#                 month_sum=550, sum_paid=0, sum_left=6500, month_paid=0, start_date=date(2020, 12, 1),
#                 finish_date=date(2021, 12, 1), percent=30, fk_client_id=client.client_id)


budget = Budget(is_empty=False, available_sum=512000)


# s.add(client)
s.add(client2)
# s.add(credit1)
# s.add(credit2)
# s.add(credit3)
# s.add(credit4)
s.add(budget)


s.commit()
