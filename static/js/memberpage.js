// 取得會員姓名顯示位置
const memberName = document.querySelector("#member-name");
// 取得登出會員按鈕
const logoutButton = document.querySelector("#logout-button");
// 取得 Bearer Token 顯示位置
const bearerToken = document.querySelector("#bearer-token");
// 取得產生 / 更新金鑰按鈕
const generateTokenButton = document.querySelector("#generate-token-button");

// ===========================================================
// 取得目前登入會員資料
async function loadMemberData() {
    // 從 LocalStorage 取得 JWT Token
    const token = localStorage.getItem("token");

    // 如果沒有 Token，代表目前沒有登入
    if (!token) {
        window.location.href = "/";
        return;
    }

    // 呼叫後端 API：取得目前登入會員資訊
    const response = await fetch("/api/user/auth", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    // 將 API 回傳資料轉成 JavaScript 物件
    const result = await response.json();

    // 如果 Token 無效或已過期，回到首頁
    if (result.data === null) {
        localStorage.removeItem("token");
        window.location.href = "/";
        return;
    }

    // 顯示會員姓名
    memberName.textContent = result.data.name;
}

// ===========================================================
// 取得目前會員的 MCP Bearer Token
async function loadMcpToken() {
    // 從 LocalStorage 取得登入用 JWT Token
    const token = localStorage.getItem("token");

    // 如果沒有 Token，就不繼續執行
    if (!token) {
        return;
    }

    // 呼叫後端 API：取得目前會員的 MCP Bearer Token
    const response = await fetch("/api/member/token", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    // 將 API 回傳資料轉成 JavaScript 物件
    const result = await response.json();

    // 如果取得成功
    if (response.ok) {
        // 如果會員已經有 MCP Token，就顯示出來
        if (result.token) {
            bearerToken.textContent = result.token;
        }

        return;
    }

    // 如果登入狀態失效
    if (response.status === 403) {
        localStorage.removeItem("token");
        window.location.href = "/";
    }
}

// ===========================================================
// 點擊「登出會員」
logoutButton.addEventListener("click", () => {
    // 移除 LocalStorage 中的 JWT Token
    localStorage.removeItem("token");

    // 回到首頁
    window.location.href = "/";
});

// ===========================================================
// 點擊「產生 / 更新金鑰」
generateTokenButton.addEventListener("click", async () => {
    // 從 LocalStorage 取得登入用 JWT Token
    const token = localStorage.getItem("token");

    // 呼叫後端 API：產生新的 MCP Bearer Token
    const response = await fetch("/api/member/token", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    // 將 API 回傳資料轉成 JavaScript 物件
    const result = await response.json();

    // 如果產生成功
    if (response.ok) {
        // 將新的 MCP Bearer Token 顯示在會員中心
        bearerToken.textContent = result.token;
        return;
    }

    // 如果登入狀態失效
    if (response.status === 403) {
        localStorage.removeItem("token");
        window.location.href = "/";
    }
});

// ===========================================================
// 頁面載入完成後，取得會員資料
loadMemberData();
// 取得目前會員的 MCP Bearer Token
loadMcpToken();