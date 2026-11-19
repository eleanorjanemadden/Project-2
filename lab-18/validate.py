"""Reproduce course answers, provenance, edge cases and Streamlit probes."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'skill/buffett-sec/scripts'))
from buffett import (TAGS, annual, choose_fact, evidence, fingerprint, records,
                     screen, table_rows, unsupported_numbers, year_row)


def load(ticker):
    return json.loads((ROOT / 'data' / f'{ticker}_companyfacts.json').read_text())


class LabChecks(unittest.TestCase):
    def test_costco_course_answer(self):
        # Independent expected values are parsed from the instructor's table, not our output.
        text = (ROOT / 'instructions/lab-18-legend-investor-as-skill.md').read_text()
        expected = []
        for line in text.splitlines():
            if line.startswith('| 202'):
                cells = [v.strip() for v in line.strip('|').split('|')]
                expected.append([cells[0]]+[float(v.replace(',', '')) for v in cells[1:]])
        result = screen(load('COST'), 'COST')
        keys = ['revenue', 'net_income', 'operating_cash_flow', 'capital_spending', 'equity', 'roe', 'owner_earnings']
        differences = []
        self.assertEqual(len(expected), 5)
        for row, exp in zip(result['rows'], expected):
            self.assertEqual(row['fiscal_year_end'], exp[0])
            for metric, want in zip(keys, exp[1:]):
                got = round(row[metric], 1) if metric == 'roe' else row[metric]/1e6
                differences.append([exp[0], metric, want, got, got-want])
                self.assertEqual(got, want, (exp[0], metric))
        self.assertEqual(list(result['checks'].values()), ['pass']*3)
        self.assertGreater(result['rows'][-1]['owner_earnings'], result['rows'][0]['owner_earnings'])
        self.assertGreater(result['rows'][-1]['net_income'], result['rows'][0]['net_income'])
        with (ROOT / 'outputs/known_answer_comparison.csv').open('w') as out:
            w = csv.writer(out); w.writerow(['fiscal_year_end','metric','expected','actual','difference']); w.writerows(differences)

    def test_raw_sources_and_latest_filings(self):
        for ticker in ['COST', 'JPM']:
            path = ROOT / 'data' / f'{ticker}_companyfacts.json'
            source = json.loads(path.with_suffix('.source.json').read_text())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source['sha256'])
            self.assertIn('madden42@purdue.edu', source['user_agent'])
            facts = load(ticker)
            for row in screen(facts, ticker)['rows']:
                for metric in TAGS:
                    p = row['provenance'][metric]
                    if 'end' in p:
                        self.assertEqual(p['form'], '10-K')
                        tag = p['tag'].split(':')[1]
                        candidates = [x for x in records(facts, tag) if x.get('end') == p['end'] and x.get('form') == '10-K' and (annual(x) if metric != 'equity' else not x.get('start'))]
                        self.assertEqual(p['filed'], max(x['filed'] for x in candidates))
                        if metric != 'equity': self.assertTrue(annual(p))

    def test_jpm_gaps(self):
        result = screen(load('JPM'), 'JPM')
        for row in result['rows']:
            self.assertIsNone(row['capital_spending']); self.assertIsNone(row['owner_earnings'])
        self.assertEqual(list(result['checks'].values()), ['fail', 'not known', 'not known'])
        self.assertIn('cannot judge owner earnings', (ROOT / 'memos/JPM_memo.md').read_text())

    def test_missing_equity_and_flow(self):
        facts = load('COST')
        end = '2026-08-30'
        for equity in [0, -100]:
            changed = copy.deepcopy(facts)
            for x in records(changed, 'StockholdersEquity'):
                if x['end'] == end: x['val'] = equity
            row = year_row(changed, end)
            self.assertIsNone(row['roe'])
            self.assertEqual(list(screen(changed, 'COST')['checks'].values())[0], 'not known')
        changed = copy.deepcopy(facts)
        del changed['facts']['us-gaap']['NetCashProvidedByUsedInOperatingActivities']
        self.assertIsNone(year_row(changed, end)['owner_earnings'])
        self.assertEqual(list(screen(changed, 'COST')['checks'].values())[1:], ['not known', 'not known'])

    def test_tag_priority_annual_and_latest(self):
        def f(value, filed, form='10-K', start='2025-09-01'):
            return {'start':start,'end':'2026-08-30','val':value,'filed':filed,'form':form,'accn':filed}
        # Small synthetic input tests mechanics only; these are never financial evidence.
        facts = {'facts': {'us-gaap': {
            'RevenueFromContractWithCustomerExcludingAssessedTax': {'units': {'USD': [f(100,'2026-09-01'),f(110,'2026-10-07'),f(999,'2026-10-08','10-Q'),f(888,'2026-10-09',start='2026-06-01')]}},
            'Revenues': {'units': {'USD': [f(200,'2026-11-01')]}}
        }}}
        tags = TAGS['revenue']
        self.assertEqual(choose_fact(facts,tags,'2026-08-30',True)[0],110)
        del facts['facts']['us-gaap'][tags[0]]
        self.assertEqual(choose_fact(facts,tags,'2026-08-30',True)[0],200)
        self.assertEqual(choose_fact(facts,tags,'2025-08-31',True)[0],None)

    def test_memo_numbers_and_binding(self):
        for ticker in ['COST','JPM']:
            result = screen(load(ticker),ticker)
            memo = (ROOT / 'memos' / f'{ticker}_memo.md').read_text()
            self.assertEqual(unsupported_numbers(memo,result),[])
            binding=json.loads((ROOT/'memos'/f'{ticker}_memo.evidence.json').read_text())
            self.assertEqual(binding['fingerprint'],fingerprint(result))
        result = screen(load('COST'),'COST')
        flags = unsupported_numbers('Invented ROE 40.0%; invented dollars 123,456; repeated 40.0%.', result)
        self.assertEqual([x['number'] for x in flags],['40.0%','123,456','40.0%'])
        self.assertEqual(unsupported_numbers('ROE 28.30%; owner earnings $9,382 million.',result),[])
        self.assertTrue(unsupported_numbers('ROE 9382%',result))

    def test_streamlit_app(self):
        from streamlit.testing.v1 import AppTest
        app=AppTest.from_file(str(ROOT/'buffett_app.py'),default_timeout=15).run()
        self.assertFalse(app.exception)
        self.assertIn('Data from SEC EDGAR',app.caption[0].value)
        self.assertEqual(len(app.dataframe),2)
        self.assertTrue(len(app.get('vega_lite_chart')))
        self.assertEqual(app.dataframe[0].value.iloc[-1]['Owner earnings'],'9,382')
        self.assertTrue(app.success)
        app.text_area[0].set_value(app.text_area[0].value+'\nInvented ROE: 40.0%.').run()
        self.assertIn('40.0%',app.error[0].value)
        (ROOT/'outputs/number_probe.txt').write_text(app.error[0].value+'\n')
        app.text_input[0].set_value('JPM').run()
        self.assertFalse(app.exception)
        self.assertEqual(app.dataframe[0].value.iloc[-1]['Capital spending'],'not found')
        self.assertIn('cannot judge owner earnings', app.text_area[0].value)
        app.text_input[0].set_value('../bad').run()
        self.assertFalse(app.exception); self.assertTrue(app.error)
        app.text_input[0].set_value('ZZZZZZ').run()
        self.assertFalse(app.exception); self.assertTrue(app.error)


if __name__ == '__main__':
    unittest.main(verbosity=2)
