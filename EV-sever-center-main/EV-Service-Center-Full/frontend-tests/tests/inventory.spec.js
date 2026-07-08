const { test, expect } = require("@playwright/test");

// Sửa theo tài khoản staff/admin thật của mày
const STAFF_EMAIL = "staff@gmail.com";
const STAFF_PASSWORD = "123456";

const TEST_PART_NUMBER = `FE-INV-${Date.now()}`;
const TEST_ITEM_NAME = "Vật tư test Playwright";

async function login(page) {
  await page.goto("/");

  await page.locator("#login-email-username").fill(STAFF_EMAIL);
  await page.locator("#login-password").fill(STAFF_PASSWORD);
  await page.locator("#login-form button[type='submit']").click();

  await page.waitForTimeout(1000);
}

async function goToInventory(page) {
  await page.goto("/");

  const inventoryLink = page
    .locator(
      'a:has-text("Kho"), a:has-text("Vật tư"), a:has-text("Inventory"), button:has-text("Kho"), button:has-text("Vật tư")',
    )
    .first();

  if (await inventoryLink.count()) {
    await inventoryLink.click();
  } else {
    await page.goto("/inventory.html");
  }

  await page.waitForTimeout(1000);
}

test.describe("Inventory Service - Frontend Test", () => {
  test("FE-INV-01 Mở được trang danh sách vật tư", async ({ page }) => {
    await login(page);
    await goToInventory(page);

    await expect(
      page.locator("text=/Kho|Vật tư|Inventory|Danh sách/i").first(),
    ).toBeVisible();
  });

  test("FE-INV-02 Hiển thị danh sách vật tư", async ({ page }) => {
    await login(page);
    await goToInventory(page);

    await expect(
      page
        .locator("table, .item, .inventory, text=/Vật tư|Inventory|Số lượng/i")
        .first(),
    ).toBeVisible();
  });

  test("FE-INV-03 Thêm vật tư hợp lệ", async ({ page }) => {
    await login(page);
    await goToInventory(page);

    await page
      .locator(
        'button:has-text("Thêm"), button:has-text("Add"), a:has-text("Thêm"), a:has-text("Add")',
      )
      .first()
      .click();

    await page
      .locator(
        'input[name="part_number"], input[placeholder*="mã"], input[placeholder*="part"]',
      )
      .first()
      .fill(TEST_PART_NUMBER);
    await page
      .locator(
        'input[name="name"], input[placeholder*="tên"], input[placeholder*="name"]',
      )
      .first()
      .fill(TEST_ITEM_NAME);

    const quantityInput = page
      .locator(
        'input[name="quantity"], input[placeholder*="số lượng"], input[placeholder*="quantity"]',
      )
      .first();
    if (await quantityInput.count()) await quantityInput.fill("10");

    const minQuantityInput = page
      .locator(
        'input[name="min_quantity"], input[placeholder*="tối thiểu"], input[placeholder*="min"]',
      )
      .first();
    if (await minQuantityInput.count()) await minQuantityInput.fill("2");

    const priceInput = page
      .locator(
        'input[name="price"], input[placeholder*="giá"], input[placeholder*="price"]',
      )
      .first();
    if (await priceInput.count()) await priceInput.fill("100000");

    const centerInput = page
      .locator('input[name="center_id"], input[placeholder*="center"]')
      .first();
    if (await centerInput.count()) await centerInput.fill("1");

    await page
      .locator(
        'button[type="submit"], button:has-text("Lưu"), button:has-text("Save"), button:has-text("Thêm")',
      )
      .first()
      .click();

    await expect(page.locator(`text=${TEST_ITEM_NAME}`).first()).toBeVisible({
      timeout: 5000,
    });
  });

  test("FE-INV-04 Thêm vật tư thiếu tên", async ({ page }) => {
    await login(page);
    await goToInventory(page);

    await page
      .locator(
        'button:has-text("Thêm"), button:has-text("Add"), a:has-text("Thêm"), a:has-text("Add")',
      )
      .first()
      .click();

    await page
      .locator(
        'input[name="part_number"], input[placeholder*="mã"], input[placeholder*="part"]',
      )
      .first()
      .fill(`FE-INV-INVALID-${Date.now()}`);

    const quantityInput = page
      .locator(
        'input[name="quantity"], input[placeholder*="số lượng"], input[placeholder*="quantity"]',
      )
      .first();
    if (await quantityInput.count()) await quantityInput.fill("10");

    await page
      .locator(
        'button[type="submit"], button:has-text("Lưu"), button:has-text("Save"), button:has-text("Thêm")',
      )
      .first()
      .click();

    await expect(
      page
        .locator("text=/thiếu|bắt buộc|không được để trống|required|invalid/i")
        .first(),
    ).toBeVisible();
  });

  test("FE-INV-05 Xem cảnh báo tồn kho thấp", async ({ page }) => {
    await login(page);
    await goToInventory(page);

    const lowStockButton = page
      .locator(
        'a:has-text("Cảnh báo"), button:has-text("Cảnh báo"), a:has-text("Low Stock"), button:has-text("Low Stock")',
      )
      .first();

    if (await lowStockButton.count()) {
      await lowStockButton.click();
    } else {
      await page.goto("/low-stock.html");
    }

    await expect(
      page
        .locator("text=/Cảnh báo|Tồn kho thấp|Low Stock|minimum|min_quantity/i")
        .first(),
    ).toBeVisible();
  });
});
