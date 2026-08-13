// 取得分類選單
const categoryPanel = document.querySelector(".category-panel");
// 取得分類選擇按鈕
const categorySelector = document.querySelector(".category-selector");
// 取得搜尋輸入框
const searchInput = document.querySelector(".search-input");
// 取得搜尋按鈕
const searchButton = document.querySelector(".search-button");
// 取得 HTML 中 MRT 列表的容器
const mrtListContainer = document.querySelector(".mrt-list-container");
// 取得景點卡片容器
const attractionsGroup = document.querySelector(".attractions-group");
// 取得頁面底部的偵測點
const observerElement = document.querySelector(".observer");

// 紀錄下一頁頁碼
let nextPage = 0;
// 紀錄目前是否正在載入景點資料
let isLoading = false;
// 紀錄目前選擇的景點分類
let selectedCategory = null;
// 紀錄目前搜尋的關鍵字
let currentKeyword = "";

// ===========================================================
// 取得所有景點分類
async function loadCategories() {
    try {
        // 呼叫後端 API：取得所有景點分類
        const response = await fetch("/api/categories");

        // API 回傳失敗時主動丟出錯誤
        if (!response.ok) {
            throw new Error("取得分類資料失敗");
        }

        // 將 API 回傳資料轉成 JavaScript 物件
        const result = await response.json();

        // 建立「全部分類」項目
        const allCategoryItem = document.createElement("div");
        allCategoryItem.className = "category-item";
        allCategoryItem.textContent = "全部分類";

        // 點擊「全部分類」時，取消分類篩選
        allCategoryItem.addEventListener("click", () => {
            // 清除目前選擇的分類
            selectedCategory = null;

            // 將分類選擇按鈕改回「全部分類」
            categorySelector.textContent = "全部分類▼";

            // 關閉分類選單
            categoryPanel.style.display = "none";
        });

        // 將「全部分類」加入分類選單
        categoryPanel.appendChild(allCategoryItem);

        // 逐一處理每一個景點分類
        result.data.forEach((category) => {
            // 建立一個分類項目
            const categoryItem = document.createElement("div");

            // 加上 CSS class
            categoryItem.className = "category-item";

            // 將分類名稱放入項目中
            categoryItem.textContent = category;

            // 點擊分類項目時，更新目前選擇的分類
            categoryItem.addEventListener("click", () => {
                // 儲存目前選擇的分類
                selectedCategory = category;

                // 將分類選擇按鈕改成目前選擇的分類
                categorySelector.textContent = category + "▼";

                // 關閉分類選單
                categoryPanel.style.display = "none";
            });

            // 將分類項目加入分類選單
            categoryPanel.appendChild(categoryItem);
        });

    } catch (error) {
        console.error(error);
    }
}

// ===========================================================
// 點擊分類選擇按鈕時，開啟或關閉分類選單
categorySelector.addEventListener("click", () => {
    if (categoryPanel.style.display === "grid") {
        categoryPanel.style.display = "none";
    } else {
        categoryPanel.style.display = "grid";
    }
});

// ===========================================================
// 點擊搜尋按鈕時，依目前選擇的分類與關鍵字搜尋景點
searchButton.addEventListener("click", () => {
    // 取得搜尋框中的關鍵字
    const keyword = searchInput.value.trim();

    // 儲存目前搜尋的關鍵字
    currentKeyword = keyword;

    // 清空目前畫面上的景點
    attractionsGroup.innerHTML = "";

    // 從第 0 頁重新載入篩選後的景點
    loadAttractions(
        0,
        selectedCategory ?? "", // 如果目前還沒選分類，selectedCategory 是 null，就改傳空字串
        keyword
    );
});

// ===========================================================
// 取得所有捷運站名稱並顯示在首頁
async function loadMRTs() {
    try {
        // 呼叫後端 API：取得所有捷運站名稱
        const response = await fetch("/api/mrts");

        // API 回傳失敗時主動丟出錯誤
        if (!response.ok) {
            throw new Error("取得 MRT 資料失敗");
        }

        // 將 API 回傳的 JSON 字串轉成 JavaScript 物件
        const result = await response.json();

        // result.data 是一個陣列
        // 例如：["劍潭", "圓山", "士林", ...]
        // 逐一處理每一個捷運站名稱
        result.data.forEach((mrt) => {
            // 建立一個 div 元素
            const mrtItem = document.createElement("div");

            // 加上 CSS class，讓它套用 .mrt-item 樣式
            mrtItem.className = "mrt-item";

            // 將捷運站名稱放入 div 中
            mrtItem.textContent = mrt;

            // 點擊 MRT 名稱時，依 MRT 名稱與目前分類搜尋景點
            mrtItem.addEventListener("click", () => {
                // 將 MRT 名稱填入搜尋框
                searchInput.value = mrt;

                // 將 MRT 名稱儲存為目前搜尋的關鍵字
                currentKeyword = mrt;

                // 清空目前畫面上的景點
                attractionsGroup.innerHTML = "";

                // 從第 0 頁重新載入符合條件的景點
                loadAttractions(
                    0,
                    selectedCategory ?? "",
                    currentKeyword
                );
            });

            // 將 div 加入 MRT List Container
            mrtListContainer.appendChild(mrtItem);
        });
    } catch (error) {
        // 若 API 呼叫失敗，在 Console 顯示錯誤訊息
        console.error(error);
    }
}

