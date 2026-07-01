const { test, expect } = require("@playwright/test");

test.describe("Booking Service Frontend", () => {
  test("FE-BOOKING-01: Mở trang đặt lịch", async ({ page }) => {
    await page.goto("http://localhost:8000/booking.html");

    await expect(page).toHaveTitle(/Booking|EV|Service/i);
  });

  test("FE-BOOKING-02: Hiển thị form đặt lịch", async ({ page }) => {
    await page.goto("http://localhost:8000/booking.html");

    await expect(page.locator("form")).toBeVisible();
  });

  test("FE-BOOKING-03: Hiển thị ô nhập loại dịch vụ", async ({ page }) => {
    await page.goto("http://localhost:8000/booking.html");

    await expect(
      page.locator('input[name="service_type"], select[name="service_type"]'),
    ).toBeVisible();
  });

  test("FE-BOOKING-04: Hiển thị ô chọn ngày hẹn", async ({ page }) => {
    await page.goto("http://localhost:8000/booking.html");

    await expect(
      page.locator('input[type="date"], input[name="start_time"]'),
    ).toBeVisible();
  });

  test("FE-BOOKING-05: Submit khi để trống dữ liệu", async ({ page }) => {
    await page.goto("http://localhost:8000/booking.html");

    await page.click('button[type="submit"]');

    await expect(
      page.locator("text=/required|bắt buộc|vui lòng/i"),
    ).toBeVisible();
  });

  test("FE-BOOKING-06: Đặt lịch hợp lệ", async ({ page }) => {
    await page.goto("http://localhost:8000/booking.html");

    if (await page.locator('input[name="service_type"]').count()) {
      await page.fill('input[name="service_type"]', "Kiểm tra tổng quát");
    }

    if (await page.locator('input[name="start_time"]').count()) {
      await page.fill('input[name="start_time"]', "2026-07-10T09:00");
    }

    await page.click('button[type="submit"]');

    await expect(
      page.locator("text=/thành công|success|đặt lịch/i"),
    ).toBeVisible();
  });
});
