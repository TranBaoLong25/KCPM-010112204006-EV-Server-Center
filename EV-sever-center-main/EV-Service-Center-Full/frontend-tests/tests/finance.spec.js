const { test, expect } = require("@playwright/test");

test.describe("Finance Service Frontend", () => {
  test("FE-FINANCE-01: Mở trang hóa đơn", async ({ page }) => {
    await page.goto("http://localhost/finance.html");

    await expect(page).toHaveTitle(/Finance|Invoice|Hóa đơn|EV|Service/i);
  });

  test("FE-FINANCE-02: Hiển thị danh sách hóa đơn", async ({ page }) => {
    await page.goto("http://localhost/finance.html");

    await expect(
      page.locator("table, .invoice-list, .invoice-card"),
    ).toBeVisible();
  });

  test("FE-FINANCE-03: Hiển thị thông tin tổng tiền", async ({ page }) => {
    await page.goto("http://localhost/finance.html");

    await expect(
      page.locator("text=/Tổng tiền|Total|Amount|VNĐ|VND/i"),
    ).toBeVisible();
  });

  test("FE-FINANCE-04: Hiển thị trạng thái hóa đơn", async ({ page }) => {
    await page.goto("http://localhost/finance.html");

    await expect(
      page.locator("text=/pending|issued|paid|canceled|Chờ|Đã thanh toán/i"),
    ).toBeVisible();
  });

  test("FE-FINANCE-05: Xem chi tiết hóa đơn", async ({ page }) => {
    await page.goto("http://localhost/finance.html");

    const detailButton = page.locator(
      'button:has-text("Chi tiết"), a:has-text("Chi tiết"), button:has-text("Detail"), a:has-text("Detail")',
    );

    if (await detailButton.count()) {
      await detailButton.first().click();

      await expect(
        page.locator("text=/Invoice|Hóa đơn|Dịch vụ|Phụ tùng|Service|Part/i"),
      ).toBeVisible();
    }
  });
});
