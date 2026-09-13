from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
import json
from pydantic import BaseModel
import jwt
import requests
import os
from datetime import datetime, timedelta, timezone
app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# JWT 設定
SECRET_KEY = "taipei-day-trip-secret-key"
ALGORITHM = "HS256"

PARTNER_KEY = os.getenv("TAPPAY_PARTNER_KEY")
MERCHANT_ID = "tppf_irenehsu_GP_POS_1"

TAPPAY_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"

# ==================================================================
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
# 會員註冊資料格式
class UserSignup(BaseModel):
	name: str
	email: str
	password: str

# 會員登入資料格式
class UserSignin(BaseModel):
	email: str
	password: str

# 預定行程資料格式
class BookingCreate(BaseModel):
	attractionId: int
	date: str
	time: str
	price: int

# 訂單景點資料格式
class OrderAttraction(BaseModel):
	id: int
	name: str
	address: str
	image: str

# 訂單行程資料格式
class OrderTrip(BaseModel):
	attraction: OrderAttraction
	date: str
	time: str

# 訂單聯絡人資料格式
class OrderContact(BaseModel):
	name: str
	email: str
	phone: str

# 訂單內容資料格式
class OrderData(BaseModel):
	price: int
	trip: OrderTrip
	contact: OrderContact

# 建立訂單資料格式
class OrderCreate(BaseModel):
	prime: str
	order: OrderData

# ==================================================================
# API：註冊一個新的會員
@app.post("/api/user")
async def signup(user: UserSignup):

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

		# dictionary=True 讓查詢結果可以用欄位名稱存取
		cursor = connection.cursor(dictionary=True)

		# 檢查 Email 是否已經註冊過
		cursor.execute("""
			SELECT id
			FROM users
			WHERE email = %s
		""", (user.email,))

		# 取得查詢結果
		existing_user = cursor.fetchone()

		# 如果 Email 已經存在，回傳 HTTP 400
		if existing_user is not None:
			return JSONResponse(
				status_code=400,
				content={
					"error": True,
					"message": "註冊失敗，重複的 Email 或其他原因"
				}
			)

		# 將新會員資料新增到 users 資料表
		cursor.execute("""
			INSERT INTO users (name, email, password)
			VALUES (%s, %s, %s)
		""", (user.name, user.email, user.password))

		# 儲存資料庫的變更
		connection.commit()

		# 新會員註冊成功，回傳 HTTP 200
		return {
			"ok": True
		}

	except Exception as error:
		# 在終端機顯示實際錯誤，方便開發時除錯
		print(error)

		# 資料庫連線或操作失敗時，回傳 HTTP 500
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
# API：登入會員帳戶
@app.put("/api/user/auth")
async def signin(user: UserSignin):

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

		# dictionary=True 讓查詢結果可以用欄位名稱存取
		cursor = connection.cursor(dictionary=True)

		# 根據 Email 和密碼查詢會員資料
		cursor.execute("""
			SELECT id, name, email
			FROM users
			WHERE email = %s AND password = %s
		""", (user.email, user.password))

		# 取得查詢結果
		member = cursor.fetchone()

		# 如果找不到符合的會員資料，代表 Email 或密碼錯誤
		if member is None:
			return JSONResponse(
				status_code=400,
				content={
					"error": True,
					"message": "登入失敗，帳號或密碼錯誤或其他原因"
				}
			)

		# 設定 Token 內容，包含會員資料與 7 天後的到期時間
		payload = {
			"id": member["id"],
			"name": member["name"],
			"email": member["email"],
			"exp": datetime.now(timezone.utc) + timedelta(days=7)
		}

		# 使用 JWT 將會員資料編碼成 Token
		token = jwt.encode(
			payload,
			SECRET_KEY,
			algorithm=ALGORITHM
		)

		# 登入成功，回傳 JWT Token
		return {
			"token": token
		}
		
	except Exception as error:
		# 在終端機顯示實際錯誤，方便開發時除錯
		print(error)

		# 資料庫連線或操作失敗時，回傳 HTTP 500
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
# API：取得當前登入的會員資訊
@app.get("/api/user/auth")
async def get_current_user(authorization: str | None = Header(default=None)):

	# 如果沒有 Authorization Header，代表目前未登入
	if authorization is None:
		return {
			"data": None
		}

	# 如果 Authorization Header 不是以 Bearer 開頭，代表 Token 格式不正確
	if not authorization.startswith("Bearer "):
		return {
			"data": None
		}

	# 移除 Bearer 前綴，取得真正的 JWT Token
	token = authorization.replace("Bearer ", "", 1)

	try:
		# 使用 JWT 解碼並驗證 Token
		payload = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM]
		)

		# Token 驗證成功，回傳目前登入的會員資料
		return {
			"data": {
				"id": payload["id"],
				"name": payload["name"],
				"email": payload["email"]
			}
		}

	except Exception as error:
		# Token 驗證失敗、格式錯誤或已過期時，視為未登入
		print(error)

		return {
			"data": None
		}

