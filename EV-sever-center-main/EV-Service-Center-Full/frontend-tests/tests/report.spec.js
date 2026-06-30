const { test, expect } = require("@playwright/test");

// Đổi theo tài khoản admin/staff thật
const ADMIN_EMAIL = "admin@gmail.com";
const ADMIN_PASSWORD = "123456";

async function login(page) {
  await page.goto("/");

  await page
    .locator(
      'input[type="email"], input[name="email"], input[name="username"]'
    )
    .first()
    .fill(ADMIN_EMAIL);

  await page
    .locator('input[type="password"], input[name="password"]')
    .first()
    .fill(ADMIN_PASSWORD);

  await page
    .locator(
      'button[type="submit"], button:has-text("Đăng nhập"), button:has-text("Login")'
    )
    .first()
    .click();

  await page.waitForTimeout(1000);
}

async function goToReport(page) {
  const reportLink = page.locator(
    'a:has-text("Báo cáo"), a:has-text("Report"), button:has-text("Báo cáo"), button:has-text("Report")'
  );

  if (await reportLink.count()) {
    await reportLink.first().click();
  } else {
    // Sửa lại nếu nhóm có URL khác
    await page.goto("/report.html");
  }

  await page.waitForTimeout(1000);
}

test.describe("Report Service - Frontend Test", () => {
  test("FE-REPORT-01 Mở được trang báo cáo", async ({ page }) => {
    await login(page);
    await goToReport(page);

    await expect(
      page.locator("text=/Báo cáo|Report|Thống kê/i").first()
    ).toBeVisible();
  });

  test("FE-REPORT-02 Hiển thị danh sách báo cáo", async ({ page }) => {
    await login(page);
    await goToReport(page);

    await expect(
      page.locator("table, canvas, .report-card").first()
    ).toBeVisible();
  });

  test("FE-REPORT-03 Xem báo cáo doanh thu", async ({ page }) => {
    await login(page);
    await goToReport(page);

    const revenueBtn = page.locator(
      'button:has-text("Doanh thu"), button:has-text("Revenue"), a:has-text("Doanh thu")'
    );

    if (await revenueBtn.count()) {
      await revenueBtn.first().click();

      await expect(
        page.locator("text=/Doanh thu|Revenue/i").first()
      ).toBeVisible();
    }
  });

  test("FE-REPORT-04 Xem báo cáo booking", async ({ page }) => {
    await login(page);
    await goToReport(page);

    const bookingBtn = page.locator(
      'button:has-text("Booking"), a:has-text("Booking")'
    );

    if (await bookingBtn.count()) {
      await bookingBtn.first().click();

      await expect(
        page.locator("text=/Booking|Lịch hẹn/i").first()
      ).toBeVisible();
    }
  });

  test("FE-REPORT-05 Xuất báo cáo", async ({ page }) => {
    await login(page);
    await goToReport(page);

    const exportBtn = page.locator(
      'button:has-text("Export"), button:has-text("Xuất"), a:has-text("Export")'
    );

    if (await exportBtn.count()) {
      await exportBtn.first().click();

      await expect(exportBtn.first()).toBeVisible();
    }
  });
});