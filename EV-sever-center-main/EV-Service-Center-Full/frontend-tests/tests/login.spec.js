const { test, expect } = require("@playwright/test");

test("Frontend mở được trang chính", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/EV|Service|Center|Login|Đăng nhập/i);
});
