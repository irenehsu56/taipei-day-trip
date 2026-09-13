// 初始化 TapPay SDK
TPDirect.setupSDK(
    171069,
    "app_5D1YKFZdnlNHBR6eZ2mcYR2aQw0Co7Sl76C1hNOvUSowpu921cNUbU8C772x",
    "sandbox"
);

// 設定 TapPay 信用卡輸入欄位
TPDirect.card.setup({
    fields: {
        number: {
            element: "#card-number",
            placeholder: "**** **** **** ****"
        },
        expirationDate: {
            element: "#card-expiration",
            placeholder: "MM / YY"
        },
        ccv: {
            element: "#card-ccv",
            placeholder: "CVV"
        }
    },
    styles: {
        "input": {
            "color": "#000000",
            "font-size": "16px"
        },
        "input::placeholder": {
            "color": "#757575"
        },
        ":focus": {
            "color": "#000000"
        },
        ".valid": {
            "color": "green"
        },
        ".invalid": {
            "color": "red"
        }
    }
});

// 取得會員姓名
const bookingMemberName = document.querySelector("#booking-member-name");
// 取得沒有預定行程時顯示的區塊
const bookingEmptyState = document.querySelector(".booking-empty-state");
// 取得有預定行程時顯示的區塊
const bookingSection = document.querySelector(".booking-section");

// 取得景點圖片
const bookingAttractionImage = document.querySelector("#booking-attraction-image");
// 取得景點名稱
const bookingAttractionName = document.querySelector("#booking-attraction-name");
// 取得預定日期
const bookingDate = document.querySelector("#booking-date");
// 取得預定時間
const bookingTime = document.querySelector("#booking-time");
// 取得預定費用
const bookingPrice = document.querySelector("#booking-price");
// 取得景點地址
const bookingAddress = document.querySelector("#booking-address");
// 取得刪除預定按鈕
const bookingDeleteButton = document.querySelector("#booking-delete-button");

// 取得聯絡姓名輸入框
const contactName = document.querySelector("#contact-name");
// 取得聯絡信箱輸入框
const contactEmail = document.querySelector("#contact-email");
// 取得聯絡電話輸入框
const contactPhone = document.querySelector("#contact-phone");
// 取得總價
const confirmPrice = document.querySelector("#confirm-price");
// 取得所有分隔線
const mainSeparators = document.querySelectorAll(".main-separator");
// 取得聯絡資訊區塊
const contactForm = document.querySelector(".contact-form");
// 取得付款資訊區塊
const payment = document.querySelector(".payment");
// 取得確認付款區塊
const confirmSection = document.querySelector(".confirm");
// 取得確認訂購並付款按鈕
const confirmButton = document.querySelector("#confirm-button");

// 儲存目前的預定行程資料
let currentBooking = null;

