import datetime
import os
import re
import time
import telethon
import pathlib

def calc_order_date(date: datetime.datetime, day_border_local_hour):
    order_date = date if date.hour < day_border_local_hour else (date + datetime.timedelta(days=1))

    year = order_date.year
    month = order_date.month
    day = order_date.day

    return order_date, year, month, day


def sanitize_folder_name(name):
    invalid_chars = '<>:"/\\|?*'
    # Remove invalid characters
    sanitized_name = re.sub(f"[{re.escape(invalid_chars)}]", "", name)
    # Remove trailing periods and spaces
    sanitized_name = sanitized_name.rstrip('. ')
    return sanitized_name


def _create_customer_profile(username, first_name, last_name):

    _customer_profile = sanitize_folder_name(
        f'(@{username})' +
        ' ' +
        (first_name or '') +
        ' '
        + (last_name or '')
    )

    return _customer_profile


def create_model_path(date, username, first_name, last_name, day_border_local_hour):

    customer_profile = _create_customer_profile(username, first_name, last_name,)
    order_date, year, month, day = calc_order_date(date, day_border_local_hour)

    path = f"common_data/models/{year}/{order_date.strftime('%B')}/{day:02d}/{customer_profile}"
    os.makedirs(path, exist_ok=True)
    return path

def convert_model_path_to_video_path(file_path):
    file_path.replace('/model/', '/video/')
    file_path.replace('.obj', '.mp4')
    return file_path
