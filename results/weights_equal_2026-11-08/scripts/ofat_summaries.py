import sys, pandas as pd
sys.path.insert(0, "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/weights_equal")
import weights_summaries as ws
from multiprocessing import Pool
O = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/ofat_2026-11-08/"
jobs = [('ofat', 'fit_lo', 'fit_lo', 'r0', O + 'fit_lo/r0/output/'), ('ofat', 'fit_hi', 'fit_hi', 'r0', O + 'fit_hi/r0/output/'), ('ofat', 'fit_hi', 'fit_hi', 'r1', O + 'fit_hi/r1/output/'), ('ofat', 'fit_hi', 'fit_hi', 'r2', O + 'fit_hi/r2/output/'), ('ofat', 'nrg_and_theta50', 'nrg_and_theta50', 'r0', O + 'nrg_and_theta50/r0/output/'), ('ofat', 'nrg_and_theta50', 'nrg_and_theta50', 'r1', O + 'nrg_and_theta50/r1/output/'), ('ofat', 'nrg_and_theta50', 'nrg_and_theta50', 'r2', O + 'nrg_and_theta50/r2/output/'), ('ofat', 'fit_lo_theta1m', 'fit_lo_theta1m', 'r0', O + 'fit_lo_theta1m/r0/output/'), ('ofat', 'fit_hi_theta1m', 'fit_hi_theta1m', 'r0', O + 'fit_hi_theta1m/r0/output/')]
with Pool(9) as p: rows = p.map(ws.one, jobs)
pd.DataFrame(rows).round(4).to_csv(O + "ofat_summaries.csv", index=False)
print(pd.DataFrame(rows).set_index("group").T.round(3).to_string())
