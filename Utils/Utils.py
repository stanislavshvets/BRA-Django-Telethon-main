import datetime
import os
import time
import telethon

def calc_order_date(self):
    msg_date = msg.date.astimezone(get_localzone())
    order_date = msg_date if msg_date.hour < self.day_border_local_hour else (msg_date + timedelta(days=1))

    year = order_date.year
    month = order_date.month
    day = order_date.day

    return order_date, year, month, day

def create_model_path(date, internal_customer_profile):
    if isinstance(date, datetime.datetime ):
        order_date, year, month, day = calc_order_date(date)
    else:
        full_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    path = f"../common_data/models/{year}/{full_date.strftime('%B')}/{day:02d}/{internal_customer_profile}"

def convert_model_path_to_video_path():
    pass