// ===========================================================
// 取得目前登入的會員資訊
async function getMember() {
    // 從 LocalStorage 取得 JWT Token
    const token = localStorage.getItem("token");

    // 呼叫後端 API：取得目前登入的會員資訊
    const response = await fetch("/api/user/auth", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    // 將 API 回傳資料轉成 JavaScript 物件
    const result = await response.json();

    // 如果目前沒有登入會員
    if (result.data === null) {
        // 導回首頁
        window.location.href = "/";
        return false;
    }

    // 將會員姓名顯示在預定頁面標題
    bookingMemberName.textContent = result.data.name;
    // 將會員姓名帶入聯絡姓名
    contactName.value = result.data.name;
    // 將會員 Email 帶入聯絡信箱
    contactEmail.value = result.data.email;

    // 代表目前會員已登入
    return true;
}

// ===========================================================
// 取得目前的預定行程
async function getBooking() {
    // 從 LocalStorage 取得 JWT Token
    const token = localStorage.getItem("token");

    // 呼叫後端 API：取得目前的預定行程
    const response = await fetch("/api/booking", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    // 如果 API 回傳失敗，就停止執行
    if (!response.ok) {
        return;
    }

    // 將 API 回傳資料轉成 JavaScript 物件
    const result = await response.json();

    // 如果目前沒有預定行程
    if (result.data === null) {
        // 顯示沒有預定行程的文字
        bookingEmptyState.style.display = "flex";

        // 隱藏預定行程內容
        bookingSection.style.display = "none";
        // 隱藏聯絡資訊
        contactForm.style.display = "none";
        // 隱藏付款資訊
        payment.style.display = "none";
        // 隱藏確認付款區塊
        confirmSection.style.display = "none";
        // 隱藏所有分隔線
        mainSeparators.forEach((separator) => {
            separator.style.display = "none";
        });

        // 套用 Empty State 的 Footer 樣式
        document.body.classList.add("booking-empty");

        return;
    }

    // 有預定行程時，隱藏沒有預定行程的文字
    bookingEmptyState.style.display = "none";

    // 取得預定行程資料
    currentBooking = result.data;
    const booking = currentBooking; 

    // 將景點圖片顯示在頁面
    bookingAttractionImage.src = booking.attraction.image;
    // 將景點名稱顯示在頁面
    bookingAttractionName.textContent = booking.attraction.name;
    // 將預定日期顯示在頁面
    bookingDate.textContent = booking.date;
    // 根據預定時間顯示對應的中文內容
    if (booking.time === "morning") {
        bookingTime.textContent = "早上 9 點到下午 4 點";
    } else {
        bookingTime.textContent = "下午 2 點到晚上 9 點";
    }
    // 將預定費用顯示在頁面
    bookingPrice.textContent = `新台幣 ${booking.price} 元`;
    // 將景點地址顯示在頁面
    bookingAddress.textContent = booking.attraction.address;
    // 將總價顯示在頁面
    confirmPrice.textContent = booking.price;
}

// ===========================================================
// 點擊刪除按鈕時，刪除目前的預定行程
bookingDeleteButton.addEventListener("click", async () => {
    // 從 LocalStorage 取得 JWT Token
    const token = localStorage.getItem("token");

    // 呼叫後端 API：刪除目前的預定行程
    const response = await fetch("/api/booking", {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    // 將 API 回傳資料轉成 JavaScript 物件
    const result = await response.json();

    // 如果成功刪除預定行程
    if (response.ok) {
        // 重新整理頁面
        window.location.reload();
    }
});

// ===========================================================
// 點擊確認訂購並付款時，向 TapPay 取得 Prime
confirmButton.addEventListener("click", () => {
    // 先確認信用卡欄位是否都填寫正確
    const tappayStatus = TPDirect.card.getTappayFieldsStatus();

    if (!tappayStatus.canGetPrime) {
        alert("信用卡資訊有誤，請確認後再試一次。");
        return;
    }

    // 向 TapPay 取得 Prime
    TPDirect.card.getPrime(async (result) => {
        if (result.status !== 0) {
            console.log("取得 Prime 失敗");
            console.log(result);
            return;
        }

        const prime = result.card.prime;

        // 從 LocalStorage 取得 JWT Token
        const token = localStorage.getItem("token");

        // 組成建立訂單 API 需要的資料
        const orderData = {
            prime: prime,
            order: {
                price: currentBooking.price,
                trip: {
                    attraction: {
                        id: currentBooking.attraction.id,
                        name: currentBooking.attraction.name,
                        address: currentBooking.attraction.address,
                        image: currentBooking.attraction.image
                    },
                    date: currentBooking.date,
                    time: currentBooking.time
                },
                contact: {
                    name: contactName.value,
                    email: contactEmail.value,
                    phone: contactPhone.value
                }
            }
        };

        console.log(orderData);

        // 呼叫後端 API：建立訂單並付款
        const response = await fetch("/api/orders", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(orderData)
        });

        // 將 API 回傳資料轉成 JavaScript 物件
        const orderResult = await response.json();

        console.log(orderResult);

        // 如果訂單建立且付款成功
        if (
            response.ok &&
            orderResult.data.payment.status === 0
        ) {
            // 取得訂單編號
            const orderNumber = orderResult.data.number;

            // 導向感謝頁面，並將訂單編號放在網址參數中
            window.location.href = `/thankyou?number=${orderNumber}`;
        }
    });
});

// ===========================================================
// 頁面載入完成後，依序取得會員與預定行程資料
async function initializeBookingPage() {
    // 先確認會員登入狀態
    const isSignedIn = await getMember();

    // 如果沒有登入，就不要繼續取得預定行程
    if (!isSignedIn) {
        return;
    }

    // 確認已登入後，再取得預定行程
    await getBooking();
}

// 執行預定行程頁面的初始化
initializeBookingPage();