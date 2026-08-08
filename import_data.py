import json
import re
import mysql.connector

# 連接 MySQL 資料庫

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="taipei_day_trip"
)

cursor = connection.cursor()

# 讀取景點 JSON 資料
with open("data/taipei-attractions.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# 取得圖片網址主機
img_host = data["img_host"]

# 新增景點資料的 SQL 指令
sql = """
    INSERT INTO attractions (
        id,
        name,
        category,
        description,
        address,
        transport,
        mrt,
        lat,
        lng,
        images,
        rate,
        date,
        ref_wp,
        av_begin,
        av_end,
        langinfo,
        serial_no,
        row_num,
        memo_time,
        poi,
        idpt
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s
    )
    """

# 逐筆處理景點資料
for attraction in data["list"]:

    # 取得景點基本資料
    attraction_id = attraction["_id"]
    name = attraction["name"]
    category = attraction["CAT"]
    description = attraction["description"]
    address = attraction["address"]
    transport = attraction["direction"]
    mrt = attraction["MRT"]
    lat = float(attraction["latitude"])
    lng = float(attraction["longitude"])
    imgurls = attraction["imgurls"]
    # 取得其他景點資訊
    rate = attraction["rate"]
    date = attraction["date"]
    ref_wp = attraction["REF_WP"]
    av_begin = attraction["avBegin"]
    av_end = attraction["avEnd"]
    langinfo = attraction["langinfo"]
    serial_no = attraction["SERIAL_NO"]
    row_num = attraction["RowNumber"]
    memo_time = attraction["MEMO_TIME"]
    poi = attraction["POI"]
    idpt = attraction["idpt"]

    # 擷取所有圖片路徑
    image_paths = re.findall(r"/imgs/.*?\.jpg", imgurls)
    # 組合完整圖片網址
    images = [img_host + image for image in image_paths]
    
    # 要新增至資料庫的資料
    values = (
        attraction_id,
        name,
        category,
        description,
        address,
        transport,
        mrt,
        lat,
        lng,
        json.dumps(images),
        rate,
        date,
        ref_wp,
        av_begin,
        av_end,
        langinfo,
        serial_no,
        row_num,
        memo_time,
        poi,
        idpt
    )

    # 執行新增資料
    cursor.execute(sql, values)

# 儲存所有變更
connection.commit()
print(f"資料匯入完成，共匯入 {len(data['list'])} 筆")

# 關閉資料庫連線
cursor.close()
connection.close()