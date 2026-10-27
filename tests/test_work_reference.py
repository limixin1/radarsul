"""Regressões contra recálculos independentes recebidos no ZIP Work.

Fixtures copiadas sem alteração; não são resultados gerados por src.antt.
Os CSV brutos não estão disponíveis: estas verificações cobrem o snapshot tratado.
"""
from pathlib import Path
import unittest
import pandas as pd
from src.antt import annual_table, monthly_table, equipment_table, cohort_ids, context_table
from src.sentinel_data import load_snapshot

FIXTURES = Path(__file__).parent/'fixtures/work_2026-10-27'


class WorkReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames, _ = load_snapshot()

    def assert_reference(self, actual, file, keys, rename):
        reference = pd.read_csv(FIXTURES/file).rename(columns=rename)
        actual = actual[reference.columns]
        pd.testing.assert_frame_equal(actual.sort_values(keys).reset_index(drop=True),
                                      reference.sort_values(keys).reset_index(drop=True),
                                      check_dtype=False, rtol=1e-12, atol=1e-12)

    def test_all_annual_equipment_values(self):
        self.assert_reference(annual_table(self.frames['diario']), 'anual_recalculado.csv',
                              ['identificador','ano'], {'cobertura':'cobertura_dias','indice':'por_10_mil'})

    def test_all_monthly_equipment_values(self):
        self.assert_reference(monthly_table(self.frames['diario']), 'mensal_recalculado.csv',
                              ['identificador','mes'], {'cobertura':'cobertura_dias','indice':'por_10_mil'})

    def test_ranking_fixed_reference(self):
        ids = cohort_ids(self.frames['anual'])
        eq = equipment_table(self.frames['diario'].loc[lambda d:d.identificador.isin(ids)], self.frames['equipamentos'])
        self.assert_reference(eq, 'ranking_coorte.csv', ['identificador'],
                              {'kms':'km_distintos','sentidos':'sentidos_distintos','indice':'por_10_mil'})

    def test_common_date_accident_counts(self):
        ctx = context_table(self.frames['diario'], self.frames['equipamentos'], self.frames['acidentes'], cohort_ids(self.frames['anual']))
        self.assert_reference(ctx, 'contexto_5km.csv', ['segmento_inicio'],
                              {'seg':'segmento_inicio','dias':'dias_comuns','indice':'por_10_mil',
                               'registros':'registros_acidentes','combinacoes':'combinacoes_data_km'})
