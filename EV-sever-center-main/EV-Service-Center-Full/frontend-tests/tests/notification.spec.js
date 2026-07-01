const { test, expect } = require("@playwright/test");

test.describe("Notification Service Frontend", () => {
  test("FE-NOTI-01: Mở trang thông báo", async ({ page }) => {
    await page.goto("http://localhost/notifications.html");

    await expect(page).toHaveTitle(/Notification|Thông báo|EV|Service/i);
  });

  test("FE-NOTI-02: Hiển thị danh sách thông báo", async ({ page }) => {
    await page.goto("http://localhost/notifications.html");

    await expect(
      page.locator("table, .notification-list, .notification-card"),
    ).toBeVisible();
  });

  test("FE-NOTI-03: Hiển thị nội dung thông báo", async ({ page }) => {
    await page.goto("http://localhost/notifications.html");

    await expect(
      page.locator("text=/Thông báo|Notification|message|title|nội dung/i"),
    ).toBeVisible();
  });

  test("FE-NOTI-04: Đánh dấu thông báo đã đọc", async ({ page }) => {
    await page.goto("http://localhost/notifications.html");

    const readButton = page.locator(
      'button:has-text("Đã đọc"), button:has-text("Read"), button:has-text("Mark as read")',
    );

    if (await readButton.count()) {
      await readButton.first().click();

      await expect(
        page.locator("text=/read|đã đọc|success|thành công/i"),
      ).toBeVisible();
    }
  });

  test("FE-NOTI-05: Hiển thị trạng thái thông báo", async ({ page }) => {
    await page.goto("http://localhost/notifications.html");

    await expect(
      page.locator("text=/pending|sent|failed|read|đã đọc|chưa đọc/i"),
    ).toBeVisible();
  });
});
