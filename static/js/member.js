// 取得預定行程按鈕
const bookingButton = document.querySelector("#booking-button");
// 取得登入 / 註冊按鈕
const loginRegisterButton = document.querySelector("#login-register-button");
// 取得 Dialog 背景遮罩
const dialogOverlay = document.querySelector("#dialog-overlay");
// 取得登入 Dialog
const signinDialog = document.querySelector("#signin-dialog");
// 取得註冊 Dialog
const signupDialog = document.querySelector("#signup-dialog");
// 取得登入 Dialog 關閉按鈕
const signinClose = document.querySelector("#dialog-close");
// 取得註冊 Dialog 關閉按鈕
const signupClose = document.querySelector("#signup-close");
// 取得切換到註冊的文字
const showSignup = document.querySelector("#show-signup");
// 取得切換到登入的文字
const showSignin = document.querySelector("#show-signin");

// 取得登入 Email 輸入框
const signinEmail = document.querySelector("#signin-email");
// 取得登入密碼輸入框
const signinPassword = document.querySelector("#signin-password");
// 取得登入按鈕
const signinButton = document.querySelector("#signin-button");
// 取得登入訊息區塊
const signinMessage = document.querySelector("#signin-message");

// 取得註冊姓名輸入框
const signupName = document.querySelector("#signup-name");
// 取得註冊 Email 輸入框
const signupEmail = document.querySelector("#signup-email");
// 取得註冊密碼輸入框
const signupPassword = document.querySelector("#signup-password");
// 取得註冊按鈕
const signupButton = document.querySelector("#signup-button");
// 取得註冊訊息區塊
const signupMessage = document.querySelector("#signup-message");

// ===========================================================
// 點擊「預定行程」時，依登入狀態執行對應功能
bookingButton.addEventListener("click", async () => {
    // 從 LocalStorage 取得 JWT Token
    const token = localStorage.getItem("token");

    // 呼叫後端 API：確認目前會員登入狀態
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
        // 顯示 Dialog 背景遮罩
        dialogOverlay.style.display = "block";
        // 顯示登入 Dialog
        signinDialog.style.display = "block";
        // 隱藏註冊 Dialog
        signupDialog.style.display = "none";

        return;
    }

    // 如果已經登入，前往預定行程頁面
    window.location.href = "/booking";
});

// ===========================================================
// 點擊右上角會員按鈕時，依登入狀態執行對應功能
loginRegisterButton.addEventListener("click", () => {
    // 如果目前顯示「登出系統」，代表使用者已登入
    if (loginRegisterButton.textContent === "登出系統") {
        // 移除 LocalStorage 中的 JWT Token
        localStorage.removeItem("token");

        // 重新整理目前頁面
        window.location.reload();

        return;
    }

    // 顯示 Dialog 背景遮罩
    dialogOverlay.style.display = "block";

    // 顯示登入 Dialog
    signinDialog.style.display = "block";

    // 隱藏註冊 Dialog
    signupDialog.style.display = "none";
});

// ===========================================================
// 點擊「點此註冊」時，切換到註冊 Dialog
showSignup.addEventListener("click", () => {
    // 隱藏登入 Dialog
    signinDialog.style.display = "none";

    // 顯示註冊 Dialog
    signupDialog.style.display = "block";

    // 清除上一次的註冊訊息
    signupMessage.textContent = "";
    signupMessage.style.display = "none";
});

// 點擊「點此登入」時，切換到登入 Dialog
showSignin.addEventListener("click", () => {
    // 隱藏註冊 Dialog
    signupDialog.style.display = "none";

    // 顯示登入 Dialog
    signinDialog.style.display = "block";
});

// ===========================================================
// 點擊登入 Dialog 的關閉按鈕時，關閉 Dialog
signinClose.addEventListener("click", () => {
    // 隱藏 Dialog 背景遮罩
    dialogOverlay.style.display = "none";
});

// 點擊註冊 Dialog 的關閉按鈕時，關閉 Dialog
signupClose.addEventListener("click", () => {
    // 隱藏 Dialog 背景遮罩
    dialogOverlay.style.display = "none";
});

// ===========================================================
// 點擊登入按鈕時，取得使用者輸入的登入資料
signinButton.addEventListener("click", async () => {
    // 取得 Email
    const email = signinEmail.value.trim();

    // 取得密碼
    const password = signinPassword.value;

    // 呼叫後端 API：登入會員帳戶
    const response = await fetch("/api/user/auth", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    // 將 API 回傳資料轉成 JavaScript 物件
    const result = await response.json();

    // 登入成功
    if (response.ok) {
        // 將後端回傳的 JWT Token 儲存在 LocalStorage
        localStorage.setItem("token", result.token);

        // 重新整理目前頁面
        window.location.reload();

    // 登入失敗
    } else {
        // 顯示後端回傳的錯誤訊息
        signinMessage.textContent = result.message;

        // 顯示訊息區塊
        signinMessage.style.display = "block";
    }
});

// ===========================================================
// 在登入輸入框按下 Enter 時，直接登入
signinEmail.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        signinButton.click();
    }
});

signinPassword.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        signinButton.click();
    }
});

// ===========================================================
// 點擊註冊按鈕時，取得使用者輸入的註冊資料
signupButton.addEventListener("click", async () => {
    // 取得姓名
    const name = signupName.value.trim();

    // 取得 Email
    const email = signupEmail.value.trim();

    // 取得密碼
    const password = signupPassword.value;

    // 呼叫後端 API：註冊新會員
    const response = await fetch("/api/user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name,
            email: email,
            password: password
        })
    });

    // 將 API 回傳資料轉成 JavaScript 物件
    const result = await response.json();

    // 註冊成功
    if (response.ok) {
        // 顯示註冊成功訊息
        signupMessage.textContent = "註冊成功，請登入系統";

        // 顯示訊息區塊
        signupMessage.style.display = "block";

        // 清空註冊表單
        signupName.value = "";
        signupEmail.value = "";
        signupPassword.value = "";

    // 註冊失敗
    } else {
        // 顯示後端回傳的錯誤訊息
        signupMessage.textContent = result.message;

        // 顯示訊息區塊
        signupMessage.style.display = "block";
    }
});

// ===========================================================
// 在註冊輸入框按下 Enter 時，直接註冊
signupName.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        signupButton.click();
    }
});

signupEmail.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        signupButton.click();
    }
});

signupPassword.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        signupButton.click();
    }
});

// ===========================================================
// 確認目前會員登入狀態
async function checkSigninStatus() {
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

    // 如果沒有登入，顯示「登入/註冊」
    if (result.data === null) {
        loginRegisterButton.textContent = "登入/註冊";

    // 如果已經登入，顯示「登出系統」
    } else {
        loginRegisterButton.textContent = "登出系統";
    }
}

// ===========================================================
// 頁面載入完成後，確認目前會員登入狀態
checkSigninStatus();