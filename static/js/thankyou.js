// 取得顯示訂單編號的元素
const thankyouOrderNumber = document.querySelector("#thankyou-order-number");
// 取得網址的 query parameter
const urlParams = new URLSearchParams(window.location.search);
// 取得訂單編號
const orderNumber = urlParams.get("number");

// 將訂單編號顯示在頁面上
thankyouOrderNumber.textContent = orderNumber;