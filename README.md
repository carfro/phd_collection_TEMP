# Combined Scripts for Quantum ESPRESSO Calculations

**This is a temporary repository to showcase some of the Python scripts that I've written for my PhD work.**
**They will be published in separate repos with more complete documentation on GitLab soon,**
**but I wanted to make them available for a potential employer to see now.**

The repository contains a collection of scripts (and input files for completeness) used to run DFT 
calculations with Quantum ESPRESSO (QE) on HPC clusters using the SLURM job scheduler.

### Structure of the Repo

#### The ```polymers``` directory contains:
This project relied on ASE for structure manipulation and generation of input files.

- ```PVF_studies.ipynb``` Notebook with the code used to generate the input files for Quantum ESPRESSO as well as some SLURM scripts to run the calculations on our HPC.  

- ```PVF-*.cif``` Structure files for the initial 12 motifs or guesses for the ground state structure of PVF. The same structures are also stored in the ```initial_12.db``` ASE database file.

- ```shifted_12.db``` ASE database file contains the shifted versions of the above structures.

#### The subdirectories of ```hard_and_soft``` contains the following:
This project used QE template files to generate input files for the calculations.

- `bPVDF_a-b_grid/` Template input file and script to generate the energy vs strain along a-b for $\beta$-PVDF.

- `bPVDF_c_grid/` Template input file and script to generate the energy vs strain along c for $\beta$-PVDF.

- `bPVDF_Berry-phase/` Template input file and script to generate the results needed to compute the spontaneous polarization by calculting the Berry phase for $\beta$-PVDF.

- `MnBiO3/` Fully relaxed input filed for MnBiO3 and script to transform to the primitive cell.

- `CubicMetals/` Template input files and script needed to generate the energy vs strain for BCC Fe and FCC Ni.

- `input_structures/` Input structures for the relax calculations.

