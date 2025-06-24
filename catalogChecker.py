import csv
import sys
import requests
from datetime import datetime
import re

# コマンドライン引数からファイル名を取得
filename = sys.argv[1]

# 確認結果を格納するリスト
resultList = []

# 画像URLの確認を行う関数
def check_url_status(url):
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False
# Unix時間をタイムスタンプ形式に変換する関数
def unixtime_to_timestamp(unixtime):
    # Unix時間をdatetimeオブジェクトに変換
    dt = datetime.fromtimestamp(unixtime)
    # タイムスタンプ形式（例: '2023-01-01 12:00:00'）にフォーマット
    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


# 指定されたCSVファイルを開き、idカラムに空白があるかチェック
with open(filename, mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    # 日付の確認 YYYY-MM-DDの形式になっているかを確認する
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')

    for row in csv_reader:
        # idに空白がないか
        if not row['id'].strip():
            resultList.append("クーポン名:" + row['couponName'] + "はidが空白になっています")

        # couponNameに空白がないか
        if not row['couponName'].strip():
            resultList.append("クーポンID:" + row['id'] + "はクーポン名が空白になっています")

        # couponDescriptionに空白がないか
        if not row['couponDescription'].strip():
            resultList.append("クーポンID:" + row['id'] + "はクーポン説明が空白になっています")

        # imageUrlが正しいものになっているか
        if not 'stage' in row['id']:
            if not row['imageUrl'].strip():
               resultList.append("クーポンID:" + row['id'] + "は画像URLが空白になっています")
            if not check_url_status(row['imageUrl']):
               resultList.append("クーポンID:" + row['id'] + "の画像URLが無効です")
        
        # startDateTime, endDateTime, startDate, expiryDateに半角スペースと全角スペースが含まれていないか
        if " " in row['startDateTime']:
            resultList.append("クーポンID:" + row['id'] + "のstartDateTimeに半角スペースが含まれています")
        if " " in row['endDateTime']:
            resultList.append("クーポンID:" + row['id'] + "のendDateTimeに半角スペースが含まれています")
        if " " in row['startDate']:
            resultList.append("クーポンID:" + row['id'] + "のstartDateに半角スペースが含まれています")
        if " " in row['expiryDate']:
            resultList.append("クーポンID:" + row['id'] + "のexpiryDateに半角スペースが含まれています")
        if "　" in row['startDateTime']:
            resultList.append("クーポンID:" + row['id'] + "のstartDateTimeに全角スペースが含まれています")
        if "　" in row['endDateTime']:
            resultList.append("クーポンID:" + row['id'] + "のendDateTimeに全角スペースが含まれています")
        if "　" in row['startDate']:
            resultList.append("クーポンID:" + row['id'] + "のstartDateに全角スペースが含まれています")
        if "　" in row['expiryDate']:
            resultList.append("クーポンID:" + row['id'] + "のexpiryDateに全角スペースが含まれています")


        # 対象クーポンのstartDateTime, endDateTime, startDate, expiryDateの空白がないか
        if row['promotionId'].strip() and 'stage' in row['promotionId']:
            if not row['startDateTime'] or not row['endDateTime'] or not row['startDate'] or not row['expiryDate']:
                resultList.append("クーポンID:" + row['id'] + "のstartDateTime, endDateTime, startDate, expiryDateのいずれか1つ以上空白になっています")
            
        # startDateTime, endDateTime, startDate, expiryDateのフォーマットチェックを行う
        if resultList == [] and row['startDateTime'] and row['endDateTime'] and row['startDate'] and row['expiryDate']:
            # startDate, expiryDateがYYYY-MM-DDの形式になっているか
            if not date_pattern.match(row['startDate']):
                resultList.append("クーポンID:" + row['id'] + "のstartDateがYYYY-MM-DDの形式になっていません")
            if not date_pattern.match(row['expiryDate']):
                resultList.append("クーポンID:" + row['id'] + "のexpiryDateがYYYY-MM-DDの形式になっていません")
            # startDateTimeがendDateTimeより後の日付になっていないか
            if row['startDateTime'].isdigit() and row['endDateTime'].isdigit():
               if int(row['startDateTime']) > int(row['endDateTime']):
                   resultList.append("クーポンID:" + row['id'] + "のstartDateTimeがendDateTimeより後の日付になっています")
            # startDateがexpiryDateより後の日付になっていないか
            if date_pattern.match(row['startDate']) and date_pattern.match(row['expiryDate']):
                start_date_str = row['startDate']
                expiry_date_str = row['expiryDate']
                if start_date_str and expiry_date_str:  # Ensure both dates are not empty
                   start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                   expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
                   if start_date > expiry_date:
                      resultList.append("クーポンID:" + row['id'] + "のstartDateがexpiryDateより後の日付になっています")
        
        # (空白以外で)expiredDateとendDateTimeの値が同一であるか
        if row['expiredDate'].strip() and row['endDateTime'].strip():
            if row['expiredDate'] != row['endDateTime']:
                resultList.append("クーポンID:" + row['id'] + "のexpiredDateとendDateTimeが同一ではありません")
        
        # (空白以外で)startDateTimeとstartDateは同一の日付であるか
        if row['startDateTime'].strip() and row['startDate'].strip():
            start_datetime = row['startDateTime']
            start_datetime_timestamp = unixtime_to_timestamp(int(start_datetime))
            start_date = row['startDate']
            # start_datetime_timestampから日付のみを取得
            start_datetime_timestamp = start_datetime_timestamp.split(' ')[0]
            if start_datetime_timestamp != start_date:
                resultList.append("クーポンID:" + row['id'] + "のstartDateTimeとstartDateが同一の日付ではありません")

        # (空白以外で)endDateTimeとexpiryDateは同一の日付であるか
        if row['endDateTime'].strip() and row['expiryDate'].strip():
            end_datetime = row['endDateTime']
            end_datetime_timestamp = unixtime_to_timestamp(int(end_datetime))
            expiry_date = row['expiryDate']
            # end_datetime_timestampから日付のみを取得
            end_datetime_timestamp = end_datetime_timestamp.split(' ')[0]
            if end_datetime_timestamp != expiry_date:
                resultList.append("クーポンID:" + row['id'] + "のendDateTimeとexpiryDateが同一の日付ではありません")

        # (空白以外で)couponCodeの文字列がpromotionIdに含まれているか
        if row['couponCode'].strip() and row['promotionId'].strip():
            if row['couponCode'] not in row['promotionId']:
                resultList.append("クーポンID:" + row['id'] + "のcouponCodeがpromotionIdに含まれていません")
        
        # (normalPrice/discountPriceが空白の場合もあるので以下は機能を無効化)
        # # (有効なクーポンにおいて)normalPriceが空白でないか
        # if row['couponDescription'] != '-':
        #     if row['normalPrice'] == "":
        #         resultList.append("クーポンID:" + row['id'] + "のnormalPriceが空白です")
        
        # # (有効なクーポンにおいて)discountPriceが空白でないか
        # if row['couponDescription'] != '-':
        #     if row['discountPrice'] == "":
        #         resultList.append("クーポンID:" + row['id'] + "のdiscountPriceが空白です")

        # # (有効なクーポンにおいて)discountPriceがnormalPriceより大きくなっていないか
        # if row['couponDescription'] != '-':
        #     int_discountPrice = int(row['discountPrice'])
        #     int_normalPrice = int(row['normalPrice'])
        #     if int_discountPrice > int_normalPrice:
        #         resultList.append("クーポンID:" + row['id'] + "のdiscountPriceがnormalPriceより大きいです")

        # (有効なクーポンにおいて)contentCardCategoryがcouponとなっているか
        if row['couponDescription'] != '-':
            if row['contentCardCategory'] != 'coupon':
                resultList.append("クーポンID:" + row['id'] + "のcontentCardCategoryがcouponではありません")

        # (Stageクーポン以外で)promotionIdの中にidと同じ文字列があるか 
        if 'stage' not in row['promotionId'] and row['id'].strip() and row['promotionId'].strip():
            if not row['id'] in row['promotionId']:
                resultList.append("クーポンID:" + row['id'] + "のpromotionIdにクーポンIDが含まれていません")

        # (Stageクーポンで)promotionIdの中にidと同じステージ情報があるか
        if 'stage' in row['promotionId'] and row['id'].strip() and row['promotionId'].strip():
            # row['id']を_区切りで分割して最後の要素を削除し、それがrow['promotionId']に含まれていないか確認
            splitRowId = row['id'].split('_')
            formatId = splitRowId[0] + "_" + splitRowId[1]
            if formatId not in row['promotionId']:
                resultList.append("クーポンID:" + row['id'] + "のpromotionIdにステージ情報が含まれていません")
        
        # (10000マイルクーポン、アンケートサンクスクーポン、会員登録サンクスクーポン、購入サンクスクーポンにおいて)couopnTypeがcontentsCardとなっているか
        if 'miles' in row['id'] or 'survey_thanks' in row['id'] or 'registration_thanks' in row['id'] or 'purchase_thanks' in row['id']:
            if row['couponType'] != 'contentsCard':
                resultList.append("クーポンID:" + row['id'] + "のcouponTypeがcontentsCardではありません")


# カタログの確認結果を出力
if len(resultList) == 0:
    print("====== カタログ確認結果 ======")
    print("カタログは正常に記入されています")
else:
    print("====== カタログ確認結果 ======")
    print("以下の項目で異常を検知しました。各項目を確認してください。")
    for row in resultList:
        print("・" + row)
