import sys, pandas as pd
sys.path.insert(0, "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/weights_equal")
import weights_summaries as ws
from multiprocessing import Pool
O = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/ofat_pa_2026-11-09/"
jobs = [('ofat', 'pa_lo', 'pa_lo', 'r0', O + 'pa_lo/r0/output/'), ('ofat', 'pa_lo', 'pa_lo', 'r1', O + 'pa_lo/r1/output/'), ('ofat', 'pa_lo', 'pa_lo', 'r2', O + 'pa_lo/r2/output/'), ('ofat', 'pa_hi', 'pa_hi', 'r0', O + 'pa_hi/r0/output/'), ('ofat', 'pa_hi', 'pa_hi', 'r1', O + 'pa_hi/r1/output/'), ('ofat', 'pa_hi', 'pa_hi', 'r2', O + 'pa_hi/r2/output/'), ('ofat', 'pa_lo_theta1m', 'pa_lo_theta1m', 'r0', O + 'pa_lo_theta1m/r0/output/'), ('ofat', 'pa_lo_theta1m', 'pa_lo_theta1m', 'r1', O + 'pa_lo_theta1m/r1/output/'), ('ofat', 'pa_lo_theta1m', 'pa_lo_theta1m', 'r2', O + 'pa_lo_theta1m/r2/output/'), ('ofat', 'pa_hi_theta1m', 'pa_hi_theta1m', 'r0', O + 'pa_hi_theta1m/r0/output/'), ('ofat', 'pa_hi_theta1m', 'pa_hi_theta1m', 'r1', O + 'pa_hi_theta1m/r1/output/'), ('ofat', 'pa_hi_theta1m', 'pa_hi_theta1m', 'r2', O + 'pa_hi_theta1m/r2/output/')]
with Pool(12) as p: rows = p.map(ws.one, jobs)
pd.DataFrame(rows).round(4).to_csv(O + "ofat_summaries.csv", index=False)
print(pd.DataFrame(rows).set_index("group").T.round(3).to_string())
