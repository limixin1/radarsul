import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from src.sentinel_data import load_snapshot, validate_frames, SnapshotError


def set_column(frame, name, value):
    frame[name] = value


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames, cls.summary = load_snapshot()

    def test_snapshot_and_known_totals(self):
        self.assertEqual(len(self.frames['diario']), 59168)
        self.assertEqual(self.summary['coorte_passagens'], 226870300)
        self.assertEqual(self.summary['coorte_altas'], 57163)
        self.assertEqual(len(self.frames['prf']), 1750)

    def assert_rejected(self, change):
        frames = {k: v.copy() if isinstance(v, pd.DataFrame) else v for k, v in self.frames.items()}
        summary = copy.deepcopy(self.summary)
        change(frames, summary)
        with self.assertRaises(SnapshotError):
            validate_frames(frames, summary)

    def test_duplicate_daily_key(self):
        self.assert_rejected(lambda f, s: f.__setitem__('diario', pd.concat([f['diario'], f['diario'].iloc[:1]])))

    def test_unknown_equipment(self):
        self.assert_rejected(lambda f, s: set_column(f['diario'], 'identificador', 'sem cadastro'))

    def test_date_inconsistency(self):
        self.assert_rejected(lambda f, s: set_column(f['diario'], 'ano', 1999))

    def test_invalid_numerator(self):
        self.assert_rejected(lambda f, s: set_column(f['diario'], 'altas', f['diario'].passagens+1))

    def test_fractional_count(self):
        self.assert_rejected(lambda f, s: set_column(f['diario'], 'passagens', 1.5))

    def test_missing_location(self):
        self.assert_rejected(lambda f, s: set_column(f['equipamentos'], 'municipio', None))

    def test_aggregation_drift(self):
        self.assert_rejected(lambda f, s: set_column(f['anual'], 'passagens', f['anual'].passagens+1))

    def test_cannot_enable_incompatible_ratio(self):
        self.assert_rejected(lambda f, s: s.__setitem__('taxa_possiveis_infracoes_disponivel', True))

    def test_stale_reference(self):
        self.assert_rejected(lambda f, s: s.__setitem__('coorte_ids', []))

    def test_corrupted_bytes_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'antt_diario.parquet').write_bytes(b'<html>not parquet</html>')
            with self.assertRaisesRegex(SnapshotError, 'Integridade'):
                load_snapshot(processed=d)

    def test_missing_file_is_friendly_contract_error(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(SnapshotError):
                load_snapshot(processed=d)

    def test_optional_prf_failure_does_not_break_antt(self):
        original = pd.read_parquet
        def read(path, *args, **kwargs):
            if Path(path).name == 'ocorrencias.parquet':
                raise ValueError('invalid optional file')
            return original(path, *args, **kwargs)
        with patch('src.sentinel_data.pd.read_parquet', side_effect=read):
            frames, _ = load_snapshot()
        self.assertIsNone(frames['prf'])
        self.assertIn('indisponível', frames['prf_status'])
