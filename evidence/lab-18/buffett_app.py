"""Run: python3 -m streamlit run buffett_app.py"""
import json
from pathlib import Path
import sys

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'skill/buffett-sec/scripts'))
from buffett import (clean_ticker, download, evidence, fingerprint, report, screen,
                     table_rows, unsupported_numbers)


def main():
    st.set_page_config(page_title='Buffett Business Screen', layout='wide')
    st.title('Buffett Business Screen')
    st.caption('Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.')
    ticker_input = st.sidebar.text_input('Ticker', 'COST')
    mode = st.sidebar.radio('Data source', ['Saved SEC download', 'Live SEC download'])
    st.sidebar.caption('Saved downloads reproduce the submitted run. Live downloads require internet access.')
    try:
        ticker = clean_ticker(ticker_input)
        if mode == 'Saved SEC download':
            path = ROOT / 'data' / f'{ticker}_companyfacts.json'
            facts = json.loads(path.read_text())
            source = json.loads(path.with_suffix('.source.json').read_text())
            st.caption(f"Saved SEC download retrieved {source['retrieved_utc']}; {source['url']}")
        else:
            facts = download(ticker, ROOT / 'data')
        result = screen(facts, ticker)
    except (requests.RequestException, ValueError, KeyError, OSError) as error:
        st.error(f'Could not load {ticker_input}: {error}')
        st.info('For another ticker, select Live SEC download or run the skill to save its SEC facts first.')
        return
    st.subheader(f"{ticker} — {result['company']}")
    if len(result['rows']) < 5:
        st.warning('Fewer than five fiscal years are available; the checks are not known.')
    frame = pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'],
                           'Owner earnings': None if r['owner_earnings'] is None else r['owner_earnings']/1e6,
                           'Net income': None if r['net_income'] is None else r['net_income']/1e6}
                          for r in result['rows']]).set_index('Fiscal year end')
    st.line_chart(frame, x_label='Fiscal year end', y_label='USD millions')
    st.caption('Missing owner earnings remain gaps, never zero. Owner earnings = operating cash flow − capital spending.')
    st.dataframe(pd.DataFrame(table_rows(result)), hide_index=True, width='stretch')
    st.caption('Dollar amounts in USD millions. ROE = net income / year-end equity, expressed as percent.')
    st.subheader('Three checks')
    st.dataframe(pd.DataFrame(result['checks'].items(), columns=['Check', 'Result']), hide_index=True, width='stretch')
    with st.expander('XBRL tags and filing provenance'):
        st.text(report(result))
    st.download_button('Download computed evidence', report(result), f'{ticker}_run.txt')
    memo_path = ROOT / 'memos' / f'{ticker}_memo.md'
    binding_path = memo_path.with_suffix('.evidence.json')
    saved = ''
    if memo_path.exists() and binding_path.exists():
        if json.loads(binding_path.read_text()).get('fingerprint') == fingerprint(result):
            saved = memo_path.read_text()
        else:
            st.warning('Saved memo uses different financial evidence. Run the skill again for these facts.')
    st.subheader('Buffett memo')
    if not saved:
        st.info('Run the Buffett skill on this ticker and save its memo, or paste a model-written draft below. The app computes; the AI writes the judgment.')
    memo = st.text_area('Memo draft / number probe', saved, height=290, key=f'memo_{ticker}_{fingerprint(result)}')
    if memo:
        st.markdown(memo)
        flags = unsupported_numbers(memo, result)
        if flags:
            st.error('Unsupported memo numbers: '+', '.join(f['number'] for f in flags))
            st.dataframe(pd.DataFrame(flags), hide_index=True)
        else:
            st.success('Every numeric token in the memo appears in the printed financial evidence.')
            st.download_button('Download memo', memo, f'{ticker}_memo.md')
        st.caption('This checks numeric support, not whether the prose attaches a number to the correct metric or proves a moat.')
    with st.expander('Financial evidence authorized for the memo'):
        st.text(evidence(result))


if __name__ == '__main__':
    main()
