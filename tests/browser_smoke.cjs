/* Chromium real; execute apenas contra a instância local de desenvolvimento.
 * Requer Playwright e Chromium disponíveis; não instala nem testa produção.
 */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const output = path.resolve('evidencias');
fs.mkdirSync(output, { recursive: true });
const result = { environment: 'local cloud / Chromium headless', started_at_utc: new Date().toISOString(),
  base_commit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
  working_tree: 'Alterações locais em validação; os hashes do código testado constam em codigo_validado.json.',
  checks: [], limitations: ['Sem leitor de tela real ou estudo com usuários.', 'Idioma html=en do framework; sem conformidade WCAG declarada.', 'Produção e nova restauração não testadas.'] };
const browserErrors = [];
let browser;
async function check(name, run) {
  const started = Date.now();
  try { const details = await run(); result.checks.push({ name, status: 'passed', ms: Date.now() - started, details }); }
  catch (error) { result.checks.push({ name, status: 'failed', ms: Date.now() - started, error: error.message }); throw error; }
}
(async () => {
  browser = await chromium.launch({ executablePath: process.env.SENTINELA_CHROMIUM || '/usr/bin/chromium',
    headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1366, height: 936 }, acceptDownloads: true });
  const page = await context.newPage();
  page.on('pageerror', error => browserErrors.push(error.message));
  await check('Inicialização real e ranking desktop', async () => {
    const response = await page.goto('http://127.0.0.1:8501/');
    assert.equal(response.status(), 200);
    await page.getByRole('heading', { name: 'Laguna, km 304,000: maior índice do filtro', exact: true }).waitFor();
    await page.getByTestId('stPlotlyChart').nth(1).waitFor();
    await page.screenshot({ path: path.join(output, 'desktop.jpg'), quality: 80 });
    return { status: response.status(), html_lang: await page.locator('html').getAttribute('lang') };
  });
  await check('Tabela HTML equivalente ao ranking e foco por teclado', async () => {
    await page.getByText('Dados equivalentes ao ranking e totais por radar', { exact: true }).click();
    const table = page.getByRole('table').first();
    await table.waitFor({ state: 'visible' });
    assert.match(await table.innerText(), /VC101-9/);
    for (let i = 0; i < 8; i++) await page.keyboard.press('Tab');
    const focus = await page.evaluate(() => ({ tag: document.activeElement.tagName, name: document.activeElement.getAttribute('aria-label') }));
    assert.notEqual(focus.tag, 'BODY');
    return { focus, note: 'Percurso parcial de teclado; não equivale a teste com leitor de tela.' };
  });
  await check('Toolbar Plotly: zoom, reset, tela cheia e download PNG', async () => {
    const chart = page.getByTestId('stPlotlyChart').first();
    await chart.scrollIntoViewIfNeeded();
    await chart.hover();
    const controls = await chart.locator('.modebar-btn').evaluateAll(nodes => nodes.map(n => n.getAttribute('data-title')));
    const before = await chart.locator('.js-plotly-plot').evaluate(n => [...n.layout.xaxis.range]);
    await chart.locator('.modebar-btn[data-title="Zoom in"]').click();
    const after = await chart.locator('.js-plotly-plot').evaluate(n => [...n.layout.xaxis.range]);
    assert.ok(after[1] - after[0] < before[1] - before[0]);
    await chart.locator('.modebar-btn[data-title="Reset axes"]').click();
    const reset = await chart.locator('.js-plotly-plot').evaluate(n => [...n.layout.xaxis.range]);
    assert.ok(Math.abs(reset[1] - before[1]) < 1e-6);
    const fullscreen = chart.getByRole('button', { name: /Fullscreen/ });
    if (await fullscreen.count()) { await fullscreen.click(); await page.keyboard.press('Escape'); }
    const downloadPromise = page.waitForEvent('download');
    await chart.locator('.modebar-btn[data-title="Download plot as a PNG"]').click();
    const download = await downloadPromise;
    const file = path.join(output, 'ranking_exportado.png');
    await download.saveAs(file);
    assert.ok(fs.readFileSync(file).subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])));
    fs.unlinkSync(file); // Não versionar imagens derivadas redundantes.
    return { controls, png_bytes_verified: true, axes_changed_and_reset: true };
  });
  await check('Clique real no localizador sincroniza a ficha', async () => {
    const chart = page.getByTestId('stPlotlyChart').nth(1);
    await chart.evaluate(n => n.scrollIntoView({ block: 'center' }));
    const points = await chart.locator('.point').evaluateAll(nodes => nodes.map(n => {
      const r = n.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
    }));
    const distances = points.map((p, i) => Math.min(...points.filter((_, j) => i !== j).map(q => Math.hypot(p.x - q.x, p.y - q.y))));
    const index = distances.indexOf(Math.max(...distances)); // ponto isolado evita ambiguidade de símbolos sobrepostos.
    const expected = await chart.locator('.js-plotly-plot').evaluate((n, i) => n.data[0].customdata[i][0], index);
    await page.mouse.move(points[index].x, points[index].y);
    await page.waitForTimeout(150); // permitir atualização do hover do Plotly antes do clique.
    await page.mouse.click(points[index].x, points[index].y);
    await page.waitForFunction(id => document.querySelector('input[aria-label="Radar para consultar"]')?.value === id,
      expected, { timeout: 15000 });
    const ficha = await page.getByRole('combobox', { name: 'Radar para consultar', exact: true }).inputValue();
    assert.equal(ficha, expected);
    return { expected, ficha, real_mouse_click: true };
  });
  const pages = [
    ['Comparador de equipamentos', 'Comparar radares'],
    ['Evolução e persistência', 'Histórico de velocidade'],
    ['Contexto rodoviário', 'Acidentes no contexto'],
    ['Relatório preventivo', 'Síntese para investigação']
  ];
  for (const [name, heading] of pages) {
    await check('Navegação: ' + name, async () => {
      await page.getByRole('radio', { name, exact: true }).check({ force: true });
      await page.getByRole('heading', { name: heading, exact: true }).first().waitFor();
      assert.equal(await page.getByTestId('stException').count(), 0);
      if (name === 'Comparador de equipamentos' || name === 'Relatório preventivo') {
        const label = name === 'Comparador de equipamentos' ? 'Baixar comparação em CSV' : 'Baixar relatório com fontes e limites';
        const downloadPromise = page.waitForEvent('download');
        await page.getByRole('button', { name: label, exact: true }).click();
        const download = await downloadPromise;
        const dest = path.join(output, name === 'Comparador de equipamentos' ? 'comparacao_navegador.csv' : 'relatorio_navegador.md');
        await download.saveAs(dest);
        const content = fs.readFileSync(dest, 'utf8');
        assert.match(content, /VC101-/);
        assert.match(content, /snapshot-/);
        if (name === 'Relatório preventivo') assert.match(content, /Taxa B\/A bloqueada/);
        return { filename: download.suggestedFilename(), bytes: Buffer.byteLength(content), export_verified: true };
      }
      return { heading };
    });
  }
  await page.getByRole('radio', { name: 'Visão geral', exact: true }).check({ force: true });
  await page.getByRole('heading', { name: 'Laguna, km 304,000: maior índice do filtro', exact: true }).waitFor();
  for (const width of [320, 390, 768, 1366]) {
    await check('Refluxo e cabeçalho a ' + width + ' CSS px', async () => {
      await page.setViewportSize({ width, height: 936 });
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.getByTestId('stMain').evaluate(n => n.scrollTo(0, 0));
      await page.waitForTimeout(300); // aguardar resize do canvas, sem medir carregamento.
      const geometry = await page.evaluate(() => {
        const intro = [...document.querySelectorAll('[data-testid="stCaptionContainer"]')].find(n => n.textContent.includes('BR-101 SUL'));
        const header = document.querySelector('header');
        return { viewport: window.innerWidth, document_width: document.documentElement.scrollWidth,
          intro_top: intro.getBoundingClientRect().top, header_bottom: header.getBoundingClientRect().bottom };
      });
      assert.ok(geometry.document_width <= geometry.viewport + 1, JSON.stringify(geometry));
      assert.ok(geometry.intro_top >= geometry.header_bottom, JSON.stringify(geometry));
      await page.screenshot({ path: path.join(output, `viewport_${width}.jpg`), quality: 75 });
      return geometry;
    });
  }
  await check('Sem erros JavaScript de página', async () => { assert.deepEqual(browserErrors, []); return browserErrors; });
  await browser.close();
})().catch(async error => { console.error(error); process.exitCode = 1; if (browser) await browser.close(); })
  .finally(() => { result.finished_at_utc = new Date().toISOString(); fs.writeFileSync(path.join(output, 'navegador.json'), JSON.stringify(result, null, 2) + '\n'); });
