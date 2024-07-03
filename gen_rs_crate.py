import os
import argparse
import textwrap

DIR_ROWS = 1
DIR_COLS = 1
MOD_ROWS = 1
MOD_COLS = 1
comment_size = 5000


def write_directory(basedir, dr, dc):
    dirname = f"{basedir}/dir_{dr}_{dc}"
    os.makedirs(dirname, exist_ok=True)

    for mr in range(MOD_ROWS):
        for mc in range(MOD_COLS):
            if mr == 0:
                if dr == 0:
                    deps = []
                else:
                    deps = [
                        (dr - 1, j, MOD_ROWS - 1, k)
                        for k in range(MOD_COLS)
                        for j in range(DIR_COLS)
                    ]
            else:
                deps = [(dr, dc, mr - 1, k) for k in range(MOD_COLS)]

            str_deps = f";\n{' '*4*4}".join(
                f"m_{d[0]}_{d[1]}_{d[2]}_{d[3]}::f()" for d in deps
            )
            mod_name = f"{dirname}/m_{dr}_{dc}_{mr}_{mc}"
            os.makedirs(mod_name, exist_ok=True)

            mod_main = f"{mod_name}/Cargo.toml"
            deps = [
                (f"m_{dt[0]}_{dt[1]}_{dt[2]}_{dt[3]}", f"dir_{dt[0]}_{dt[1]}")
                for dt in deps
            ]

            os.makedirs(f"{mod_name}/src", exist_ok=True)
            with open(f"{mod_name}/src/lib.rs", "w") as fp:
                fp.write(
                    textwrap.dedent(
                        f"""\
                // {"X" * comment_size} //
                pub fn f() {{
                    {str_deps}
                }}
                """
                    )
                )
            with open(mod_main, "w") as fp:
                fp.write(
                    textwrap.dedent(
                        f"""
                [package]
                name = "m_{dr}_{dc}_{mr}_{mc}"
                version = "0.1.0"
                edition = "2021"
                [dependencies]
                """
                    )
                )
                for name, path in deps:
                    fp.write(f'{name} = {{ path = "../../{path}/{name}"}}\n')


def write(basedir):
    for row in range(DIR_ROWS):
        for col in range(DIR_COLS):
            write_directory(basedir, row, col)

    os.makedirs(f"{basedir}/src", exist_ok=True)
    with open(f"{basedir}/src/main.rs", "w") as fp:
        imports = [
            f"m_{dr}_{dc}_{mr}_{mc}"
            for dr in range(DIR_ROWS)
            for dc in range(DIR_COLS)
            for mr in range(MOD_ROWS)
            for mc in range(MOD_COLS)
        ]
        for item in imports:
            fp.write(f"use {item};\n")

        fp.write("fn main() {\n")
        for item in imports:
            fp.write(f"    let _ = {item}::f;\n")
        fp.write('    println!("ok");\n')
        fp.write("}\n")

    with open(f"{basedir}/Cargo.toml", "w") as fp:
        fp.write(
            textwrap.dedent(
                f"""
        [package]
        name = "build_matrix"
        version = "0.1.0"
        edition = "2021"
        [dependencies]
        """
            )
        )
        deps = [
            (f"dir_{dr}_{dc}", f"m_{dr}_{dc}_{mr}_{mc}")
            for dr in range(DIR_ROWS)
            for dc in range(DIR_COLS)
            for mr in range(MOD_ROWS)
            for mc in range(MOD_COLS)
        ]
        for level1, level2 in deps:
            fp.write(f'{level2} = {{ path = "./{level1}/{level2}"}}\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("basedir", nargs="?", default=".")
    parser.add_argument(
        "-n",
        type=int,
        help="set all of -dir-rows, -dir-cols, -mod-rows, -mod-cols to the same value",
    )
    parser.add_argument("-row", type=int, help="set row")
    parser.add_argument("-col", type=int, help="set col")
    parser.add_argument("-mrow", type=int, help="set mod-row")
    parser.add_argument("-mcol", type=int, help="set mod-col")

    args = parser.parse_args()

    global DIR_ROWS, DIR_COLS, MOD_ROWS, MOD_COLS

    if args.n is not None:
        DIR_ROWS = DIR_COLS = MOD_ROWS = MOD_COLS = args.n
    if args.row is not None:
        DIR_ROWS = args.row
    if args.col is not None:
        DIR_COLS = args.col
    if args.mrow is not None:
        MOD_ROWS = args.mrow
    if args.mcol is not None:
        MOD_COLS = args.mcol

    write(args.basedir)


if __name__ == "__main__":
    main()
