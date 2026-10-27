"""Contratos de exportação: o relatório precisa ser verificável fora da UI."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.antt_report import report
from src.sentinel_sources import (_snapshot_id, SNAPSHOT_ID, application_version, format_number,
                                  source_catalog, sources_markdown)

ROOT = Path(__file__).resolve().parents[1]


class SourceTests(unittest.TestCase):
    def test_catalog_links_and_limits(self):
        catalog = source_catalog()
        self.assertEqual([r['code'] for r in catalog], list('ABCD'))
        for r in catalog:
            self.assertTrue(r['csv_url'].startswith('https://dados.antt.gov.br/'))
            self.assertIn('/download/', r['dictionary_url'])
            self.assertEqual(len(r['sha256']), 64)
            self.assertIn('novo download não confirmado', r['status'])
        self.assertIn('Taxa B/A bloqueada', sources_markdown())
        self.assertIn('HTTP 200 com HTML', sources_markdown())

    def test_snapshot_uses_data_hashes(self):
        manifest = json.loads((ROOT/'MANIFESTO_PUBLICACAO.json').read_text())
        entries = sorted((r['caminho'], r['sha256']) for r in manifest['arquivos']
                         if r['caminho'].startswith('dados_tratados/') and r['caminho'].endswith('.parquet'))
        self.assertEqual(len(entries), 9)
        digest = hashlib.sha256('\n'.join(f'{p}:{h}' for p,h in entries).encode()).hexdigest()[:16]
        self.assertEqual(SNAPSHOT_ID, 'snapshot-'+digest)

    def test_catalog_matches_filename_not_record_order(self):
        records = json.loads((ROOT/'dados_brutos/coleta_20261026T224903Z.json').read_text())
        with patch.object(Path, 'read_text', return_value=json.dumps(records[::-1])):
            catalog = source_catalog()
        self.assertTrue(catalog[0]['csv_url'].endswith('/volume-radar-viacosteira.csv'))
        self.assertEqual(catalog[0]['sha256'], records[0]['sha256'])

    def test_corrupt_manifest_does_not_crash_module_identification(self):
        with patch.object(Path, 'read_text', return_value='<html>not json</html>'):
            self.assertEqual(_snapshot_id(), 'snapshot não identificado')

    def test_format_number_does_not_hide_missing(self):
        self.assertEqual(format_number(12345.678, 2), '12.345,68')
        self.assertEqual(format_number(12, 0), '12')
        for value in [None, np.nan, np.inf, -np.inf]:
            self.assertEqual(format_number(value), 'indisponível')

    def test_version_reads_render_commit_without_assuming_deploy(self):
        with patch.dict('os.environ', {'RENDER_GIT_COMMIT': 'a'*40}):
            self.assertEqual(application_version(), 'a'*12)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames = {n:pd.read_parquet(ROOT/'dados_tratados'/f'antt_{n}.parquet')
                      for n in ['diario','equipamentos','anual','possiveis_diario']}

    def make_report(self, daily, **kwargs):
        return report(daily, self.frames['equipamentos'], self.frames['anual'],
                      self.frames['possiveis_diario'], 'Criciúma', **kwargs)

    def test_criciuma_recomputes_annual_and_has_sources(self):
        daily = self.frames['diario'].loc[lambda d:d.identificador.eq('VC101-30') & d.ano.eq(2024)].head(2)
        result = self.make_report(daily, years=[2024,2026], scope={'sentidos':['Crescente']})
        self.assertIn('Anos solicitados:** 2024, 2026', result)
        self.assertIn('Anos observados:** 2024', result)
        self.assertIn('391,940', result)
        self.assertIn('Crescente', result)
        self.assertIn(format_number(daily.passagens.sum(), 0), result)
        # Annual evidence must refer to these two days, not the complete precomputed year.
        self.assertIn('| 2 | 366 |', result)
        self.assertNotIn('4.549.086', result)
        self.assertIn('base completa A não foi fornecida', result)
        self.assertIn('Contexto de acidentes não calculado', result)
        for r in source_catalog():
            self.assertIn(r['csv_url'], result)
            self.assertIn(r['sha256'], result)

    def test_b_uses_id_date_intersection(self):
        daily = self.frames['diario'].loc[lambda d:d.identificador.eq('VC101-30') & d.ano.eq(2024)].head(1)
        selected_b = self.frames['possiveis_diario'].merge(daily[['identificador','data']],on=['identificador','data'])
        result = self.make_report(daily)
        if not selected_b.empty:
            self.assertIn(format_number(selected_b.possiveis.sum(),0)+' contagens publicadas de B', result)
        self.assertIn('Taxa B/A bloqueada', result)

    def test_empty_selection_keeps_scope_and_no_metrics(self):
        result = self.make_report(self.frames['diario'].iloc[0:0], years=[2026])
        self.assertIn('Anos solicitados:** 2026', result)
        self.assertIn('Sem registros para o filtro', result)
        self.assertIn(SNAPSHOT_ID, result)
        self.assertNotIn('| N —', result)

    def test_b_absence_is_unavailable_not_zero(self):
        daily = self.frames['diario'].loc[lambda d:d.identificador.eq('VC101-30')].head(1)
        empty_b = self.frames['possiveis_diario'].iloc[0:0]
        result = report(daily, self.frames['equipamentos'], self.frames['anual'], empty_b)
        self.assertIn('Contagem indisponível; não equivale a zero infrações', result)

    def test_fixed_reference_and_local_quality_in_report(self):
        daily = self.frames['diario'].loc[lambda d:d.identificador.eq('VC101-30') & d.ano.isin([2024,2025])]
        result = self.make_report(daily, years=[2024,2025], all_daily=self.frames['diario'])
        self.assertIn('VC101-30 — Dados insuficientes para a regra', result)
        self.assertIn('Referência fixa: 20 pontos', result)
        self.assertIn('4,072840', result)
        self.assertIn('3,672803', result)
        self.assertIn('29/08/2025', result)
        self.assertIn('contagens publicadas: 22', result)
        self.assertIn('Causa não confirmada', result)

    def test_repeated_pattern_narrative_is_evidence_specific(self):
        daily = self.frames['diario'].loc[lambda d:d.identificador.eq('VC101-4') & d.ano.isin([2024,2025])]
        result = self.make_report(daily, all_daily=self.frames['diario'])
        self.assertIn('VC101-4 — Padrão repetido para investigação', result)
        self.assertIn('Evidência do ponto no snapshot completo', result)
        self.assertIn('Q75 de 2024', result)

    def test_requested_unobserved_year_does_not_disappear_from_context(self):
        daily = self.frames['diario'].loc[lambda d:d.identificador.eq('VC101-30') & d.ano.isin([2024,2025])]
        accidents = pd.read_parquet(ROOT/'dados_tratados/antt_acidentes.parquet')
        result = self.make_report(daily, years=[2024,2025,2026], accidents=accidents)
        self.assertIn('Contexto de acidentes não calculado', result)
        self.assertNotIn('Contexto calculado em segmentos', result)

    def test_accident_context_has_actual_segment_and_no_causal_claim(self):
        daily = self.frames['diario'].loc[lambda d:d.identificador.eq('VC101-30') & d.ano.isin([2024,2025])]
        accidents = pd.read_parquet(ROOT/'dados_tratados/antt_acidentes.parquet')
        result = self.make_report(daily, accidents=accidents)
        self.assertIn('Contexto calculado em segmentos', result)
        self.assertIn('390–395 km', result)
        self.assertIn('sem', result)
        self.assertIn('interpretar associação como causalidade', result)

    def test_zero_denominator_is_unavailable(self):
        daily = self.frames['diario'].head(1).copy()
        daily['passagens'] = 0
        daily['altas'] = 0
        result = self.make_report(daily)
        self.assertIn('| Índice agregado: H / N × 10.000 | indisponível |', result)
        self.assertNotIn('| nan |', result)
        self.assertNotIn('| inf |', result)


if __name__ == '__main__':
    unittest.main()
