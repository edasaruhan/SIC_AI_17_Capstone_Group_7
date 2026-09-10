import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const routes = [
  ["/", "GrowthPilot"],
  ["/customers", "Customers · GrowthPilot"],
  ["/intelligence", "Customer intelligence · GrowthPilot"],
  ["/audiences", "Audiences · GrowthPilot"],
  ["/orders", "Orders · GrowthPilot"],
  ["/products", "Products · GrowthPilot"],
  ["/inventory", "Inventory · GrowthPilot"],
  ["/imports", "Imports · GrowthPilot"],
  ["/integrations", "Integrations · GrowthPilot"],
  ["/campaigns", "Campaigns · GrowthPilot"],
  ["/decisions", "Decision review · GrowthPilot"],
  ["/audit", "Audit trail · GrowthPilot"],
  ["/settings", "Workspace settings · GrowthPilot"],
] as const;

for (const [route, title] of routes) {
  test(`${route} renders an honest, accessible application state`, async ({ page }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    const response = await page.goto(route);
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveTitle(title);
    await expect(page.getByRole("main")).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Primary navigation" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    expect(pageErrors).toEqual([]);

    const hasHorizontalOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    expect(hasHorizontalOverflow).toBe(false);

    const accessibility = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    expect(
      accessibility.violations,
      JSON.stringify(accessibility.violations, null, 2),
    ).toEqual([]);
  });
}