# ==================================================================
# API：建立新的預定行程
@app.post("/api/booking")
async def create_booking(
	booking: BookingCreate,
	authorization: str | None = Header(default=None)
):
	# 如果沒有 Authorization Header，代表目前未登入
	if authorization is None:
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# Authorization Header 必須以 Bearer 開頭
	if not authorization.startswith("Bearer "):
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# 移除 Bearer 前綴，取得 JWT Token
	token = authorization.replace("Bearer ", "", 1)

	try:
		# 解碼並驗證 JWT Token
		payload = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM]
		)

		# 從 Token 取得目前登入會員的 id
		user_id = payload["id"]

	except Exception as error:
		print(error)

		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# 檢查輸入資料是否正確
	if (
		booking.attractionId <= 0
		or not booking.date
		or booking.time not in ["morning", "afternoon"]
		or booking.price <= 0
	):
		return JSONResponse(
			status_code=400,
			content={
				"error": True,
				"message": "建立失敗，輸入不正確或其他原因"
			}
		)

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

		# 檢查景點是否存在
		cursor.execute("""
			SELECT id
			FROM attractions
			WHERE id = %s
		""", (booking.attractionId,))

		attraction = cursor.fetchone()

		if attraction is None:
			return JSONResponse(
				status_code=400,
				content={
					"error": True,
					"message": "建立失敗，輸入不正確或其他原因"
				}
			)

		# 刪除目前會員原本的預定行程
		cursor.execute("""
			DELETE FROM bookings
			WHERE user_id = %s
		""", (user_id,))

		# 建立新的預定行程
		cursor.execute("""
			INSERT INTO bookings (
				user_id,
				attraction_id,
				date,
				time,
				price
			)
			VALUES (%s, %s, %s, %s, %s)
		""", (
			user_id,
			booking.attractionId,
			booking.date,
			booking.time,
			booking.price
		))

		# 儲存資料庫變更
		connection.commit()

		return {
			"ok": True
		}

	except Exception as error:
		print(error)

		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)

	finally:
		if cursor is not None:
			cursor.close()

		if connection is not None and connection.is_connected():
			connection.close()

# ==================================================================
# API：取得目前的預定行程
@app.get("/api/booking")
async def get_booking(
	authorization: str | None = Header(default=None)
):
	# 如果沒有 Authorization Header，代表目前未登入
	if authorization is None:
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# Authorization Header 必須以 Bearer 開頭
	if not authorization.startswith("Bearer "):
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# 移除 Bearer 前綴，取得 JWT Token
	token = authorization.replace("Bearer ", "", 1)

	try:
		# 解碼並驗證 JWT Token
		payload = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM]
		)

		# 從 Token 取得目前登入會員的 id
		user_id = payload["id"]

	except Exception as error:
		print(error)

		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

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

		cursor = connection.cursor(dictionary=True)

		# 查詢目前會員的預定行程，並取得景點資料
		cursor.execute("""
			SELECT
				b.attraction_id,
				b.date,
				b.time,
				b.price,
				a.name,
				a.address,
				a.images
			FROM bookings AS b
			JOIN attractions AS a
				ON b.attraction_id = a.id
			WHERE b.user_id = %s
		""", (user_id,))

		booking = cursor.fetchone()

		# 如果目前沒有預定行程，回傳 data: null
		if booking is None:
			return {
				"data": None
			}

		# 將景點圖片 JSON 字串轉成 list
		images = json.loads(booking["images"])

		# 取第一張圖片
		image = images[0] if len(images) > 0 else None

		# 回傳預定行程資料
		return {
			"data": {
				"attraction": {
					"id": booking["attraction_id"],
					"name": booking["name"],
					"address": booking["address"],
					"image": image
				},
				"date": booking["date"].strftime("%Y-%m-%d"),
				"time": booking["time"],
				"price": booking["price"]
			}
		}

	except Exception as error:
		print(error)

		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)

	finally:
		if cursor is not None:
			cursor.close()

		if connection is not None and connection.is_connected():
			connection.close()

