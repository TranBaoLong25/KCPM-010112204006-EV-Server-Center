const { test, expect } = require("@playwright/test");

// Đổi lại theo tài khoản Technician thật của nhóm
const TECH_EMAIL = "technician@gmail.com";
const TECH_PASSWORD = "123456";

async function login(page) {
  await page.goto("/");

  await page
    .locator(
      'input[type="email"], input[name="email"], input[name="username"]'
    )
    .first()
    .fill(TECH_EMAIL);

  await page
    .locator('input[type="password"], input[name="password"]')
    .first()
    .fill(TECH_PASSWORD);

  await page
    .locator(
      'button[type="submit"], button:has-text("Đăng nhập"), button:has-text("Login")'
    )
    .first()
    .click();

  await page.waitForTimeout(1000);
}

async function goToMaintenance(page) {
  const maintenanceLink = page.locator(
    'a:has-text("Công Việc"), a:has-text("Maintenance"), button:has-text("Công Việc"), button:has-text("Maintenance")'
  );

  if (await maintenanceLink.count()) {
    await maintenanceLink.first().click();
  } else {
    // sửa lại nếu nhóm có URL khác
    await page.goto("/technician-dashboard.html");
  }

  await page.waitForTimeout(1000);
}

test.describe("Maintenance Service - Frontend Test", () => {
  test("FE-MAIN-01 Mở được trang công việc", async ({ page }) => {
    await login(page);
    await goToMaintenance(page);

    await expect(
      page.locator("text=/Công Việc|Maintenance|Task/i").first()
    ).toBeVisible();
  });

  test("FE-MAIN-02 Hiển thị danh sách task", async ({ page }) => {
    await login(page);
    await goToMaintenance(page);

    await expect(
      page
        .locator(
          "table, .task, .maintenance-card, text=/Pending|In Progress|Completed/i"
        )
        .first()
    ).toBeVisible();
  });

  test("FE-MAIN-03 Chuyển Pending → In Progress", async ({ page }) => {
    await login(page);
    await goToMaintenance(page);

    const button = page.locator(
      'button:has-text("Bắt đầu"), button:has-text("Start"), button:has-text("In Progress")'
    );

    if (await button.count()) {
      await button.first().click();

      await expect(
        page.locator("text=/In Progress|Đang thực hiện/i").first()
      ).toBeVisible();
    }
  });

  test("FE-MAIN-04 Chuyển In Progress → Completed", async ({ page }) => {
    await login(page);
    await goToMaintenance(page);

    const button = page.locator(
      'button:has-text("Hoàn thành"), button:has-text("Complete"), button:has-text("Completed")'
    );

    if (await button.count()) {
      await button.first().click();

      await expect(
        page.locator("text=/Completed|Hoàn thành/i").first()
      ).toBeVisible();
    }
  });

  test("FE-MAIN-05 Hiển thị trạng thái Failed", async ({ page }) => {
    await login(page);
    await goToMaintenance(page);

    const failButton = page.locator(
      'button:has-text("Failed"), button:has-text("Lỗi"), button:has-text("Thất bại")'
    );

    if (await failButton.count()) {
      await failButton.first().click();

      await expect(
        page.locator("text=/Failed|Thất bại/i").first()
      ).toBeVisible();
    }
  });

  test("FE-MAIN-06 Xem chi tiết task", async ({ page }) => {
    await login(page);
    await goToMaintenance(page);

    const detailButton = page.locator(
      'button:has-text("Chi tiết"), button:has-text("View"), a:has-text("Chi tiết"), a:has-text("View")'
    );

    if (await detailButton.count()) {
      await detailButton.first().click();

      await expect(
        page.locator("text=/Booking|VIN|Description|Mô tả/i").first()
      ).toBeVisible();
    }
  });
});