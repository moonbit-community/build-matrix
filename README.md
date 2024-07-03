# build-matrix

Port from https://github.com/rescript-lang/build-benchmark

## MoonBit

```bash
$ moon generate-build-matrix -n 6 -o bench6-mbt
$ cd bench6-mbt
$ moon clean && time moon check -q
$ moon clean && time moon build -q
$ cd ..
```

## Go

```bash
$ python3 gen_go.py -n 6 bench6-go
$ cd bench6-go
$ go clean -cache && time go build ./entry/main.go
$ go clean -cache && time go build -gcflags '-N -l' ./entry/main.go
$ cd ..
```

## Rust crates

```bash
$ python3 gen_rs_crate.py -n 6 bench6-rs
$ cd bench6-rs
$ cargo clean && time cargo check -q
$ cargo clean && time cargo build -q
$ cargo clean && time cargo build -q --release
```
