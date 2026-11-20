"""Private offline packaging checks; not a replacement for the Flye CLI."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

VERSION = "2.9.7"
DISPLAY_VERSION = "2.9.7-b1802"
stage = "arguments"


def run(argv, cwd=None, timeout=480):
    child = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = child.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        # This PID is exactly the session/process group created above.
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = child.communicate(timeout=10)
    result = subprocess.CompletedProcess(argv, 124 if timed_out else child.returncode, stdout, stderr)
    if result.returncode:
        sys.stderr.write((result.stdout + result.stderr).decode(errors="replace")[-12000:])
        raise RuntimeError(f"child_exit={result.returncode} timed_out={timed_out} argv={argv!r}")
    return result


def exact_version(result):
    return (result.returncode == 0 and result.stdout == (DISPLAY_VERSION + "\n").encode()
            and result.stderr == b"")


def identity():
    global stage
    stage = "version"
    result = run(["flye", "--version"])
    assert exact_version(result), repr((result.stdout, result.stderr))
    from flye.__version__ import __version__
    from flye.__build__ import __build__
    assert __version__ == VERSION and __build__ == 1802
    stage = "help"
    help_text = run(["flye", "--help"]).stdout.decode()
    for token in ("Assembly of long reads with repeat graphs", "--pacbio-hifi",
                  "--pacbio-corr", "--nano-hq", "--nano-raw", "--meta", "--resume",
                  "--polish-target", "--stop-after"):
        assert token in help_text, token
    stage = "helpers-and-libraries"
    for executable in ("flye-modules", "flye-minimap2", "flye-samtools"):
        path = shutil.which(executable)
        assert path, executable
        linked = run(["ldd", path])
        assert b"not found" not in linked.stdout + linked.stderr, executable
    stage = "bundled-resources"
    import flye
    root = Path(flye.__file__).parent
    for subdir in ("config/bin_cfg", "tests/data"):
        files = list((root / subdir).glob("*"))
        assert files and all(f.is_file() and f.stat().st_size for f in files), subdir
    assert (Path("/opt/flye/share/doc/flye") / "LICENSE").is_file()


def verify_assembly(output):
    output = Path(output)
    for name in ("assembly.fasta", "assembly_graph.gfa", "assembly_info.txt", "flye.log", "params.json"):
        assert (output / name).stat().st_size > 0, name
    fasta = (output / "assembly.fasta").read_text()
    assert fasta.startswith(">") and sum(len(line) for line in fasta.splitlines() if not line.startswith(">")) > 1000
    assert any(line.startswith("S\t") for line in (output / "assembly_graph.gfa").read_text().splitlines())
    assert len((output / "assembly_info.txt").read_text().splitlines()) >= 2
    assert isinstance(json.loads((output / "params.json").read_text()), dict)


def assembly():
    global stage
    import flye
    reads = Path(flye.__file__).parent / "tests/data/ecoli_500kb_reads_hifi.fastq.gz"
    with tempfile.TemporaryDirectory(prefix="taf-flye-smoke-") as scratch:
        output = Path(scratch) / "assembly"
        stage = "toy-assembly"
        run(["flye", "--pacbio-corr", str(reads), "-g", "500k", "-o", str(output), "-t", "2", "-m", "1000"])
        stage = "assembly-outputs"
        verify_assembly(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("identity", "assembly"))
    args = parser.parse_args()
    try:
        globals()[args.mode]()
    except Exception as error:
        print(f"FLYE_SMOKE_FAILURE stage={stage} exit=1 {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(f"FLYE_SMOKE_PASS {args.mode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
