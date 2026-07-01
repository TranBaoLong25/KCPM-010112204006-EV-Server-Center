const { test, expect } = require("@playwright/test");

test.describe("Staff Service Frontend", () => {
  test("FE-STAFF-01: Mở trang quản lý nhân viên", async ({ page }) => {
    await page.goto("http://localhost:8000/staff.html");

    await expect(page).toHaveTitle(/Staff|Nhân viên|EV|Service/i);
  });

  test("FE-STAFF-02: Hiển thị danh sách nhân viên", async ({ page }) => {
    await page.goto("http://localhost:8000/staff.html");

    await expect(page.locator("table, .staff-list")).toBeVisible();
  });

  test("FE-STAFF-03: Hiển thị form thêm nhân viên", async ({ page }) => {
    await page.goto("http://localhost:8000/staff.html");

    await expect(page.locator("form")).toBeVisible();
  });

  test("FE-STAFF-04: Hiển thị ô nhập họ tên", async ({ page }) => {
    await page.goto("http://localhost:8000/staff.html");

    await expect(page.locator('input[name="full_name"]')).toBeVisible();
  });

  test("FE-STAFF-05: Hiển thị ô nhập email", async ({ page }) => {
    await page.goto("http://localhost:8000/staff.html");

    await expect(page.locator('input[name="email"]')).toBeVisible();
  });

  test("FE-STAFF-06: Không cho submit khi bỏ trống dữ liệu", async ({
    page,
  }) => {
    await page.goto("http://localhost:8000/staff.html");

    await page.click('button[type="submit"]');

    await expect(
      page.locator("text=/required|bắt buộc|vui lòng/i"),
    ).toBeVisible();
  });

  test("FE-STAFF-07: Thêm nhân viên thành công", async ({ page }) => {
    await page.goto("http://localhost:8000/staff.html");

    if (await page.locator('input[name="full_name"]').count()) {
      await page.fill('input[name="full_name"]', "Nguyễn Văn Hùng");
    }

    if (await page.locator('input[name="email"]').count()) {
      await page.fill('input[name="email"]', "hungtest@gmail.com");
    }

    if (await page.locator('input[name="phone"]').count()) {
      await page.fill('input[name="phone"]', "0912345678");
    }

    if (await page.locator('input[name="password"]').count()) {
      await page.fill('input[name="password"]', "123456");
    }

    await page.click('button[type="submit"]');

    await expect(
      page.locator("text=/thành công|success|đã thêm/i"),
    ).toBeVisible();
  });
});
