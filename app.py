from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
import json
app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

# ==================================================================
# API：取得景點資料(取得不同分頁的旅遊景點列表資料，也可以根據標題關鍵字、或捷運站名稱篩選)
@app.get("/api/attractions")
async def get_attractions(
    page: int,
    category: str | None = None,
    keyword: str | None = None
):
	# 預先設定為 None，避免資料庫連線失敗時無法執行 finally
	connection = None
	cursor = None

	try:
		# 連接 MySQL 資料庫
		connection = mysql.connector.connect(
			host="localhost",
			user="root",
			password="123456",
			database="taipei_day_trip"
		)

		# dictionary=True 讓查詢結果以欄位名稱存取
		cursor = connection.cursor(dictionary=True)

		# 每頁顯示 8 筆景點
		page_size = 8

		# 根據目前頁數計算要跳過幾筆資料
        # page=0 時跳過 0 筆，page=1 時跳過 8 筆
		offset = page * page_size

		# 建立查詢條件與對應的參數
		conditions = []
		parameters = []

		# category 有提供時，完全比對景點分類
		if category is not None:
			conditions.append("category = %s")
			parameters.append(category)

        # keyword 有提供時：
        # 完全比對捷運站名稱，或模糊比對景點名稱
		if keyword is not None:
			conditions.append("(mrt = %s OR name LIKE %s)")
			parameters.append(keyword)
			parameters.append(f"%{keyword}%")

		# 建立景點查詢的基本 SQL
		sql = """
			SELECT
				id,
				name,
				category,
				description,
				address,
				transport,
				mrt,
				lat,
				lng,
				images
			FROM attractions
		"""

		# 有 category 或 keyword 條件時，加入 WHERE
		if conditions:
			sql += " WHERE " + " AND ".join(conditions)

		# 依景點編號排序，讓每次分頁取得的順序固定
		sql += " ORDER BY id"

		# 多查 1 筆，用來判斷是否還有下一頁
		sql += " LIMIT %s OFFSET %s"

		parameters.append(page_size + 1)
		parameters.append(offset)

		# 執行 SQL 查詢
		cursor.execute(sql, tuple(parameters))

		# 取得所有查詢結果
		attractions = cursor.fetchall()

		# 如果查到超過 8 筆，代表後面還有下一頁
		if len(attractions) > page_size:
			next_page = page + 1

			# API 每頁只回傳前 8 筆
			attractions = attractions[:page_size]
		else:
			# 沒有下一頁時，Python 的 None 會轉成 JSON 的 null
			next_page = None

		# 整理每一筆景點的資料型態
		for attraction in attractions:
			# 將資料庫中的 JSON 字串轉回 Python list
			attraction["images"] = json.loads(attraction["images"])

			# 將 MySQL DECIMAL 轉成 Python float，符合 API 規格
			attraction["lat"] = float(attraction["lat"])
			attraction["lng"] = float(attraction["lng"])

		# 正常回傳時，FastAPI 會自動使用 HTTP 200
		return {
			"nextPage": next_page,
			"data": attractions
		}

	except Exception as error:
		# 在終端機顯示實際錯誤，方便開發時除錯
		print(error)

		# 資料庫連線或查詢失敗時，回傳 HTTP 500
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)

	finally:
		# 無論 API 正常或發生錯誤，都要關閉 cursor
		if cursor is not None:
			cursor.close()

		# 確認資料庫連線已建立且仍保持連線，再將它關閉
		if connection is not None and connection.is_connected():
			connection.close()

