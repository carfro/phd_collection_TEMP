#!/usr/bin/env python3
"""
Enhanced script to generate input files for DFT E vs a,b strain calculation on a beta-PVDF crystal,
applying strain not only to the unit cell but also translating polymer chains accordingly,
while preserving bond lengths.
"""
import os
import numpy as np
import subprocess as sp

template_file = "PVDF_template-a-b_vcrelaxed.in"
idFunct = ['vdw-df-cx']

# Initial lattice parameters (angstroms)
a0, b0 = 8.57840, 4.75724

n = 16
Delta = 5.5
a_grid = [a0 - Delta / (n - 1) * (n / 2 - i) for i in range(n)]
b_grid = [b0 - Delta / (n - 1) * (n / 2 - i) for i in range(n)]

# Redefined initial_positions to group atoms by monomers
initial_positions = {
    "monomer_1_left": [
        ("C", 2.1446, 2.6481946324, 0.0),        # Carbon 1
        ("C", 2.1446, 1.8202895007, 1.2873982),  # Carbon 2
        ("F", 3.2461336431, 3.4915217277, 0.0),  # Fluorine 1
        ("F", 1.0430663569, 3.4915217277, 0.0),  # Fluorine 2
        ("H", 3.0324962516, 1.1722521263, 1.2873982), # Hydrogen 1
        ("H", 1.2567037484, 1.1722521263, 1.2873982)  # Hydrogen 2
    ],
    "monomer_2_right": [
        ("C", 6.4338, 0.2695633149, 0.0),          # Carbon 1
        ("C", 6.4338, -0.5583427302, 1.2873982),    # Carbon 2
        ("F", 7.5353334887, 1.1128901295, 0.0),    # Fluorine 1
        ("F", 5.3322665113, 1.1128901295, 0.0),    # Fluorine 2
        ("H", 5.5459043918, -1.2064, 1.2873982),   # Hydrogen 1
        ("H", 7.3216956082, -1.2064, 1.2873982)    # Hydrogen 2
    ]
}

def center_of_mass(atoms):
    """
    Calculate the center of mass for a given set of atoms.
    Assumes equal mass for simplicity.
    """
    x, y, z = zip(*[(atom[1], atom[2], atom[3]) for atom in atoms])
    return np.mean(x), np.mean(y), np.mean(z)

def translate_monomers(a_value, b_value, initial_positions):
    """
    Translate monomers based on the adjusted distances due to lattice parameter changes.
    For translations along the 'a' axis, the left monomer remains fixed.
    For translations along the 'b' axis, the right monomer remains fixed.
    """
    delta_a = a_value - a0  # Change in lattice parameter a
    delta_b = b_value - b0  # Change in lattice parameter b

    translated_positions = {}
    for monomer, atoms in initial_positions.items():
        if monomer == "monomer_1_left":
            # For the left monomer, apply translation only for changes in the b direction
            new_atoms = [(element, x, y + delta_b, z) for element, x, y, z in atoms]
        else:  # "monomer_2_right"
            # For the right monomer, apply translation only for changes in the a direction
            new_atoms = [(element, x + delta_a, y, z) for element, x, y, z in atoms]

        translated_positions[monomer] = new_atoms

    return translated_positions

def generate_structures_and_submit(functional, a_value, b_value):
    """
    Creates directories, calculates new atomic positions, updates lattice parameters, generates input files,
    and prepares for SLURM job script submission for each configuration.
    """
    directory_name = f"{functional}/a_{a_value:.2f}_b_{b_value:.2f}"
    os.makedirs(directory_name, exist_ok=True)
    
    # Calculate new atomic positions based on the lattice parameter changes
    new_positions = translate_monomers(a_value, b_value, initial_positions)
    
    # Read the template file
    with open(template_file, 'r') as file:
        content = file.read()
    
    # Replace 'FUNC' with the functional
    content = content.replace('FUNC', functional)
    
    # Update lattice parameters in the CELL_PARAMETERS section
    content = content.replace('A_VALUE', f'{a_value:.10f}   0.000000000   0.000000000')
    content = content.replace('B_VALUE', f'0.000000000   {b_value:.10f}   0.000000000')
    
    # Generate the atomic positions string for the input file and replace the placeholder
    atomic_positions_str = "ATOMIC_POSITIONS angstrom\n"
    for monomer, atoms in new_positions.items():
        for atom in atoms:
            element, x, y, z = atom
            atomic_positions_str += f"{element} {x:.10f} {y:.10f} {z:.10f}\n"
    content = content.replace('ATOMIC_POSITIONS_PLACEHOLDER', atomic_positions_str)
    
    # Write the modified content to the new input file
    input_file_path = os.path.join(directory_name, "atoms.in")
    with open(input_file_path, 'w') as file:
        file.write(content)

    # Generate the SLURM job script
    submission_script_path = os.path.join(directory_name, "submit.sh")
    with open(submission_script_path, 'w+') as file:
        file.write(f"""#!/usr/bin/env bash
#SBATCH -A <project_id>
#SBATCH -p <partition_name>
#SBATCH -N <node_count>
#SBATCH -t <time_allocation>
#SBATCH -J PVDF_{functional}_a{a_value:.2f}_b{b_value:.2f}
#SBATCH -o {directory_name}/slurm-%j.stdout

# Load relevant modules
module load <load_QE_and_dependencies>

cd {directory_name}/

time mpirun pw.x -inp ./atoms.in > QE.out;
""")

    # Submit the job script
    #sp.run(f"sbatch {submission_script_path}", shell=True)
    sp.run(f"echo 'sbatch {submission_script_path}'", shell=True)

# Loop over combinations of functional, a, and b to generate and submit jobs
for functional in idFunct:
    for a_value in a_grid:
        for b_value in b_grid:
            generate_structures_and_submit(functional, a_value, b_value)
