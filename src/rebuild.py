"""Reprodução isolada; não sobrescreve o snapshot em uso."""
import argparse
import json
import zipfile
from pathlib import Path
import pandas as pd
from config import ROOT
from src import antt
from src.prf import build_prf
from src.data_package import generate,validate,digest

def rebuild(raw_zip,output):
    output=Path(output).resolve()
    if output==ROOT or ROOT in output.parents and output.name in ['dados_tratados','dados_brutos','relatorios']: raise ValueError('Use diretório isolado para reconstrução.')
    if output.exists() and any(output.iterdir()): raise ValueError('Diretório de saída deve estar vazio.')
    output.mkdir(parents=True,exist_ok=True)
    raw=output/'dados_brutos';raw.mkdir()
    expected=set(antt.FILES.values())|{'coleta_20261026T224903Z.json','manifesto_prf.json','datatran2024.zip','datatran2025.zip'}
    with zipfile.ZipFile(raw_zip) as z:
        if not expected.issubset(z.namelist()):raise ValueError('Pacote bruto incompleto.')
        for name in expected:(raw/name).write_bytes(z.read(name))
    old=(antt.RAW,antt.PROCESSED,antt.REPORTS)
    try:
        antt.RAW=raw;antt.PROCESSED=output/'dados_tratados';antt.REPORTS=output/'relatorios'
        antt.build()
        prf,audit=build_prf(raw,antt.PROCESSED)
    finally:antt.RAW,antt.PROCESSED,antt.REPORTS=old
    generate(output);validate(output)
    comparisons={}
    for f in (output/'dados_tratados').glob('*.parquet'):
        reference=ROOT/'dados_tratados'/f.name
        if reference.exists():
            a,b=pd.read_parquet(reference),pd.read_parquet(f)
            try:pd.testing.assert_frame_equal(a,b,check_dtype=True);semantic=True
            except AssertionError: semantic=False
            comparisons[f.name]={'identico_bytes':digest(f)==digest(reference),'identico_semantico':semantic,'linhas':len(b)}
    (output/'comparacao.json').write_text(json.dumps(comparisons,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return comparisons

def main():
    p=argparse.ArgumentParser();p.add_argument('--raw-zip',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(rebuild(a.raw_zip,a.output),indent=2))
if __name__=='__main__':main()
