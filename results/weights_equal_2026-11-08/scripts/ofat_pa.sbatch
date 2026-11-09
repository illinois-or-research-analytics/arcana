#!/bin/bash
#SBATCH --job-name=ofat_pa_summ
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --time=00:30:00
#SBATCH --partition=secondary
#SBATCH --account=chackoge-ic
#SBATCH --output=ofat_pa_summ-%j.out
/projects/illinois/eng/cs/chackoge/illinoiscomputes/abm/cantatas/cantatas_venv/bin/python ofat_pa_summaries.py
