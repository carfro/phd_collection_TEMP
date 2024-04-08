#!/usr/bin/env bash
#SBATCH -A <project_id>
#SBATCH -p <partition_name>
#SBATCH -N <node_count>
#SBATCH -t <time_allocation>
#SBATCH -J <PVDF_rot_phi_ANGLE>
#SBATCH -o ./PATH_TO_CALC/slurmid-%j.stdout

# Load relevant modules
module load <load_QE_and_dependencies>

export OMP_NUM_THREADS=1
export OMP_PLACES=cores

cd ./PATH_TO_CALC

time mpirun pw.x  < CX_bPVDF_scf.in >& bPVDF_scf.out
time mpirun pw.x  < CX_bPVDF_Nscf_gdir1.in >& bPVDF_Nscf_gdir1.out
time mpirun pw.x  < CX_bPVDF_Nscf_gdir2.in >& bPVDF_Nscf_gdir2.out

rm -rf ./tmp
rm -rf *kernel*

#End of script (make sure line before this gets run)
