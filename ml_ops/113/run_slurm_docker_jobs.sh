#!/bin/sh
set -eu
cd jobs

# Check the slurm service status
# sudo systemctl status slurmctld slurmd

# Make sure the job scripts are executable to avoid "slurmstepd: error: execve(): jobs/train_docker.sh: Permission denied"
# chmod +x train_docker.sh

# Run the slurm jobs
sbatch train_docker.sh

# Check the job status
squeue --format="%.18i %.9P %.30j %.8u %.8T %.9M %.4D %R"

# Check the job output
# scontrol show job
