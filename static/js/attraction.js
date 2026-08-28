// 取得目前網址中的景點編號
const path = window.location.pathname;
const attractionId = path.split("/").pop();

// 取得景點名稱
const attractionTitle = document.querySelector(".attraction-title");
// 取得景點分類與捷運站
const attractionCategoryMrt = document.querySelector(".attraction-category-mrt");
// 取得景點介紹
const attractionDescription = document.querySelector(".attraction-description");
// 取得景點地址
const attractionAddress = document.querySelector(".attraction-address");
// 取得景點交通方式
const attractionTransport = document.querySelector(".attraction-transport");
// 取得景點圖片
const attractionImage = document.querySelector(".attraction-image");

// 取得圖片指示器容器
const indicatorBar = document.querySelector(".indicator-bar");

// 儲存目前景點的所有圖片
let attractionImages = [];
// 紀錄目前顯示的圖片位置
let currentImageIndex = 0;

// ===========================================================
// 取得指定景點資料
async function loadAttraction() {
    try {
        // 呼叫後端 API：取得指定景點資料
        const response = await fetch(`/api/attraction/${attractionId}`);

        // API 回傳失敗時主動丟出錯誤
        if (!response.ok) {
            throw new Error("取得景點資料失敗");
        }

        // 將 API 回傳的 JSON 字串轉成 JavaScript 物件
        const result = await response.json();

        // 取得 API 回傳的單一景點資料
        const attractionData = result.data;

        // 將景點名稱顯示在頁面上
        attractionTitle.textContent = attractionData.name; 
        // 將景點分類與捷運站顯示在頁面上
        attractionCategoryMrt.textContent =
            `${attractionData.category} at ${attractionData.mrt}`;
        // 將景點介紹顯示在頁面上
        attractionDescription.textContent = attractionData.description;
        // 將景點地址顯示在頁面上
        attractionAddress.textContent = attractionData.address;
        // 將景點交通方式顯示在頁面上
        attractionTransport.textContent = attractionData.transport;

        // 儲存目前景點的所有圖片
        attractionImages = attractionData.images;

        // 根據圖片數量建立圖片指示器
        attractionImages.forEach((image, index) => {
            // 建立一個圖片指示器
            const indicator = document.createElement("div");

            // 加上 CSS class
            indicator.className = "indicator";

            // 如果是第一張圖片，就加上 active
            if (index === 0) {
                indicator.classList.add("active");
            }

            // 將圖片指示器加入 indicator-bar
            indicatorBar.appendChild(indicator);
        });

        // 將景點第一張圖片顯示在頁面上
        attractionImage.src = attractionImages[0];
        // 將景點名稱設定為圖片替代文字
        attractionImage.alt = attractionData.name;

        // 在 Console 顯示單一景點資料
        console.log(attractionData);

    } catch (error) {
        // 若 API 呼叫失敗，在 Console 顯示錯誤訊息
        console.error(error);
    }
}

// ===========================================================
// 更新目前圖片的指示器
function updateIndicator() {
    // 取得所有圖片指示器
    const indicators = document.querySelectorAll(".indicator");

    // 逐一處理每一個圖片指示器
    indicators.forEach((indicator, index) => {
        // 如果是目前顯示的圖片，就加上 active
        if (index === currentImageIndex) {
            indicator.classList.add("active");
        } else {
            // 其他圖片指示器移除 active
            indicator.classList.remove("active");
        }
    });
}

// ===========================================================
// 取得圖片左箭頭按鈕
const leftArrowButton = document.querySelector(".picture-arrow-left");
// 取得圖片右箭頭按鈕
const rightArrowButton = document.querySelector(".picture-arrow-right");

// 點擊左箭頭時，切換到上一張圖片
leftArrowButton.addEventListener("click", () => {
    // 如果目前沒有圖片，就不執行
    if (attractionImages.length === 0) {
        return;
    }

    // 將目前圖片位置減 1
    currentImageIndex -= 1;

    // 如果已經小於第一張，就切換到最後一張
    if (currentImageIndex < 0) {
        currentImageIndex = attractionImages.length - 1;
    }

    // 顯示目前位置的圖片
    attractionImage.src = attractionImages[currentImageIndex];

    // 更新圖片指示器
    updateIndicator();
});

// 點擊右箭頭時，切換到下一張圖片
rightArrowButton.addEventListener("click", () => {
    // 如果目前沒有圖片，就不執行
    if (attractionImages.length === 0) {
        return;
    }

    // 將目前圖片位置加 1
    currentImageIndex += 1;

    // 如果已經超過最後一張，就回到第一張
    if (currentImageIndex >= attractionImages.length) {
        currentImageIndex = 0;
    }

    // 顯示目前位置的圖片
    attractionImage.src = attractionImages[currentImageIndex];

    // 更新圖片指示器
    updateIndicator();
});

// ===========================================================
// 取得所有預約時間選項
const bookingTimeOptions = document.querySelectorAll(
    'input[name="booking-time"]'
);
// 取得導覽費用文字
const bookingPrice = document.querySelector(
    ".booking-price span:last-child"
);

// 點擊預約時間時，更新導覽費用
bookingTimeOptions.forEach((option) => {
    option.addEventListener("change", () => {
        // 如果選擇上午，導覽費用為 2000 元
        if (option.value === "morning") {
            bookingPrice.textContent = "新台幣 2000 元";
        } else {
            // 如果選擇下午，導覽費用為 2500 元
            bookingPrice.textContent = "新台幣 2500 元";
        }
    });
});

// ===========================================================
// 頁面載入完成後，取得指定景點資料
loadAttraction();