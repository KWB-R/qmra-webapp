import { expect, test } from '@playwright/test';

test('can create an assessment and add a treatment with failure fields', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('link', { name: 'Try out' }).click();
  await page.waitForLoadState('networkidle');
  await expect(page).toHaveURL(/\/assessment\/?$/);

  await page.locator("input[id*='name']").first().fill('Assessment 1');
  const exposureSelect = page.locator('#id_ra-exposure_name');
  await exposureSelect.selectOption({ value: 'domestic use, car washing' });
  await exposureSelect.dispatchEvent('change');

  await expect(page.locator("input[id*='events_per_year']")).toHaveValue('25');
  await expect(page.locator("input[id*='volume_per_event']")).toHaveValue('0.0001');

  const sourceSelect = page.locator("select[id*='source_name']");
  await sourceSelect.selectOption({ value: 'groundwater' });
  await sourceSelect.dispatchEvent('change');

  await page.locator('#id_select_treatment').selectOption({ label: 'Bank filtration' });
  await page.locator('#add-treatment-btn').click();

  const treatmentCard = page.locator('#treatments-n-0');
  await expect(treatmentCard).toContainText('Bank filtration');
  await expect(treatmentCard.locator("input[id*='failure_duration_minutes']")).toBeVisible();
  await expect(treatmentCard.locator("input[id*='failure_frequency_days_per_year']")).toBeVisible();
  await expect(treatmentCard.locator("input[id*='bacteria_min']")).toBeVisible();
  await expect(treatmentCard.locator("input[id*='viruses_min']")).toBeVisible();
  await expect(treatmentCard.locator("input[id*='protozoa_min']")).toBeVisible();
});
