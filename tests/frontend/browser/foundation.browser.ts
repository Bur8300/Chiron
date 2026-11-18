import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const pages = [
  "/giris",
  "/hesap-etkinlestir",
  "/onizleme/ogrenci/dersler",
  "/onizleme/ogrenci/kaynaklar",
  "/onizleme/ogrenci/soru-cevap",
  "/onizleme/ogrenci/ozetler",
  "/onizleme/ogrenci/sinavlar",
  "/onizleme/ogrenci/calisma-plani",
  "/onizleme/ogretmen/ogrenciler",
  "/onizleme/yonetici/ogrenciler",
  "/onizleme/yonetici/hesaplar",
  "/not-found",
];

for (const width of [360, 768, 1440]) {
  test(`all pages: no overflow or automated WCAG A/AA violations at ${width}px`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    for (const path of pages) {
      await page.goto(path);
      await expect(page.locator("h1")).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
        .analyze();
      expect(results.violations, `${path} at ${width}px`).toEqual([]);
    }
  });
}

test("phone menu supports keyboard, Escape and route changes", async ({
  page,
}) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/onizleme/ogrenci/dersler");
  const menu = page.getByRole("button", { name: "Menüyü aç" });
  await menu.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("navigation")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(menu).toBeFocused();
  await expect(page.getByRole("navigation")).toBeHidden();
  await menu.press("Enter");
  await page
    .getByRole("navigation")
    .getByRole("link", { name: "Soru sor" })
    .click();
  await expect(page.locator("h1")).toBeFocused();
  await expect(page.getByRole("navigation")).toBeHidden();
  await expect(page).toHaveURL(/soru-cevap$/);
  await menu.click();
  await page.getByRole("navigation").getByRole("link", { name: "Soru sor" }).click();
  await expect(page.getByRole("navigation")).toBeHidden();
  await expect(page.locator("h1")).toBeFocused();
  await menu.click();
  // Browser history navigation must also reset an open disclosure.
  await page.goBack();
  await expect(page).toHaveURL(/dersler$/);
  await expect(page.getByRole("navigation")).toBeHidden();
  await page.goForward();
  await expect(page).toHaveURL(/soru-cevap$/);
  await expect(page.getByRole("navigation")).toBeHidden();
  await page.goBack();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Derslerin, tek bir yerde." }),
  ).toBeVisible();
});

test("skip link targets content and enlarged text remains usable", async ({
  page,
}) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/onizleme/ogrenci/dersler");
  await page.getByRole("link", { name: "İçeriğe geç" }).focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();
  // 720 / 2 leaves the supported minimum of 360 CSS pixels.
  await page.setViewportSize({ width: 720, height: 900 });
  await page.addStyleTag({ content: "body { zoom: 2; }" });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test("capture the reviewed desktop and phone layouts", async ({
  page,
}, testInfo) => {
  for (const [name, width, height, route] of [
    ["login-desktop", 1440, 1000, "/giris"],
    ["login-phone", 360, 800, "/giris"],
    ["student-desktop", 1440, 1100, "/onizleme/ogrenci/dersler"],
    ["student-phone", 360, 800, "/onizleme/ogrenci/dersler"],
  ] as const) {
    await page.setViewportSize({ width, height });
    await page.goto(route);
    await expect(page.locator("h1")).toBeVisible();
    await page.screenshot({
      path: testInfo.outputPath(`${name}.png`),
      fullPage: true,
    });
  }
});
