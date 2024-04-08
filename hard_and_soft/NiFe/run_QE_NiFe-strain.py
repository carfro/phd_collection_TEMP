#!/usr/bin/env python3
"""
Script to create Quantum ESPRESSO input files for energy vs lattice parameter curves for simple cubic structures.
This script allows specifying functional, input template file, and
a grid range for lattice parameters via command-line flags.

To recreate our results for the cubic metals, use the following grid ranges:

- For the Ni series: 
    CX & PBE: -grid 6.40,6.80,0.01
    AHCX & HSE (not exactly same): -grid 6.45,6.75,0.25

- For the BCC Fe series: 
    CX & PBE: -grid 5.10,5.65,0.01
    AHCX & HSE (not exactly same): -grid 5.25,5.65,0.25

Usage:
    python script.py -func "vdw-df-cx" -tmplt "atoms_pz.in" -grid 5.10,5.65,0.01
    python script.py -func "vdw-df-cx vdw-df-ahcx" -tmplt "atoms_pz.in" -grid 6.40,6.80,0.01
    python script.py -func ["vdw-df-cx","vdw-df-ahcx"] -tmplt "atoms_pz.in" -grid 5.10,5.65,0.01
"""
import os
import subprocess as sp
import argparse
import re

def parse_functionals(args):
  """Parse and clean up the functional arguments from various input formats."""
  # Join arguments and remove potential list/vector notation
  args_combined = " ".join(args).translate({ord(c): None for c in '[]{}"'})
  # Split by commas or spaces to accommodate different input formats
  return [arg.strip() for arg in re.split(r'[ ,]+', args_combined) if arg.strip()]

def create_and_submit_job(functional, a_value, template_file):
  """Create directories, modify input files, and submit jobs for given functional and a-value."""
  directory_name = f"{functional}/a_{a_value}"
  os.makedirs(directory_name, exist_ok=True)

  # Modify the input file based on the functional and a-value, then move it to the created directory
  sp.run(f"sed s/FUNC/{functional}/g {template_file} > atoms_{functional}_tmp.in", shell=True)
  sp.run(f"sed s/LAT_PARAM/'{a_value}'/g atoms_{functional}_tmp.in > {directory_name}/atoms.in", shell=True)

  # Create and write the submission script
  submission_script_path = f"{directory_name}/submit.sh"
  with open(submission_script_path, 'w+') as file:
    file.write(f"""#!/usr/bin/env bash
#SBATCH -A <project_id>
#SBATCH -p <partition_name>
#SBATCH -N <node_count>
#SBATCH -t <time_allocation>
#SBATCH -J job_name_{functional}_{a_value}
#SBATCH -o {directory_name}/slurmid-%j.stdout

# Load relevant modules
module load <load_QE_and_dependencies>

cd {directory_name}/

time mpirun pw.x -inp ./atoms.in > QE.out;

#End of script\n""")

  # Submit the job
  sp.run(f"sbatch {submission_script_path}", shell=True)

  # Cleanup temporary files
  sp.run(f"rm atoms_{functional}_tmp.in", shell=True)

# Setup argument parser
parser = argparse.ArgumentParser(description="Create energy vs lattice parameter curves.")
parser.add_argument("-func", "--functionals", required=True, help="Van der Waals functionals as a single string or quoted list.")
parser.add_argument("-tmplt", "--template", default="atoms_pz.in", help="Template input file to use.")
parser.add_argument("-grid", "--grid_range", required=True, help="Start, end values for the grid, and increment, separated by commas.")

# Main driver
if __name__ == "__main__":
  args = parser.parse_args()

  # Parse functionals from the command line arguments
  functionals = parse_functionals([args.functionals])
  
  # Parse grid range and generate a_values
  start, end, incr = map(float, args.grid_range.split(","))
  a_values = [round(start + incr * i, 2) for i in range(int((end - start) / incr) + 1)]

  for functional in functionals:
    for a_value in a_values:
      create_and_submit_job(functional, a_value, args.template)