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
                f"m_{d[0]}_{d[1]}_{d[2]}_{d[3]}.F()" for d in deps
            )
            mod_text = textwrap.dedent(
                f"""\
            // {"X" * comment_size} //
            func F() {{
                {str_deps}
            }}
            """
            )
            mod_name = f"{dirname}/m_{dr}_{dc}_{mr}_{mc}"
            os.makedirs(mod_name, exist_ok=True)
            mod_main = f"{mod_name}/main.go"
            imports_str = [
                f"build_matrix/dir_{dt[0]}_{dt[1]}/m_{dt[0]}_{dt[1]}_{dt[2]}_{dt[3]}"
                for dt in deps
            ]
            with open(mod_main, "w") as fp:
                fp.write(f"package {mod_name.split('/')[-1]}\n")
                fp.write("import (\n")
                for item in imports_str:
                    fp.write(f'\t"{item}"\n')
                fp.write(")\n")
                fp.write(mod_text)


def write(basedir):
    for row in range(DIR_ROWS):
        for col in range(DIR_COLS):
            write_directory(basedir, row, col)

    with open(f"{basedir}/go.mod", "w") as fp:
        fp.write("""module build_matrix""")
    os.makedirs(f"{basedir}/entry", exist_ok=True)
    with open(f"{basedir}/entry/main.go", "w") as fp:
        fp.write(f"package main\n")
        fp.write('import "fmt"\n')
        imports = [
            f"build_matrix/dir_{dr}_{dc}/m_{dr}_{dc}_{mr}_{mc}"
            for dr in range(DIR_ROWS)
            for dc in range(DIR_COLS)
            for mr in range(MOD_ROWS)
            for mc in range(MOD_COLS)
        ]
        fp.write("import (\n")
        for item in imports:
            fp.write(f'\t"{item}"\n')
        fp.write(")\n")
        fp.write("func main() {\n")
        for item in imports:
            fp.write(f"    _ = {item.split('/')[-1]}.F\n")
        fp.write('    fmt.Println("ok")')
        fp.write("}\n")


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
