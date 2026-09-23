import { expect, test } from '@playwright/test';

test.describe('CapAssigner in the browser', () => {
  test('solves the classroom problem exactly and verifies it', async ({ page }) => {
    await page.goto('./');
    await page.getByRole('button', { name: /Buscar redes|Find networks/ }).click();
    const summary = page.locator('.summary');
    await expect(summary).toContainText(/exhaustiva|Exhaustive/);
    const first = page.locator('.results > .table-wrap tbody tr').first();
    await expect(first).toContainText('1 pF');
    await expect(first).toContainText('0 %');
    await expect(page.locator('.detail')).toContainText(/Verificado|Verified/);
    await expect(page.locator('.detail')).toContainText(/solución exacta|exact solution/);
    await expect(page.locator('.detail svg').first()).toBeVisible();
  });

  test('finds the balanced bridge from a shared link', async ({ page }) => {
    await page.goto('./#caps=10nF+10nF+10nF+10nF+10nF&target=10nF');
    const first = page.locator('.results > .table-wrap tbody tr').first();
    await expect(first).toContainText(/Puente|Bridge/);
    await expect(first).toContainText('0 %');
  });

  test('inventory mode with an E-series', async ({ page }) => {
    await page.goto('./#mode=inventory&target=3.14pF&decTo=-10');
    const rows = page.locator('.results > .table-wrap tbody tr');
    await expect(rows.first()).toContainText('3.14056 pF');
    await expect(rows).toHaveCount(20);
  });

  test('reports input errors and disables the search', async ({ page }) => {
    await page.goto('./');
    await page.locator('textarea').fill('3pF foo 2pF');
    await expect(page.getByRole('alert')).toContainText('foo');
    await expect(page.getByRole('button', { name: /Buscar redes|Find networks/ })).toBeDisabled();
  });

  test('switches language and keeps the page usable', async ({ page }) => {
    await page.goto('./');
    await page.getByRole('combobox', { name: /Idioma|Language/ }).selectOption('en');
    await expect(page.getByRole('button', { name: 'Find networks' })).toBeVisible();
    await page.getByRole('button', { name: 'Theory & methods' }).click();
    await expect(page.getByRole('heading', { name: 'How it searches' })).toBeVisible();
    await expect(page.locator('.katex').first()).toBeVisible();
  });

  test('a long search can be cancelled', async ({ page }) => {
    const caps = Array.from({ length: 12 }, (_, i) => `${(i + 1.37).toFixed(2)}pF`).join('+');
    await page.goto(`./#caps=${caps}&target=2.345pF&topo=sp`);
    const cancel = page.getByRole('button', { name: /Cancelar|Cancel/ });
    await cancel.click();
    await expect(page.locator('.note')).toContainText(/cancelada|cancelled/);
    await expect(page.getByRole('button', { name: /Buscar redes|Find networks/ })).toBeEnabled();
  });

  test('exports a SPICE netlist', async ({ page }) => {
    await page.goto('./#caps=3pF+2pF+3pF+1pF');
    await expect(page.locator('.results > .table-wrap tbody tr').first()).toContainText('0 %');
    const download = page.waitForEvent('download');
    await page.locator('.exp', { hasText: 'SPICE' }).getByRole('button', { name: /Descargar|Download/ }).click();
    const file = await download;
    const text = await (await file.createReadStream()).toArray();
    const netlist = Buffer.concat(text).toString();
    expect(netlist).toMatch(/^C1 /m);
    expect(netlist.trim().endsWith('.end')).toBe(true);
  });

  test('performance budget: 8 distinct parts, all topologies, exhaustive in under 5 s', async ({ page }) => {
    const caps = ['1.5pF', '2.7pF', '3.3pF', '4.7pF', '5.6pF', '6.8pF', '8.2pF', '9.1pF'].join('+');
    await page.goto(`./#caps=${caps}&target=10pF`);
    const summary = page.locator('.summary');
    await expect(summary).toContainText(/exhaustiva|Exhaustive/, { timeout: 30_000 });
    const text = (await summary.innerText()).replace(/\s+/g, ' ');
    const m = /([\d.,]+) (ms|s) · \d+ MB$/.exec(text.trim());
    expect(m).not.toBeNull();
    const ms = Number(m![1]!.replace(',', '.')) * (m![2] === 's' ? 1000 : 1);
    expect(ms).toBeLessThan(5000);
  });

  test('values spanning ten decades are solved and verified (user report)', async ({ page }) => {
    const caps = '10nF+10nF+10nF+10nF+10nF+55.4F+3F+10nF+10nF+55.4F+3F';
    await page.goto(`./#caps=${caps}&target=10.4nF&topo=sp`);
    await expect(page.locator('.summary')).toBeVisible({ timeout: 30_000 });
    await expect(page.locator('.note.bad')).toHaveCount(0);
    await expect(page.locator('.detail')).toContainText(/Verificado|Verified/);
  });

  test('works at phone width without horizontal scrolling', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 800 });
    await page.goto('./#caps=3pF+2pF+3pF+1pF');
    await expect(page.locator('.results > .table-wrap tbody tr').first()).toContainText('0 %');
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
  });
});
