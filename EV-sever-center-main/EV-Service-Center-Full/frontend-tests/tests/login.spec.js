const { test, expect } = require("@playwright/test");

// Sửa tài khoản này theo data thật trong hệ thống của mày
const VALID_EMAIL = "user@gmail.com";
const VALID_PASSWORD = "123456";

const INVALID_EMAIL = "wrong@gmail.com";
const INVALID_PASSWORD = "wrongpass";

async function goToLogin(page) {
  await page.goto("/");
}

async function fillLoginForm(page, email, password) {
  await page
    .locator('input[type="email"], input[name="email"], input[name="username"]')
    .first()
    .fill(email);
  await page
    .locator('input[type="password"], input[name="password"]')
    .first()
    .fill(password);
}

async function clickLogin(page) {
  await page
    .locator(
      'button[type="submit"], button:has-text("Đăng nhập"), button:has-text("Login")',
    )
    .first()
    .click();
}

test.describe("User Service - Frontend Login Test", () => {
  test("FE-USER-01 Mở được trang chính hoặc trang đăng nhập", async ({
    page,
  }) => {
    await goToLogin(page);

    await expect(page).toHaveTitle(/EV|Service|Center|Login|Đăng nhập/i);
  });

  test("FE-USER-02 Đăng nhập thành công", async ({ page }) => {
    await goToLogin(page);

    await fillLoginForm(page, VALID_EMAIL, VALID_PASSWORD);
    await clickLogin(page);

    await expect(page).toHaveURL(/dashboard|profile|home|booking|index/i);
  });

  test("FE-USER-03 Đăng nhập sai mật khẩu", async ({ page }) => {
    await goToLogin(page);

    await fillLoginForm(page, VALID_EMAIL, INVALID_PASSWORD);
    await clickLogin(page);

    await expect(
      page.locator("text=/sai|thất bại|không đúng|invalid|failed/i").first(),
    ).toBeVisible();
  });

  test("FE-USER-04 Đăng nhập với email không tồn tại", async ({ page }) => {
    await goToLogin(page);

    await fillLoginForm(page, INVALID_EMAIL, VALID_PASSWORD);
    await clickLogin(page);

    await expect(
      page
        .locator("text=/không tồn tại|thất bại|invalid|failed|not found/i")
        .first(),
    ).toBeVisible();
  });

  test("FE-USER-05 Bỏ trống email", async ({ page }) => {
    await goToLogin(page);

    await page
      .locator('input[type="password"], input[name="password"]')
      .first()
      .fill(VALID_PASSWORD);
    await clickLogin(page);

    const emailInput = page
      .locator(
        'input[type="email"], input[name="email"], input[name="username"]',
      )
      .first();

    await expect(emailInput).toBeVisible();
  });

  test("FE-USER-06 Bỏ trống password", async ({ page }) => {
    await goToLogin(page);

    await page
      .locator(
        'input[type="email"], input[name="email"], input[name="username"]',
      )
      .first()
      .fill(VALID_EMAIL);
    await clickLogin(page);

    const passwordInput = page
      .locator('input[type="password"], input[name="password"]')
      .first();

    await expect(passwordInput).toBeVisible();
  });
});
