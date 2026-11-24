from pathlib import Path
import pandas as pd
from streamlit.testing.v1 import AppTest

def find(widgets, label):
    return next(w for w in widgets if w.label == label)

def show(app, name):
    assert not app.exception
    print("\n", name)
    print(app.dataframe[0].value.to_string(index=False))
    print([(m.label, m.value) for m in app.metric])
    print([e.value for e in app.error])

app = AppTest.from_file(str(Path("app.py").resolve())).run()
show(app, "Default")
find(app.checkbox, "Last 36 months").set_value(True).run()
show(app, "Last 36")
find(app.checkbox, "Last 36 months").set_value(False).run()
vt = find(app.number_input, "VT return estimate (%)")
vt.set_value(vt.value - 1).run()
show(app, "VT return down 1 pp")
app = AppTest.from_file(str(Path("app.py").resolve())).run()
find(app.number_input, "Annual additional cost assumption (bps)").set_value(15.).run()
show(app, "15 bp")
monthly = pd.read_csv("prices.csv", index_col=0).pct_change().dropna()
fixed = (monthly.mean()["BIL"] * .6 + monthly.mean()["VT"] * .4) * 12 - .0015
print(f"Fixed original 60/40 after 15 bp: {fixed:.8%}")
find(app.checkbox, "IEF reserve-eligible").set_value(False).run()
show(app, "15 bp, bills-only eligibility")
find(app.number_input, "Reserve minimum (%)").set_value(100.).run()
show(app, "15 bp, 100% BIL reserve")
print("Selectbox choices:", [(w.label, w.options) for w in app.selectbox])
