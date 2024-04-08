#!/usr/bin/env python3
"""
This script creates and runs a series of strain deformation calculations in Quantum ESPRESSO (QE)
for a beta-PVDF crystal to generate the energy curve E(c; a_0, b_0) for the system. 
The along-chain lattice parameters c is varied in a grid pattern around the equilibrium values (obtained from full vc-relax), the *unit cell* is then relaxed along the a and b directions in vdW-DF-cx for each strained configuration using QE.

The script generates an individual dir for each strained configuration, containing the QE input file
and the pertaining SLURM submit script which is then submitted to the cluster.
The input file is generated by replacing placeholders in a template file with the grid 
values of the lattice parameters.

Usage:
    ./<PLACEHOLDER>.py

Author:
    Carl Frostenson
"""
import os
import subprocess as sp

template_file = "PVDF_template-c_vcrelaxd.in"

# Define the functional used and lattice parameter variations
idFunct = ['vdw-df-cx']
n = 16
Delta = 0.5
c_grid = [2.55300 - Delta / (n - 1) * (n / 2 - i) for i in range(n)]

def create_directory_and_prepare_input(functional, c_value):
  """
  Creates a directory for the given functional and a_value, prepares the input files,
  and generates a SLURM submission script.
  """
  directory_name = f"{functional}/c_{c_value:.4f}"
  os.makedirs(directory_name, exist_ok=True)

  # Prepare the input file
  tmp_in_file = f"{directory_name}/atoms_tmp.in"
  sp.run(f"sed s/FUNC/{functional}/g {template_file} > {tmp_in_file}", shell=True)
  sp.run(f"sed s/C_VALUE/'{c_value:.4f}'/g {tmp_in_file} > {directory_name}/atoms.in", shell=True)
  os.remove(tmp_in_file)

  # Create and write the SLURM submission script
  submission_script_path = f"{directory_name}/submit.sh"
  with open(submission_script_path, 'w+') as file:
    file.write(f'''#!/usr/bin/env bash
#SBATCH -A <project_id>
#SBATCH -p <partition_name>
#SBATCH -N <node_count>
#SBATCH -t <time_allocation>
#SBATCH -J PVDF-vera_series_vc-relax_c={c_value:.4f}
#SBATCH -o {directory_name}/slurmid-%j.stdout

# Load relevant modules
module load <load_QE_and_dependencies>

cd {directory_name}/

time mpirun pw.x -inp ./atoms.in > QE.out;

#End of script
''')
  # Submit the job script
  sp.run(f"sbatch {submission_script_path}", shell=True)

# Iterate over all combinations of functionals and a-values to create directories, prepare inputs, and submit jobs
for functional in idFunct:
  for c_value in c_grid:
    create_directory_and_prepare_input(functional, c_value)
