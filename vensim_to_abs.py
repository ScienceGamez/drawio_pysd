"""Translate a vensim model to an abstract model representation of pysd."""


import argparse
import subprocess

from pathlib import Path
from pysd.translators.vensim.vensim_file import VensimFile
from pysd.builders.python.python_model_builder import ModelBuilder


if __name__ == '__main__':

    # Parse arguments
    parser = argparse.ArgumentParser(description='Translate a vensim model to an abstract model representation of pysd.')
    parser.add_argument('mdl_file', type=str, help='Vensim model file')
    args = parser.parse_args()
    mdl_file = args.mdl_file
    mdl_file = Path(mdl_file)


    # Read and parse Vensim file
    ven_file = VensimFile(mdl_file)
    ven_file.parse()
    # get AbstractModel
    abs_model = ven_file.get_abstract_model()

    abs_file = mdl_file.with_name(mdl_file.name + '.abs')
    # prit to file
    with open(abs_file, 'w') as f:
        f.write(repr(abs_model))
    # Format the file with black
    subprocess.run(['black', abs_file])
    print(f"Succesfully translated {mdl_file} to {abs_file}")
