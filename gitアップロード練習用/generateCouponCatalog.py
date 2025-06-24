import csv
import sys
from html import escape
import datetime

def unixtime_to_timestamp(unixtime):
    # Unix時間をdatetimeオブジェクトに変換
    dt = datetime.datetime.fromtimestamp(unixtime)
    # タイムスタンプ形式（例: '2023-01-01 12:00:00'）にフォーマット
    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


def generate_html_from_csv(csv_file_path):
    css_styles = """
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
        }
        .coupon-card {
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            transition: 0.3s;
            width: 300px;
            margin: 10px;
            background-color: #f5f5f5;
        }
        .coupon-card img {
            width: 100%;
            height: auto;
        }
        .container {
            padding: 2px 16px;
            text-align: center;
        }
        h2, p, .date-info {
            margin: 0;
        }
        .prices {
            margin-top: 10px;
        }
        .normal-price {
            text-decoration: line-through;
        }
        .discount-price {
            color: red;
        }
    </style>
    """
    html_output = f'<!DOCTYPE html>\n<html lang="jp">\n<head>\n<meta charset="UTF-8">\n<title>Coupon Catalog</title>\n{css_styles}\n</head>\n<body>\n<div style="display: flex; justify-content: center; flex-wrap: wrap; width: 100%;">\n'
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            coupon_name = escape(row['couponName'])
            coupon_description = escape(row['couponDescription'])
            image_url = escape(row['imageUrl'])
            normal_price = escape(row['normalPrice'])
            discount_price = escape(row['discountPrice'])
            start_datetime = escape(row['startDateTime'])
            if start_datetime: 
                start_datetime_timestamp = unixtime_to_timestamp(int(start_datetime))
            else:
                start_datetime_timestamp = ""
            end_datetime = escape(row['endDateTime'])
            if end_datetime:    
                end_datetime_timestamp = unixtime_to_timestamp(int(end_datetime))
            else:
                end_datetime_timestamp = ""
            start_date = escape(row['startDate'])
            expiry_date = escape(row['expiryDate'])
            html_output += f'<div class="coupon-card">\n<img src="{image_url}" alt="{coupon_name}">\n<div class="container">\n<h2>{coupon_name}</h2>\n<p>{coupon_description}</p>\n<p class="date-info">開始日時: {start_datetime_timestamp}</p>\n<p class="date-info">終了日時: {end_datetime_timestamp}</p>\n<p class="date-info">開始日: {start_date}</p>\n<p class="date-info">有効期限: {expiry_date}</p>\n<div class="prices">\n<span class="normal-price">通常価格 : {normal_price}</span>\n<span class="discount-price">割引価格 : {discount_price}</span>\n</div>\n</div>\n</div>\n'
    html_output += '</div>\n</body>\n</html>'
    return html_output

# コマンドライン引数からファイル名を取得
csv_file_path = sys.argv[1]

# HTMLファイルを生成
html_content = generate_html_from_csv(csv_file_path)
with open('coupon_catalog.html', 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)