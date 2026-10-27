"""Contratos de cálculo e regressões numéricas do snapshot real incluído."""
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

from src.antt import (annual_table, monthly_table, cohort_ids, context_table,
                      equipment_table, passages, weighted_index)
from src.sentinel_analysis import (INSUFFICIENT, REPEATED, coverage_sensitivity,
                                   investigation_table, quality_evidence)

ROOT = Path(__file__).resolve().parents[1]


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.daily = pd.read_parquet(ROOT/'dados_tratados/antt_diario.parquet')
        cls.meta = pd.read_parquet(ROOT/'dados_tratados/antt_equipamentos.parquet')
        cls.accidents = pd.read_parquet(ROOT/'dados_tratados/antt_acidentes.parquet')

    def test_invalid_ratio_is_unavailable(self):
        for high, total in [(1, 0), (1, -1), (-1, 1), (2, 1), (np.nan, 1),
                            (1, np.nan), (np.inf, 1), (1, np.inf), (None, 1)]:
            with self.subTest(high=high, total=total):
                self.assertTrue(np.isnan(weighted_index(high, total)))
        self.assertEqual(weighted_index(0, 5), 0)
        self.assertEqual(weighted_index(3, 100), 300)

    def test_aggregation_is_ratio_of_sums(self):
        one = self.daily.head(2).copy()
        one['passagens'] = [100, 1000]
        one['altas'] = [10, 1]
        one['identificador'] = one.identificador.iloc[0]
        eq = equipment_table(one, self.meta, [int(one.ano.iloc[0])])
        self.assertAlmostEqual(eq.por_10_mil.iloc[0], 100)
        self.assertEqual(eq.passagens.iloc[0], 1100)

    def test_reference_snapshot_and_derived_tables(self):
        annual = annual_table(self.daily)
        pd.testing.assert_frame_equal(annual, pd.read_parquet(ROOT/'dados_tratados/antt_anual.parquet'))
        pd.testing.assert_frame_equal(monthly_table(self.daily), pd.read_parquet(ROOT/'dados_tratados/antt_mensal.parquet'))
        ids = cohort_ids(annual)
        eq = equipment_table(self.daily.loc[self.daily.identificador.isin(ids)], self.meta)
        self.assertEqual(len(eq), 20)
        self.assertEqual(eq.passagens.sum(), 226870300)
        self.assertEqual(eq.altas.sum(), 57163)
        self.assertAlmostEqual(weighted_index(eq.altas.sum(), eq.passagens.sum()), 2.519633464583068)

    def test_daily_contract_rejects_duplicates_and_inconsistent_counts(self):
        one = self.daily.head(1).copy()
        with self.assertRaises(ValueError):
            annual_table(pd.concat([one, one]))
        for column, value in [('passagens', -1), ('altas', np.inf), ('altas', .5), ('passagens', np.nan)]:
            altered = one.copy()
            altered[column] = value
            with self.subTest(column=column, value=value), self.assertRaises(ValueError):
                annual_table(altered)
        one['ano'] = 1999
        with self.assertRaises(ValueError):
            annual_table(one)

    def test_zero_denominator_is_not_zero_index(self):
        one = self.daily.head(1).copy()
        one[['passagens', 'altas']] = 0
        annual = annual_table(one)
        self.assertTrue(np.isnan(annual.por_10_mil.iloc[0]))
        self.assertEqual(cohort_ids(annual), [])

    def test_location_join_rejects_missing_or_ambiguous_id(self):
        one = self.daily.head(1)
        meta = self.meta.loc[~self.meta.identificador.isin(one.identificador)]
        with self.assertRaises(ValueError):
            equipment_table(one, meta, one.ano.unique())
        with self.assertRaises(ValueError):
            equipment_table(one, pd.concat([self.meta, self.meta.head(1)]), one.ano.unique())
        meta = self.meta.copy()
        meta.loc[meta.identificador.isin(one.identificador), 'km'] = np.nan
        with self.assertRaises(ValueError):
            equipment_table(one, meta, one.ano.unique())

    def test_missing_current_speed_reference_does_not_hide_real_point(self):
        eq = equipment_table(self.daily.loc[self.daily.identificador.eq('VC101-20')], self.meta)
        self.assertEqual(len(eq), 1)
        self.assertTrue(eq.limite_leve_ref_2026.isna().all())
        self.assertEqual(eq.km.iloc[0], 252)

    def test_raw_unknown_bands_invalid_counts_and_locations(self):
        raw = pd.DataFrame([dict(identificador='A', data_da_passagem='01/01/2024',
            velocidade='121 - 140 ', volume_total='3', km_m='391.94',
            sentido_da_passagem='Crescente', faixa_da_passagem='1',
            tipo_de_veiculo='Não classificado', latitude='-28.8', longitude='-49.3')])
        valid = passages(raw)
        self.assertEqual(valid.quantidade_alta.sum(), 3)
        for column, value in [('velocidade', 'nova faixa'), ('volume_total', '-1'),
                              ('volume_total', '1.1'), ('volume_total', 'inf'),
                              ('identificador', ''), ('km_m', 'inf')]:
            modified = raw.copy()
            modified[column] = value
            with self.subTest(column=column, value=value), self.assertRaises(ValueError):
                passages(modified)
        with self.assertRaises(ValueError):
            passages(pd.concat([raw, raw]))
        changed = pd.concat([raw, raw.assign(km_m='390')])
        with self.assertRaises(ValueError):
            passages(changed)

    def test_investigation_uses_fixed_reference_and_reproduces_four_ids(self):
        result = investigation_table(self.daily, self.meta)
        repeated = result.loc[result.estado.eq(REPEATED)]
        self.assertEqual(set(repeated.identificador), {'VC101-39', 'VC101-4', 'VC101-7', 'VC101-9'})
        self.assertTrue(result.referencia_equipamentos.eq(20).all())
        self.assertAlmostEqual(result.q75_2024.iloc[0], 4.0728398313450045)
        self.assertAlmostEqual(result.q75_2025.iloc[0], 3.6728028445734275)
        selected = result.loc[result.identificador.eq('VC101-9')]
        self.assertAlmostEqual(selected.q75_2024.iloc[0], result.q75_2024.iloc[0])
        self.assertEqual(len(result), 42)

    def test_ineligible_point_and_other_years_have_no_safety_class(self):
        result = investigation_table(self.daily, self.meta)
        criciuma = result.loc[result.identificador.eq('VC101-30')].iloc[0]
        self.assertEqual(criciuma.estado, INSUFFICIENT)
        self.assertEqual(criciuma.dias_2024, 306)
        self.assertEqual(criciuma.dias_2025, 332)
        self.assertAlmostEqual(criciuma.indice_2024, 2.8555186690249426)
        other = investigation_table(self.daily, self.meta, [2026])
        self.assertTrue(other.estado.eq(INSUFFICIENT).all())
        self.assertFalse(other.padrao_repetido.any())

    def test_zero_annual_denominator_excluded_from_reference_and_rule(self):
        altered = self.daily.copy()
        invalid = altered.identificador.eq('VC101-9') & altered.ano.eq(2024)
        altered.loc[invalid, ['passagens', 'altas']] = 0
        result = investigation_table(altered, self.meta)
        point = result.loc[result.identificador.eq('VC101-9')].iloc[0]
        self.assertEqual(point.estado, INSUFFICIENT)
        self.assertFalse(point.elegivel)
        self.assertEqual(point.referencia_equipamentos, 19)

    def test_quartile_ties_are_included_without_forcing_four_points(self):
        altered = self.daily.copy()
        altered['altas'] = 0
        result = investigation_table(altered, self.meta)
        self.assertEqual(int(result.padrao_repetido.sum()), 20)
        self.assertTrue(result.loc[result.elegivel, 'q75_2024'].eq(0).all())

    def test_quality_evidence_keeps_documented_day_and_all_records(self):
        quality = quality_evidence(self.daily)
        case = quality.loc[quality.caso_documentado]
        self.assertEqual(len(quality), len(self.daily))
        self.assertEqual(case.identificador.nunique(), 36)
        self.assertEqual(case.passagens.sum(), 698)
        criciuma = case.loc[case.identificador.eq('VC101-30')].iloc[0]
        self.assertEqual(criciuma.passagens, 22)
        self.assertEqual(criciuma.faixas_publicadas, 2)
        self.assertEqual(criciuma.mediana_anual, 14745.5)
        self.assertIn('Não confirmada', criciuma.causa)
        self.assertEqual(quality.passagens.sum(), self.daily.passagens.sum())

    def test_sensitivity_changes_population_without_altering_snapshot(self):
        result = coverage_sensitivity(self.daily, self.meta)
        self.assertEqual(result.equipamentos.tolist(), [27, 20, 9])
        for actual, expected in zip(result.por_10_mil, [2.539985, 2.519633, 3.522462]):
            self.assertAlmostEqual(actual, expected, places=6)

    def test_context_matches_original_and_does_not_multiply_accidents(self):
        ids = cohort_ids(annual_table(self.daily))
        context = context_table(self.daily, self.meta, self.accidents, ids)
        stored = pd.read_parquet(ROOT/'dados_tratados/antt_contexto_5km.parquet')
        pd.testing.assert_frame_equal(context, stored)
        self.assertEqual(len(context), 16)
        self.assertEqual(context.registros_acidentes.sum(), 1276)
        self.assertTrue(context.registros_acidentes.ge(context.combinacoes_data_km).all())

    def test_absent_accident_source_year_never_becomes_zero(self):
        with self.assertRaisesRegex(ValueError, 'ausência não é zero'):
            context_table(self.daily, self.meta, self.accidents, ['VC101-30'], [2026])
        with self.assertRaises(ValueError):
            context_table(self.daily, self.meta, self.accidents, ['VC101-30'], width=0)


if __name__ == '__main__':
    unittest.main()