# ==================================================================
# API：刪除目前的預定行程
@app.delete("/api/booking")
async def delete_booking(
	authorization: str | None = Header(default=None)
):
	# 如果沒有 Authorization Header，代表目前未登入
	if authorization is None:
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# Authorization Header 必須以 Bearer 開頭
	if not authorization.startswith("Bearer "):
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# 移除 Bearer 前綴，取得 JWT Token
	token = authorization.replace("Bearer ", "", 1)

	try:
		# 解碼並驗證 JWT Token
		payload = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM]
		)

		# 從 Token 取得目前登入會員的 id
		user_id = payload["id"]

	except Exception as error:
		print(error)

		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

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

		# 刪除目前會員的預定行程
		cursor.execute("""
			DELETE FROM bookings
			WHERE user_id = %s
		""", (user_id,))

		# 儲存資料庫變更
		connection.commit()

		return {
			"ok": True
		}

	except Exception as error:
		print(error)

		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)

	finally:
		if cursor is not None:
			cursor.close()

		if connection is not None and connection.is_connected():
			connection.close()
	
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

# ==================================================================
# API：建立新的訂單，並完成付款程序
@app.post("/api/orders")
async def create_order(
	order: OrderCreate,
	authorization: str | None = Header(default=None)
):
	# 如果沒有 Authorization Header，代表目前未登入
	if authorization is None:
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# Authorization Header 必須以 Bearer 開頭
	if not authorization.startswith("Bearer "):
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# 移除 Bearer 前綴，取得 JWT Token
	token = authorization.replace("Bearer ", "", 1)

	try:
		# 解碼並驗證 JWT Token
		payload = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM]
		)

		# 從 Token 取得目前登入會員的 id
		user_id = payload["id"]

	except Exception as error:
		print(error)

		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# 檢查輸入資料是否正確
	if (
		order.order.price <= 0
		or order.order.trip.attraction.id <= 0
		or not order.order.trip.date
		or order.order.trip.time not in ["morning", "afternoon"]
		or not order.order.contact.name
		or not order.order.contact.email
		or not order.order.contact.phone
		or not order.prime
	):
		return JSONResponse(
			status_code=400,
			content={
				"error": True,
				"message": "訂單建立失敗，輸入不正確或其他原因"
			}
		)

	# 產生訂單編號
	order_number = datetime.now().strftime("%Y%m%d%H%M%S%f")

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

		# 將訂單資料寫入 orders 資料表
		cursor.execute(
			"""
			INSERT INTO orders (
				number,
				user_id,
				attraction_id,
				date,
				time,
				price,
				contact_name,
				contact_email,
				contact_phone,
				status
			)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			""",
			(
				order_number,
				user_id,
				order.order.trip.attraction.id,
				order.order.trip.date,
				order.order.trip.time,
				order.order.price,
				order.order.contact.name,
				order.order.contact.email,
				order.order.contact.phone,
				0
			)
		)

		# 取得剛建立訂單的 id
		order_id = cursor.lastrowid

		connection.commit()

		# TapPay API Header
		headers = {
			"Content-Type": "application/json",
			"x-api-key": PARTNER_KEY
		}

		# TapPay Pay By Prime 付款資料
		payment_data = {
			"prime": order.prime,
			"partner_key": PARTNER_KEY,
			"merchant_id": MERCHANT_ID,
			"details": "Taipei Day Trip",
			"amount": order.order.price,
			"cardholder": {
				"phone_number": order.order.contact.phone,
				"name": order.order.contact.name,
				"email": order.order.contact.email
			},
			"remember": False
		}

		# 呼叫 TapPay Pay By Prime API
		response = requests.post(
			TAPPAY_URL,
			headers=headers,
			json=payment_data
		)

		# 將 TapPay 回傳的 JSON 轉成 Python dictionary
		payment_result = response.json()

		# 取得 TapPay 付款結果
		payment_status = payment_result["status"]
		payment_message = payment_result["msg"]

		# 將付款結果寫入 payments 資料表
		cursor.execute("""
			INSERT INTO payments (
				order_id,
				status,
				message
			)
			VALUES (%s, %s, %s)
		""", (
			order_id,
			payment_status,
			payment_message
		))

		connection.commit()

		# 如果付款成功，將訂單狀態更新為已付款
		if payment_status == 0:
			cursor.execute("""
				UPDATE orders
				SET status = 1
				WHERE id = %s
			""", (order_id,))

			# 刪除目前會員的預定行程
			cursor.execute("""
				DELETE FROM bookings
				WHERE user_id = %s
			""", (user_id,))

			connection.commit()

		# 回傳訂單編號與付款結果
		return {
			"data": {
				"number": order_number,
				"payment": {
					"status": payment_status,
					"message": "付款成功" if payment_status == 0 else "付款失敗"
				}
			}
		}

	except Exception as error:
		print(error)
	
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)
	
	finally:
		if cursor is not None:
			cursor.close()

		if connection is not None and connection.is_connected():
			connection.close()

