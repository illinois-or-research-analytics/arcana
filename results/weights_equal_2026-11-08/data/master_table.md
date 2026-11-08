### Concentration and tails

| condition | weights (pa/fit/na/ar) | Gini | top-10 share % | top-1% share % | top-0.1% median in-degree | max in-degree | agents > 50k |
|---|---|---|---|---|---|---|---|
| citing on, labels 0.1 | 0.10/0.70/0.10/0.10 | 0.77 | 1.91 | 38.6 | 2,301 | 55,592 | 2.0 |
| citing on, labels 0.1 | 0.25/0.25/0.25/0.25 | 0.76 | 1.33 | 33.8 | 1,984 | 45,893 | 0.3 |
| citing on, labels 0.01 | 0.10/0.70/0.10/0.10 | 0.82 | 1.75 | 46.1 | 2,892 | 57,897 | 2.0 |
| citing on, labels 0.01 | 0.25/0.25/0.25/0.25 | 0.80 | 1.13 | 40.6 | 2,503 | 33,863 | 0.0 |
| citing on, labels 0.001 | 0.10/0.70/0.10/0.10 | 0.85 | 2.46 | 56.1 | 3,712 | 68,136 | 7.3 |
| citing on, labels 0.001 | 0.25/0.25/0.25/0.25 | 0.84 | 1.77 | 50.4 | 2,982 | 47,587 | 0.3 |
| citing off, uniform generators | 0.10/0.70/0.10/0.10 | 0.78 | 2.02 | 45.2 | 2,978 | 69,642 | 2.3 |
| citing off, uniform generators | 0.25/0.25/0.25/0.25 | 0.76 | 1.45 | 39.5 | 2,480 | 43,357 | 0.0 |
| generators non-random, and | 0.10/0.70/0.10/0.10 | 0.80 | 3.30 | 47.1 | 2,634 | 102,367 | 17.7 |
| generators non-random, and | 0.25/0.25/0.25/0.25 | 0.79 | 2.34 | 42.5 | 2,306 | 66,651 | 5.7 |
| generators non-random, or | 0.10/0.70/0.10/0.10 | 0.79 | 2.88 | 47.5 | 3,000 | 107,683 | 9.7 |
| generators non-random, or | 0.25/0.25/0.25/0.25 | 0.77 | 1.71 | 41.5 | 2,598 | 52,360 | 1.3 |

### Citing, ages, seeds, uncited

| condition | weights (pa/fit/na/ar) | within-label citing % | seed share of new citations % | citations aged 1-4 % | uncited % |
|---|---|---|---|---|---|
| citing on, labels 0.1 | 0.10/0.70/0.10/0.10 | 40.3 | 4.54 | 34.4 | 15.1 |
| citing on, labels 0.1 | 0.25/0.25/0.25/0.25 | 40.4 | 4.67 | 34.3 | 14.2 |
| citing on, labels 0.01 | 0.10/0.70/0.10/0.10 | 43.2 | 4.67 | 34.5 | 17.0 |
| citing on, labels 0.01 | 0.25/0.25/0.25/0.25 | 43.2 | 4.75 | 34.4 | 15.5 |
| citing on, labels 0.001 | 0.10/0.70/0.10/0.10 | 44.1 | 4.78 | 34.8 | 18.5 |
| citing on, labels 0.001 | 0.25/0.25/0.25/0.25 | 44.1 | 4.85 | 34.6 | 16.6 |
| citing off, uniform generators | 0.10/0.70/0.10/0.10 | 15.5 | 5.03 | 30.8 | 14.4 |
| citing off, uniform generators | 0.25/0.25/0.25/0.25 | 15.8 | 5.19 | 30.9 | 13.5 |
| generators non-random, and | 0.10/0.70/0.10/0.10 | 15.5 | 4.46 | 34.3 | 14.8 |
| generators non-random, and | 0.25/0.25/0.25/0.25 | 15.0 | 4.57 | 34.2 | 14.3 |
| generators non-random, or | 0.10/0.70/0.10/0.10 | 14.7 | 4.54 | 33.0 | 14.3 |
| generators non-random, or | 0.25/0.25/0.25/0.25 | 14.8 | 4.69 | 32.9 | 13.4 |

### Leiden readout (resolution 0.1): node coverage % and median conductance by cluster-size band

| condition | weights (pa/fit/na/ar) | coverage 2-9 % | conductance 2-9 | coverage 10-99 % | conductance 10-99 | coverage 100-999 % | conductance 100-999 |
|---|---|---|---|---|---|---|---|
| citing on, labels 0.1 | 0.10/0.70/0.10/0.10 | 55.0 | 0.919 | 43.4 | 0.847 | 1.4 | 0.716 |
| citing on, labels 0.1 | 0.25/0.25/0.25/0.25 | 54.0 | 0.919 | 44.3 | 0.853 | 1.6 | 0.702 |
| citing on, labels 0.01 | 0.10/0.70/0.10/0.10 | 71.6 | 0.926 | 27.1 | 0.859 | 1.3 | 0.835 |
| citing on, labels 0.01 | 0.25/0.25/0.25/0.25 | 70.6 | 0.927 | 28.3 | 0.868 | 1.1 | 0.788 |
| citing on, labels 0.001 | 0.10/0.70/0.10/0.10 | 78.8 | 0.929 | 20.7 | 0.869 | 0.4 | 0.906 |
| citing on, labels 0.001 | 0.25/0.25/0.25/0.25 | 78.5 | 0.931 | 21.1 | 0.877 | 0.4 | 0.848 |
| citing off, uniform generators | 0.10/0.70/0.10/0.10 | 37.4 | 0.889 | 62.4 | 0.820 | 0.1 | 0.835 |
| citing off, uniform generators | 0.25/0.25/0.25/0.25 | 37.4 | 0.891 | 62.4 | 0.826 | 0.1 | 0.852 |
| generators non-random, and | 0.10/0.70/0.10/0.10 | 42.3 | 0.902 | 57.2 | 0.835 | 0.1 | 0.847 |
| generators non-random, and | 0.25/0.25/0.25/0.25 | 44.4 | 0.902 | 55.2 | 0.838 | 0.1 | 0.854 |
| generators non-random, or | 0.10/0.70/0.10/0.10 | 34.9 | 0.893 | 64.8 | 0.817 | 0.1 | 0.836 |
| generators non-random, or | 0.25/0.25/0.25/0.25 | 35.3 | 0.894 | 64.5 | 0.824 | 0.1 | 0.848 |
