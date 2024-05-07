"""Small script to plot the data from a tab file as output from pysd.

"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def plot_tab_file(tab_file, vars=None):
    df = pd.read_csv(tab_file, sep="\t")

    if vars:
        vars = [[v] if not "*" in v else
                # Match all the columsn that start with the string before the *
                [c for c in df.columns if c.startswith(v.split("*")[0])]
                for v in vars]
        # Flatten the list
        vars = [v for sublist in vars for v in sublist]

        df = df[["Time"] + vars]
    df.plot(x="Time", title=tab_file.stem)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "tab_file",
        help="The tab file to plot, it is optional. If not provided, the last generated `.tab` file will be read.",
        nargs="?",
        default=None,
    )
    parser.add_argument(
        "-r",
        "--return-variables",
        help="The variables to return. If not provided, all variables will be returned.",
        nargs="*",
        default=None,
    )
    args = parser.parse_args()
    tab_file = args.tab_file
    if tab_file is None:

        tab_files = sorted(list(Path(".").glob("*.tab")))
        if len(tab_files) == 0:
            print("No tab files found.")
            exit(1)
        tab_file = tab_files[-1]
    plot_tab_file(tab_file, vars=args.return_variables)
