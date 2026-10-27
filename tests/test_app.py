"""Regressões de escopo, estados vazios, proveniência e figuras acessíveis."""
import json
from pathlib import Path
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.antt_charts import correlation_detail, monthly_display

ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    def app(self, page='Visão geral'):
        app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=90).run()
        self.ok(app)
        if page != 'Visão geral':
            app.sidebar.radio[0].set_value(page).run()
            self.ok(app)
        return app

    def ok(self, app):
        self.assertFalse(list(app.exception), [x.message for x in app.exception])
        self.assertFalse(list(app.error), [x.value for x in app.error])

    def select(self, app, key, value):
        app.multiselect(key=key).set_value(value).run()
        self.ok(app)

    def test_all_five_pages_have_native_tables_and_no_exception(self):
        app = self.app()
        for page in app.sidebar.radio[0].options:
            with self.subTest(page=page):
                app.sidebar.radio[0].set_value(page).run()
                self.ok(app)
                self.assertTrue(list(app.table))

    def test_comparator_one_id_has_one_row_and_no_persistence_chart(self):
        app = self.app('Comparador de equipamentos')
        self.select(app, 'compare_ids', ['VC101-4'])
        values = app.table[0].value
        self.assertEqual(values['Radar'].tolist(), ['VC101-4'])
        self.assertEqual(len(app.get('plotly_chart')), 0)
        self.assertTrue(any('Um ponto não permite correlação' in x.value for x in app.info))

    def test_comparator_two_ids_use_only_selected_points(self):
        app = self.app('Comparador de equipamentos')
        self.select(app, 'compare_ids', ['VC101-4', 'VC101-9'])
        spec = json.loads(app.get('plotly_chart')[0].proto.spec)
        self.assertEqual(set(spec['data'][0]['hovertext']), {'VC101-4', 'VC101-9'})
        self.assertNotIn('Spearman', spec['layout']['title']['text'])

    def test_empty_comparator_removes_chart_and_csv(self):
        app = self.app('Comparador de equipamentos')
        self.select(app, 'compare_ids', [])
        self.assertFalse(list(app.get('plotly_chart')))
        self.assertFalse(any('comparação em CSV' in x.label for x in app.get('download_button')))
        self.assertTrue(any('Selecione pelo menos um radar' in x.value for x in app.info))

    def test_history_line_and_heatmap_have_same_single_id(self):
        app = self.app('Evolução e persistência')
        self.select(app, 'history_ids', ['VC101-9'])
        charts = app.get('plotly_chart')
        line, heat = [json.loads(c.proto.spec) for c in charts]
        self.assertEqual([trace['name'] for trace in line['data']], ['VC101-9'])
        self.assertEqual(heat['data'][0]['y'], ['VC101-9'])
        self.assertEqual(set(app.table[0].value['Radar']), {'VC101-9'})

    def test_global_change_preserves_valid_ids_without_replacing_invalid_selection(self):
        app = self.app('Comparador de equipamentos')
        self.select(app, 'compare_ids', ['VC101-4'])
        app.sidebar.selectbox[0].set_value('Criciúma: VC101-30').run()
        self.ok(app)
        self.assertEqual(app.multiselect(key='compare_ids').value, [])
        self.assertFalse(list(app.get('plotly_chart')))

    def test_empty_global_filters_have_specific_messages(self):
        app = self.app()
        self.select(app, 'years', [])
        self.assertFalse(list(app.metric))
        self.assertTrue(any('pelo menos um ano' in x.value for x in app.info))
        self.select(app, 'years', [2024, 2025])
        self.select(app, 'directions', [])
        self.assertFalse(list(app.metric))
        self.assertTrue(any('pelo menos um sentido' in x.value for x in app.info))

    def test_criciuma_2026_has_dynamic_one_radar_and_181_dates(self):
        app = self.app()
        app.sidebar.selectbox[0].set_value('Criciúma: VC101-30').run()
        self.select(app, 'years', [2026])
        metrics = {m.label: m.value for m in app.metric}
        self.assertEqual(metrics['Radares com registros'], '1')
        self.assertEqual(metrics['Datas distintas no recorte (união)'], '181')
        self.assertFalse(any('Coorte fixa: 20 de 42' in c.value for c in app.caption))
        self.assertTrue(any('2026 parcial' in c.value for c in app.caption))

    def test_method_has_four_official_sources_and_unavailable_metric(self):
        app = self.app()
        text = '\n'.join(m.value for m in app.markdown) + '\n' + '\n'.join(x.value for x in app.get('text'))
        self.assertIn('10.000 × H / N', text)
        self.assertGreaterEqual(text.count('dados.antt.gov.br'), 4)
        self.assertTrue(any('Categoria veicular' in m.value for m in app.markdown))

    def test_load_failure_is_recoverable_without_stacktrace_or_nonexistent_command(self):
        source = """from unittest.mock import patch
import app_antt
app_antt.load.clear()
with patch.object(app_antt, 'load', side_effect=ValueError('sensitive internal detail')):
    app_antt.main()
"""
        app = AppTest.from_string(source, default_timeout=90).run()
        self.assertFalse(list(app.exception))
        self.assertTrue(list(app.error))
        self.assertTrue(any(x.label == 'Tentar novamente' for x in app.button))
        text = '\n'.join(x.value for x in app.error)
        self.assertNotIn('analisar.py', text)
        self.assertNotIn('sensitive internal detail', text)

    def test_2026_accident_context_is_unavailable_instead_of_zero(self):
        app = self.app('Contexto rodoviário')
        self.select(app, 'years', [2026])
        self.assertTrue(any('base de acidentes não cobre esses anos' in x.value for x in app.info))

    def test_monthly_zero_denominator_has_unavailable_state(self):
        monthly = pd.read_parquet(ROOT / 'dados_tratados' / 'antt_mensal.parquet').iloc[:1].copy()
        monthly['passagens'] = 0
        monthly['altas'] = 0
        monthly['por_10_mil'] = float('nan')
        monthly['cobertura_dias'] = 1.0
        year = int(monthly.iloc[0].mes[:4])
        result = monthly_display(monthly, [monthly.iloc[0].identificador], [year])
        observed = result.loc[result.mes.eq(monthly.iloc[0].mes)].iloc[0]
        self.assertEqual(observed.estado, 'Denominador ou índice indisponível')
        self.assertTrue(pd.isna(observed.indice_exibido))

    def test_constant_correlation_is_unavailable(self):
        self.assertEqual(correlation_detail(pd.DataFrame({'x': [1, 1], 'y': [2, 3]}), 'x', 'y'), (2, None))

    def test_nonconsecutive_years_leave_gap_in_line(self):
        monthly = pd.read_parquet(ROOT / 'dados_tratados' / 'antt_mensal.parquet')
        result = monthly_display(monthly, ['VC101-9'], [2023, 2025])
        gap = result.loc[result.mes.str.startswith('2024')]
        self.assertEqual(len(gap), 12)
        self.assertTrue(gap.indice_exibido.isna().all())
        self.assertEqual(set(gap.estado), {'Ano fora da seleção'})


if __name__ == '__main__':
    unittest.main()
