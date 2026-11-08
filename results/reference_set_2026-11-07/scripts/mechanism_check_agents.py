"""Per-agent check of the citation quota rules for a random sample of agents (replicate r0)."""
import numpy as np, pandas as pd
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"; THETA = 50; N = 2000; rng = np.random.default_rng(20261107)
def load(kind, res):
    d = f"{A}{kind}_cpm{res}/r0/output/"
    nl = pd.read_csv(d + "nodelist.csv", usecols=["node_id","type","year","alpha","out_degree","generator_node_string","fully_random_citations","cartel_id","cluster_id"], low_memory=False)
    ed = pd.read_csv(d + "edgelist.csv", dtype=np.int64)
    return nl, ed
def run(kind, res):
    nl, ed = load(kind, res)
    g = nl.groupby(["cluster_id","year"]).size().rename("n").reset_index(); g["before"] = g.groupby("cluster_id").n.cumsum() - g.n
    nl = nl.merge(g[["cluster_id","year","before"]], on=["cluster_id","year"], how="left").set_index("node_id")
    ag = nl[(nl.type == "agent") & (nl.cartel_id < 0) & (nl.alpha > 0) & (nl.out_degree >= 5)]
    out = {}
    for name, pool in (("qualified (size>=50)", ag[ag.before >= THETA]), ("not qualified (size<50)", ag[ag.before < THETA])):
        s = pool.sample(N, random_state=int(rng.integers(1 << 30)))
        sub = ed[ed.source.isin(s.index)]
        gen = s.generator_node_string.astype(int)
        yr, cl = nl.year, nl.cluster_id
        t_year = sub.target.map(yr).values; t_cl = sub.target.map(cl).values; src = sub.source.values
        a_year = s.year.reindex(src).values; a_cl = s.cluster_id.reindex(src).values; a_gen = gen.reindex(src).values
        df = pd.DataFrame({"src": src, "same_year": (t_year == a_year), "in_cl": (t_cl == a_cl) & (t_year < a_year) & (sub.target.values != a_gen), "is_gen": sub.target.values == a_gen})
        agg = df.groupby("src").agg(sy=("same_year", "sum"), k=("in_cl", "sum"), gen=("is_gen", "sum"), edges=("same_year", "size")).reindex(s.index).fillna(0)
        Q = s.out_degree - 1 - agg.sy - s.fully_random_citations
        n1 = np.floor(s.alpha * Q + 1e-9).clip(lower=0)
        # 1-hop neighbours of the generator (superset): its references plus nodes citing it that were published before the agent
        G = set(gen.values); e2 = ed[ed.source.isin(G) | ed.target.isin(G)]
        outn = e2[e2.source.isin(G)].groupby("source").target.apply(set).to_dict()
        e_in = e2[e2.target.isin(G)]; e_in = e_in[e_in.source.map(yr).values < 10**6]
        inn = e_in.groupby("target").source.apply(list).to_dict()
        k1 = []; sizeN1 = []
        tg = sub.groupby("source").target.apply(set).to_dict()
        for a, gg, y in zip(s.index, gen.values, s.year.values):
            N1 = set(outn.get(gg, set())) | {x for x in inn.get(gg, []) if yr[x] < y}
            N1.discard(gg); sizeN1.append(len(N1)); k1.append(len(tg.get(a, set()) & N1))
        r = pd.DataFrame({"gen_cited": agg.gen > 0, "k": agg.k, "n1": n1, "fr": s.fully_random_citations, "k1": k1, "sizeN1": sizeN1, "Q": Q}, index=s.index)
        out[name] = r
    return out
def report(kind, res):
    o = run(kind, res); print(f"\n##### {kind}, labels {res}, theta {THETA if kind=='baseline' else 1000000}, sample {N}+{N} agents #####")
    for name, r in o.items():
        r = r.assign(dev=r.k - r.n1)
        lo = (r.k >= r.n1).mean() * 100; both = ((r.k >= r.n1) & (r.k <= r.n1 + r.fr)).mean() * 100
        print(f"[{name}] generator cited: {r.gen_cited.mean()*100:.1f}% | in-cluster citations k vs quota n1=floor(alpha*Q): k>=n1 for {lo:.1f}%, n1<=k<=n1+fr for {both:.1f}% | mean k={r.k.mean():.2f}, mean n1={r.n1.mean():.2f}, k-n1 quartiles {r.dev.quantile([.25,.5,.75]).tolist()}")
        big = r[r.sizeN1 >= 3 * r.n1 + 3]
        print(f"      generator 1-hop neighbourhood: k1>=n1 for {(big.k1 >= big.n1).mean()*100:.1f}% of {len(big)} agents with a large neighbourhood; mean k1={big.k1.mean():.2f} vs n1={big.n1.mean():.2f}")
    return o
report("baseline", "0.01"); report("baseline", "0.1"); report("control", "0.01")
