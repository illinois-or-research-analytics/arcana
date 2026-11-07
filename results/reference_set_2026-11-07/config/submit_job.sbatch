#!/bin/bash
#SBATCH --job-name=arcana_cpm0.01_r0
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --time=00:30:00
#SBATCH --partition=secondary
#SBATCH --account=chackoge-ic
#SBATCH --output=slurm-%j.out

source /etc/profile.d/modules.sh
/bin/bash ./batch_script.run
