#!/bin/bash
#SBATCH --job-name=planted_cohort
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --time=00:30:00
#SBATCH --partition=secondary
#SBATCH --account=chackoge-ic
#SBATCH --output=analysis-%j.out
/projects/illinois/eng/cs/chackoge/illinoiscomputes/abm/cantatas/cantatas_venv/bin/python planted_cohort_analysis.py