// ===========================================================
// 取得 MRT 左右箭頭按鈕與可滾動區域
const leftButton = document.querySelector(".arrow-button.left");
const rightButton = document.querySelector(".arrow-button.right");
const mrtList = document.querySelector(".mrt-list");

// 點擊左箭頭時，MRT 列表向左滾動
leftButton.addEventListener("click", () => {
    const scrollDistance = window.innerWidth <= 600 ? 200 : 500;
    mrtList.scrollBy({
        left: -scrollDistance,
        behavior: "smooth"
    });
});

// 點擊右箭頭時，MRT 列表向右滾動
rightButton.addEventListener("click", () => {
    const scrollDistance = window.innerWidth <= 600 ? 200 : 500;
    mrtList.scrollBy({
        left: scrollDistance,
        behavior: "smooth"
    });
});

// ===========================================================
// 取得指定頁面的景點資料並顯示在首頁
async function loadAttractions(page, category = "", keyword = "") {
    // 如果目前正在載入資料，就不要再次呼叫 API
    if (isLoading) {
        return;
    }
    // 開始載入
    isLoading = true;

    try {
        // 建立 API 網址
        let apiUrl = `/api/attractions?page=${page}`;

        // 如果有選擇分類，就加入 category
        if (category !== "") {
            apiUrl += `&category=${encodeURIComponent(category)}`;
        }

        // 如果有輸入關鍵字，就加入 keyword
        if (keyword !== "") {
            apiUrl += `&keyword=${encodeURIComponent(keyword)}`;
        }

        // 呼叫後端 API
        const response = await fetch(apiUrl);

        // API 回傳失敗時主動丟出錯誤
        if (!response.ok) {
            throw new Error("取得景點資料失敗");
        }

        // 將 API 回傳的 JSON 字串轉成 JavaScript 物件
        const result = await response.json();

        // 儲存 API 回傳的下一頁頁碼
        nextPage = result.nextPage;

        // 逐一處理每一筆景點資料
        result.data.forEach((attractionData) => {
            // 建立 attraction
            const attraction = document.createElement("div");
            attraction.className = "attraction";
            // 建立 picture
            const picture = document.createElement("div");
            picture.className = "picture";
            // 建立 img
            const image = document.createElement("img");
            // 建立 attraction-name
            const attractionName = document.createElement("div");
            attractionName.className = "attraction-name";
            // 建立 details
            const details = document.createElement("div");
            details.className = "details";
            // 建立 info
            const info = document.createElement("div");
            info.className = "info";
            // 建立 mrt
            const mrt = document.createElement("div");
            mrt.className = "mrt";
            // 建立 category
            const categoryText = document.createElement("div");
            categoryText.className = "category";
            
            // 設定圖片
            image.src = attractionData.images[0];
            image.alt = attractionData.name;
            // 設定景點名稱
            attractionName.textContent = attractionData.name;
            // 設定捷運站
            mrt.textContent = attractionData.mrt;
            // 設定景點分類
            categoryText.textContent = attractionData.category;

            // picture 底下放圖片與景點名稱
            picture.appendChild(image);
            picture.appendChild(attractionName);
            // info 底下放 MRT 與分類
            info.appendChild(mrt);
            info.appendChild(categoryText);
            // details 底下放 info
            details.appendChild(info);
            // attraction 底下放 picture 與 details
            attraction.appendChild(picture);
            attraction.appendChild(details);
            // 將 attraction 加入 attractions-group
            attractionsGroup.appendChild(attraction);
        });    
    } catch (error) {
        console.error(error);
    } finally {
        // 不論成功或失敗，都代表這次載入結束
        isLoading = false;
    }
}

// 偵測使用者是否滑到景點列表底部
const observer = new IntersectionObserver((entries) => {

    // 取得被觀察元素的狀態
    const entry = entries[0];

    // 如果偵測點進入畫面，而且還有下一頁
    if (
        entry.isIntersecting &&
        nextPage !== null &&
        !isLoading
    ) {
        loadAttractions(
            nextPage,
            selectedCategory ?? "",
            currentKeyword
        );
    }
});

// 開始觀察頁面底部的偵測點
observer.observe(observerElement);

// ===========================================================
// 頁面載入完成後，取得所有 MRT 名稱
loadMRTs();

// 頁面載入完成後，取得所有景點分類
loadCategories();

// 頁面載入完成後，取得第一頁景點資料
loadAttractions(0);