# ==================================================================
# API：根據景點編號取得景點資料
@app.get("/api/attraction/{attractionId}")
async def get_attraction(
	attractionId: int
):

	# 預先設定為 None，避免資料庫連線失敗時無法執行 finally
	connection = None
	cursor = None

	try:
		# 連接 MySQL 資料庫
		connection = mysql.connector.connect(
			host="localhost",
			user="root",
			password="123456",
			database="taipei_day_trip"
		)

		# dictionary=True 讓查詢結果以欄位名稱存取
		cursor = connection.cursor(dictionary=True)

		# 根據景點編號查詢單一景點
		cursor.execute("""
            SELECT
                id,
                name,
                category,
                description,
                address,
                transport,
                mrt,
                lat,
                lng,
                images
            FROM attractions
            WHERE id = %s
        """, (attractionId,))

		# 只取得一筆查詢結果
		attraction = cursor.fetchone()

        # 查不到景點時，回傳 HTTP 400
		if attraction is None:
			return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "景點編號不正確"
                }
            )

        # 將資料庫中的 JSON 字串轉回 Python list
		attraction["images"] = json.loads(attraction["images"])

        # 將 MySQL DECIMAL 轉成 Python float，符合 API 規格
		attraction["lat"] = float(attraction["lat"])
		attraction["lng"] = float(attraction["lng"])

		# 正常回傳時，FastAPI 會自動使用 HTTP 200
		return {
            "data": attraction
        }

	except Exception as error:
		# 在終端機顯示實際錯誤，方便開發時除錯
		print(error)
	
		# 資料庫連線或查詢失敗時，回傳 HTTP 500
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)
	
	finally:
		# 無論 API 正常或發生錯誤，都要關閉 cursor
		if cursor is not None:
			cursor.close()

		# 確認資料庫連線已建立且仍保持連線，再將它關閉
		if connection is not None and connection.is_connected():
			connection.close()

# ==================================================================
# API：取得所有的景點分類名稱列表
@app.get("/api/categories")
async def get_categories():

	# 預先設定為 None，避免資料庫連線失敗時無法執行 finally
	connection = None
	cursor = None

	try:
		# 連接 MySQL 資料庫
		connection = mysql.connector.connect(
			host="localhost",
			user="root",
			password="123456",
			database="taipei_day_trip"
		)

		cursor = connection.cursor()

		# 查詢所有不重複的景點分類
		cursor.execute("""
			SELECT DISTINCT category
			FROM attractions
		""")

		# 取得查詢結果，將 fetchall() 回傳的 tuple 轉成分類名稱列表
		result = cursor.fetchall()
		categories = [row[0] for row in result]

		# 正常回傳時，FastAPI 會自動使用 HTTP 200
		return {
			"data": categories
		}

	except Exception as error:
		# 在終端機顯示實際錯誤，方便開發時除錯
		print(error)

		# 資料庫連線或查詢失敗時，回傳 HTTP 500
		return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "伺服器內部錯誤"
            }
        )

	finally:
		# 無論 API 正常或發生錯誤，都要關閉 cursor
		if cursor is not None:
			cursor.close()

        # 確認資料庫連線已建立且仍保持連線，再將它關閉
		if connection is not None and connection.is_connected():
			connection.close()

		
# ==================================================================
# API：取得所有捷運站名稱列表，按照週邊景點的數量由大到小排序
@app.get("/api/mrts")
async def get_mrts():

	# 預先設定為 None，避免資料庫連線失敗時無法執行 finally
	connection = None
	cursor = None

	try:
		# 連接 MySQL 資料庫
		connection = mysql.connector.connect(
			host="localhost",
			user="root",
			password="123456",
			database="taipei_day_trip"
		)

		cursor = connection.cursor()

		# 取得所有捷運站，並依周邊景點數量由多到少排序
		cursor.execute("""
			SELECT mrt
			FROM attractions
			WHERE mrt IS NOT NULL
			GROUP BY mrt
			ORDER BY COUNT(*) DESC
		""")

		# 取得查詢結果，將 fetchall() 回傳的 tuple 轉成捷運站名稱列表
		result = cursor.fetchall()
		mrts = [row[0] for row in result]

		# 正常回傳時，FastAPI 會自動使用 HTTP 200
		return {
			"data": mrts
		}

	except Exception as error:
		# 在終端機顯示實際錯誤，方便開發時除錯
		print(error)

		# 資料庫連線或查詢失敗時，回傳 HTTP 500
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)

	finally:
		# 無論 API 正常或發生錯誤，都要關閉 cursor
		if cursor is not None:
			cursor.close()

		# 確認資料庫連線已建立且仍保持連線，再將它關閉
		if connection is not None and connection.is_connected():
			connection.close()