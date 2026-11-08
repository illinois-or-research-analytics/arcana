### Concentration and tails

| condition | Gini | top-10 share % | top-1% share % | top-0.1% median in-degree | max in-degree | agents > 50k |
|---|---|---|---|---|---|---|
| citing on, labels 0.1 | 0.76 | 1.33 | 33.8 | 1,984 | 45,893 | 0.3 |
| citing on, labels 0.01 | 0.80 | 1.13 | 40.6 | 2,503 | 33,863 | 0.0 |
| citing on, labels 0.001 | 0.84 | 1.77 | 50.4 | 2,982 | 47,587 | 0.3 |
| citing off, uniform generators | 0.76 | 1.45 | 39.5 | 2,480 | 43,357 | 0.0 |
| generators non-random, and | 0.79 | 2.34 | 42.5 | 2,306 | 66,651 | 5.7 |
| generators non-random, or | 0.77 | 1.71 | 41.5 | 2,598 | 52,360 | 1.3 |

### Citing, ages, seeds, uncited

| condition | within-label citing % | seed share of new citations % | citations aged 1-4 % | uncited % |
|---|---|---|---|---|
| citing on, labels 0.1 | 40.4 | 4.67 | 34.3 | 14.2 |
| citing on, labels 0.01 | 43.2 | 4.75 | 34.4 | 15.5 |
| citing on, labels 0.001 | 44.1 | 4.85 | 34.6 | 16.6 |
| citing off, uniform generators | 15.8 | 5.19 | 30.9 | 13.5 |
| generators non-random, and | 15.0 | 4.57 | 34.2 | 14.3 |
| generators non-random, or | 14.8 | 4.69 | 32.9 | 13.4 |

### Leiden readout (resolution 0.1): node coverage % and median conductance by cluster-size band

| condition | coverage 2-9 % | conductance 2-9 | coverage 10-99 % | conductance 10-99 | coverage 100-999 % | conductance 100-999 |
|---|---|---|---|---|---|---|
| citing on, labels 0.1 | 54.0 | 0.919 | 44.3 | 0.853 | 1.6 | 0.702 |
| citing on, labels 0.01 | 70.6 | 0.927 | 28.3 | 0.868 | 1.1 | 0.788 |
| citing on, labels 0.001 | 78.5 | 0.931 | 21.1 | 0.877 | 0.4 | 0.848 |
| citing off, uniform generators | 37.4 | 0.891 | 62.4 | 0.826 | 0.1 | 0.852 |
| generators non-random, and | 44.4 | 0.902 | 55.2 | 0.838 | 0.1 | 0.854 |
| generators non-random, or | 35.3 | 0.894 | 64.5 | 0.824 | 0.1 | 0.848 |
