from PIL import Image
from datetime import datetime

def resize_image(image_path, max_width=800, max_height=600):
    with Image.open(image_path) as img:
        img.thumbnail((max_width, max_height))
        img.save(image_path)

def calculate_price_and_season(date, persons):
    month = date.month
    day = date.day
    if (month == 6 and day >= 1) or month == 7 or month == 8 or (month == 9 and day <= 15):
        return 150, 'ljetna sezona'
    else:
        if int(persons) <= 2:
            return 100, 'zimska sezona'
        else:
            return 200, 'zimska sezona'