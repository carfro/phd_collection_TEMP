#!/usr/bin/env python3

"""
This script prints the primitive and conventional standard structures, space group symbol, and volume base on a Quantum ESPRESSO input file.
It uses ASE and pymatgen libraries to read the structure, convert it into a CIF format in-memory, 
and analyze its space group properties. 
It needs both since pymatgen is currently unable to read general Quantum ESPRESSO input files directly.

The script is designed to be run from the command line, taking a single argument: the filename (with or without the '.in' extension) of the structure to be analyzed.

Usage:
    ./lattice_symmetries.py <file_name>

Dependencies:
- pymatgen: Used for analyzing the structure's space group and printing detailed structural information.
- ASE (Atomic Simulation Environment): Used for reading the quantum espresso input files and converting them into CIF format.
- Python 3 and above.

Example:
    ./lattice_symmetries.py MnBiO3_relaxed.in
"""

import sys
import io
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from ase.io import read, write

def analyze_structure(base_name):
    """
    Reads the structure from a file, analyzes it using pymatgen, and prints various properties.
    
    Parameters:
    - base_name (str): The base name of the structure file, with or without the '.in' extension.
    
    The function expects a QE input file format and prints the primitive and conventional standard
    structure, space group symbol, and number.
    """
    if not base_name.endswith('.in'):
        base_name += '.in'
    inp_path = f"./{base_name}"  # Adjusted path to the QE input file
    
    # Read the structure from the QE input file using ASE
    try:
        structure = read(inp_path, format='espresso-in')
    except Exception as e:
        print(f"Failed to read structure from {inp_path}: {e}")
        return

    # Convert ASE structure to CIF format and read it with pymatgen from a string
    try:
        cif_io = io.BytesIO()  # Create an in-memory file-like object
        write(cif_io, structure, format='cif')
        cif_io.seek(0)  # Go to the beginning of the StringIO object to read it
        cif_string = cif_io.getvalue().decode('utf-8')  # Decode bytes to string
        structure_pm = Structure.from_str(cif_string, fmt="cif")
    except Exception as e:
        print(f"Error during conversion to pymatgen Structure: {e}")
        return
    finally:
        cif_io.close()  # Close the StringIO object

    # Analyzing the structure with pymatgen
    analyzer = SpacegroupAnalyzer(structure_pm)
    space_group_symbol = analyzer.get_space_group_symbol()
    space_group_number = analyzer.get_space_group_number()

    # Output results
    print(f"Primitive structure:\n{structure_pm}")
    print(f"Space Group Symbol: {space_group_symbol}")
    print(f"Space Group Number: {space_group_number}")
    print("-------------------------")
    print("Conventional standard structure:")
    conventional_structure = analyzer.get_conventional_standard_structure()
    print(conventional_structure)
    print(f"Volume: {conventional_structure.volume}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: script_name.py <file_name>")
        sys.exit(1)
    
    file_name = sys.argv[1]
    # Remove the '.in' extension if present to get the base name
    base_name = file_name.rsplit('.in', 1)[0]
    analyze_structure(base_name)
