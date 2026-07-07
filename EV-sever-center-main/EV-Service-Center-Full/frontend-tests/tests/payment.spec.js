const { test, expect } = require("@playwright/test");

test.describe("Payment Service Frontend", () => {
  test("FE-PAYMENT-01: Mở trang thanh toán", async ({ page }) => {
    await page.goto("http://localhost/payment.html");

    await expect(page).toHaveTitle(/Payment|Thanh toán|EV|Service/i);
  });

  test("FE-PAYMENT-02: Hiển thị thông tin thanh toán", async ({ page }) => {
    await page.goto("http://localhost/payment.html");

    await expect(
      page.locator("text=/Thanh toán|Payment|Momo|Bank|Chuyển khoản/i"),
    ).toBeVisible();
  });

  test("FE-PAYMENT-03: Hiển thị phương thức thanh toán", async ({ page }) => {
    await page.goto("http://localhost/payment.html");

    await expect(
      page.locator("text=/momo_qr|bank_transfer|Momo|Ngân hàng|Chuyển khoản/i"),
    ).toBeVisible();
  });

  test("FE-PAYMENT-04: Không cho thanh toán khi thiếu dữ liệu", async ({
    page,
  }) => {
    await page.goto("http://localhost/payment.html");

    const submitButton = page.locator(
      'button[type="submit"], button:has-text("Thanh toán"), button:has-text("Pay")',
    );

    if (await submitButton.count()) {
      await submitButton.first().click();

      await expect(
        page.locator("text=/required|bắt buộc|vui lòng|thiếu|invalid/i"),
      ).toBeVisible();
    }
  });

  test("FE-PAYMENT-05: Hiển thị lịch sử thanh toán", async ({ page }) => {
    await page.goto("http://localhost/payment.html");

    const historyLink = page.locator(
      'a:has-text("Lịch sử"), button:has-text("Lịch sử"), a:has-text("History"), button:has-text("History")',
    );

    if (await historyLink.count()) {
      await historyLink.first().click();
    }

    await expect(
      page.locator("text=/Lịch sử|History|success|failed|pending/i"),
    ).toBeVisible();
  });
});
