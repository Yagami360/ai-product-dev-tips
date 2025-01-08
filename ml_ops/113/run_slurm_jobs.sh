#!/bin/sh
set -eu
cd jobs

# Check the slurm service status
# sudo systemctl status slurmctld slurmd

# Make sure the job scripts are executable to avoid "slurmstepd: error: execve(): jobs/train.sh: Permission denied"
chmod +x train.sh

# Run the slurm jobs
# srun --nodes=1 --ntasks=1 train.sh
sbatch train.sh

# Check the job status
squeue --format="%.18i %.9P %.30j %.8u %.8T %.9M %.4D %R"

# Check the job output
# scontrol show job