# ==================================================================
# API：根據訂單編號取得訂單資訊
@app.get("/api/order/{orderNumber}")
async def get_order(
	orderNumber: str,
	authorization: str | None = Header(default=None)
):
	# 如果沒有 Authorization Header，代表目前未登入
	if authorization is None:
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# Authorization Header 必須以 Bearer 開頭
	if not authorization.startswith("Bearer "):
		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

	# 移除 Bearer 前綴，取得 JWT Token
	token = authorization.replace("Bearer ", "", 1)

	try:
		# 解碼並驗證 JWT Token
		payload = jwt.decode(
			token,
			SECRET_KEY,
			algorithms=[ALGORITHM]
		)

		# 從 Token 取得目前登入會員的 id
		user_id = payload["id"]

	except Exception as error:
		print(error)

		return JSONResponse(
			status_code=403,
			content={
				"error": True,
				"message": "未登入系統，拒絕存取"
			}
		)

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

		cursor = connection.cursor(dictionary=True)

		# 根據訂單編號查詢目前會員的訂單資料
		cursor.execute("""
			SELECT
				o.number,
				o.price,
				o.date,
				o.time,
				o.contact_name,
				o.contact_email,
				o.contact_phone,
				o.status,
				a.id AS attraction_id,
				a.name AS attraction_name,
				a.address AS attraction_address,
				a.images
			FROM orders AS o
			JOIN attractions AS a
				ON o.attraction_id = a.id
			WHERE o.number = %s
			  AND o.user_id = %s
		""", (
			orderNumber,
			user_id
		))

		order_data = cursor.fetchone()

		# 如果查不到訂單，回傳 data: null
		if order_data is None:
			return {
				"data": None
			}

		# 將景點圖片 JSON 字串轉成 list
		images = json.loads(order_data["images"])

		# 取第一張圖片
		image = images[0] if len(images) > 0 else None

		return {
			"data": {
				"number": order_data["number"],
				"price": order_data["price"],
				"trip": {
					"attraction": {
						"id": order_data["attraction_id"],
						"name": order_data["attraction_name"],
						"address": order_data["attraction_address"],
						"image": image
					},
					"date": order_data["date"].strftime("%Y-%m-%d"),
					"time": order_data["time"]
				},
				"contact": {
					"name": order_data["contact_name"],
					"email": order_data["contact_email"],
					"phone": order_data["contact_phone"]
				},
				"status": order_data["status"]
			}
		}

	except Exception as error:
		print(error)

		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": "伺服器內部錯誤"
			}
		)

	finally:
		if cursor is not None:
			cursor.close()

		if connection is not None and connection.is_connected():
			connection.close()