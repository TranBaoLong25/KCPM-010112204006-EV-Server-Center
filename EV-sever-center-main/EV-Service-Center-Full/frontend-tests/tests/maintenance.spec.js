const { test, expect } = require("@playwright/test");

// Change these values if your seeded technician account is different.
const TECH_EMAIL = "technician@gmail.com";
const TECH_PASSWORD = "123456";

async function loginAsTechnician(page) {
  await page.goto("/");

  await expect(page.locator("#login-form")).toBeVisible();
  await page.locator("#login-email-username").fill(TECH_EMAIL);
  await page.locator("#login-password").fill(TECH_PASSWORD);

  await Promise.all([
    page.waitForURL(/\/technician\.html/i, { timeout: 15000 }),
    page.locator("#login-form button[type='submit']").click(),
  ]);
}

async function goToMaintenance(page) {
  if (!/\/technician\.html/i.test(page.url())) {
    await page.goto("/technician.html");
  }

  await expect(page.locator("#work-list-section")).toBeVisible();
  await expect(page.locator("#work-list-tbody")).toBeVisible();
}

test.describe("Maintenance Service - Frontend Test", () => {
  test.beforeEach(async ({ page }) => {
    page.on("dialog", (dialog) => dialog.accept());
  });

  test("FE-MAIN-01 opens technician work page", async ({ page }) => {
    await loginAsTechnician(page);
    await goToMaintenance(page);

    await expect(page.locator("#dashboard-title")).toBeVisible();
    await expect(page.locator("#work-list-section table")).toBeVisible();
  });

  test("FE-MAIN-02 shows task list table", async ({ page }) => {
    await loginAsTechnician(page);
    await goToMaintenance(page);

    await expect(page.locator("#work-list-tbody")).toBeVisible();
  });

  test("FE-MAIN-03 can move Pending to In Progress when a pending task exists", async ({
    page,
  }) => {
    await loginAsTechnician(page);
    await goToMaintenance(page);

    const startButton = page.locator('button[onclick*="in_progress"]').first();
    if (await startButton.isVisible().catch(() => false)) {
      await startButton.click();
      await expect(page.locator('button[onclick*="completed"]').first()).toBeVisible();
    }
  });

  test("FE-MAIN-04 can move In Progress to Completed when an in-progress task exists", async ({
    page,
  }) => {
    await loginAsTechnician(page);
    await goToMaintenance(page);

    const completeButton = page.locator('button[onclick*="completed"]').first();
    if (await completeButton.isVisible().catch(() => false)) {
      await completeButton.click();
      await expect(page.locator("#work-list-tbody")).toBeVisible();
    }
  });

  test("FE-MAIN-05 shows task action area", async ({ page }) => {
    await loginAsTechnician(page);
    await goToMaintenance(page);

    await expect(page.locator("#work-list-section table")).toBeVisible();
  });

  test("FE-MAIN-06 can open task tools when an in-progress task exists", async ({
    page,
  }) => {
    await loginAsTechnician(page);
    await goToMaintenance(page);

    const checklistButton = page
      .locator('button[onclick*="openChecklistModal"]')
      .first();

    if (await checklistButton.isVisible().catch(() => false)) {
      await checklistButton.click();
      await expect(page.locator("#checklist-modal")).toBeVisible();
    }
  });
});
