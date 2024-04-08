#!/usr/bin/env python3
"""
This script creates a series of rotated configurations based for the relaxed beta-PVDF cystal and runs a series of Berry-phase calculations in Quantum ESPRESSO (QE).
The script is used to compute the spontaneous polarization of the beta-PVDF crystal by
calculating the difference in Berry-phase of the system in accordance with the modern theory of polarization.
The script generates a series of rotated configurations of the beta-PVDF crystal,
starting from the asymmetric polar ground state, and ending with the symmetric non-polar reference state.
This results in the polarization lattice, which can be used to compute the polarization by looking at the difference in Berry-phase between the two final configurations *as seen along the same branch*.

The script generates an individual dir for each rotated configuration, containing the QE input file
and the pertaining SLURM submit script which is then submitted to the cluster.
The input file is generated using hard-coded QE settings and ASE to read in the monomers (left and right in separate files) and then rotate the left monomer around the z-axis by a given angle.

Usage:
    ./<PLACEHOLDER>.py

Author:
    Carl Frostenson
"""
import os
import subprocess as sp
import numpy as np
from numpy.linalg import norm
from scipy.linalg import expm
from ase.build import bulk
from ase.io import read, write
from ase.visualize import view

# Rotate and translate molecule, then prepare and submit Quantum ESPRESSO input files
angles = np.hstack((np.arange(0, -185, -5), np.arange(5, 185, 5)))
for angle in angles:
    print(f"φ = {angle}")
    mid_chain = read('bPVDF_CX_left.espresso-in')
    cell = mid_chain.get_cell_lengths_and_angles()
    edge_chain = read('bPVDF_CX_right.espresso-in')
    carbon_pos = mid_chain.get_positions()[0:2]
    rot_center = (carbon_pos[1][0], carbon_pos[1][1] + 0.5 * (carbon_pos[0][1] - carbon_pos[1][1]), 0)

    mid_chain.rotate(0 - angle, 'z', center=rot_center)
    mid_chain.translate((0, 0, cell[2] / 2))
    mid_chain.extend(edge_chain)
    
    file_name = f"PVDF-COM-rot_phi{angle}.espresso-in"
    write(file_name, mid_chain)

    dir_name = f"phi_{angle}"
    os.makedirs(dir_name, exist_ok=True)
    
    # Prepare input files for scf, nscf_gdir1, and nscf_gdir2 calculations
    prepare_input_files(angle, dir_name, file_name)

    # Cleanup and submit jobs
    os.remove(file_name)
    submit_job(dir_name, angle)

def prepare_input_files(angle, dir_name, structure_file):
    """Prepare input files for Quantum ESPRESSO calculations."""
    base_input = f'''
&control
  prefix= 'pvf',
  calculation= '{{calculation_type}}',
  pseudo_dir = '<path-to-ONCV-SG15-PBE-Pseudopotentials>'
  outdir= './tmp',
  restart_mode= 'from_scratch',
  tstress= .true.,
  tprnfor= .true.,
  verbosity = 'high',
  {{additional_controls}}
/

&system
  ibrav= 0, nat= 12, ntyp= 3, ecutwfc= 160.0, input_dft='vdW-DF-cx',
  nbnd=32,
  occupations = 'smearing',
  degauss = 0.0002,
  smearing = 'gaussian',
/

&electrons
  conv_thr= 1.0d-8,
/

ATOMIC_SPECIES
C 12.0 C_ONCV_PBE-1.0.upf
F 14.0 F_ONCV_PBE-1.0.upf
H 1.0  H_ONCV_PBE-1.0.upf

K_POINTS automatic
4 6 10 0 0 0
'''

    calculations = {
        "scf": "",
        "nscf_gdir1": "lberry = .true., gdir = 1, nppstr = 4",
        "nscf_gdir2": "lberry = .true., gdir = 2, nppstr = 8"
    }

    for calc_type, additional_controls in calculations.items():
        input_text = base_input.format(calculation_type=calc_type, additional_controls=additional_controls)
        with open(os.path.join(dir_name, f"CX_bPVDF_{calc_type}.in"), "w") as f:
            f.write(input_text)

def submit_job(dir_name, angle):
    """Submit the job to the scheduler."""
    sp.run(f"sed s/PATH_TO_CALC/{dir_name}/g submit.sh > {dir_name}/submit.sh", shell=True)
    sp.run(f"sed -i s/ANGLE/{angle}/g {dir_name}/submit.sh", shell=True)
    sp.run(f"sbatch {dir_name}/submit.sh", shell=True)

