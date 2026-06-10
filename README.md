# flye

TAFFISH wrapper for [Flye](https://github.com/mikolmogorov/Flye), a de novo
assembler for single-molecule long reads using repeat graphs.

This app packages Flye `2.9.6` as `taf-flye`. The default in-container command
is `flye`, and TAFFISH command mode is enabled so bundled helper executables
such as `flye-minimap2`, `flye-samtools`, and `flye-modules` can also be called
inside the same runtime environment.

## Installation

```sh
taf install flye
```

Install the exact release:

```sh
taf install flye 2.9.6-r1
```

Before publication to the public index, build locally from this app directory:

```sh
taf build
target/taf-flye-v2.9.6-r1 -- --version
```

## Quick Start

Show TAFFISH package help:

```sh
taf-flye --help
```

Show upstream Flye help and version:

```sh
taf-flye -- --help
taf-flye -- --version
```

Assemble PacBio HiFi reads:

```sh
taf-flye --pacbio-hifi reads.fastq.gz --genome-size 5m \
  --threads 8 --out-dir flye-hifi-out
```

Assemble high-quality ONT reads:

```sh
taf-flye --nano-hq reads.fastq.gz --genome-size 5m \
  --threads 8 --out-dir flye-ont-out
```

Run metaFlye mode for metagenomes or uneven coverage:

```sh
taf-flye --nano-hq reads.fastq.gz --meta \
  --threads 16 --out-dir metaflye-out
```

Run a bundled helper directly through command mode:

```sh
taf-flye flye-minimap2 --version
taf-flye flye-samtools --version
```

## Input Modes

Flye requires one read mode option followed by one or more FASTA/FASTQ files.
Compressed FASTQ input is supported.

Common modes:

- `--pacbio-raw`: PacBio CLR reads.
- `--pacbio-corr`: corrected PacBio reads.
- `--pacbio-hifi`: PacBio HiFi reads.
- `--nano-raw`: regular or older high-error ONT reads.
- `--nano-corr`: corrected ONT reads.
- `--nano-hq`: high-quality ONT reads such as Guppy5+ SUP, Q20, or R10-style
  data.
- `--meta`: metagenome or uneven-coverage assembly mode.

Important parameters:

- `--genome-size`: approximate genome size, such as `5m`, `120m`, or `3g`.
- `--threads`: number of CPU threads.
- `--out-dir`: output directory. Flye manages resume information inside this
  directory.
- `--min-overlap`: minimum overlap, usually left on auto for normal runs.
- `--iterations`: polishing iterations.
- `--resume`, `--resume-from`, `--stop-after`: upstream stage control.

## Outputs

Flye writes all generated files into `--out-dir`. The most important outputs are:

- `assembly.fasta`: assembled contigs.
- `assembly_graph.gfa`: repeat graph in GFA format.
- `assembly_info.txt`: contig length, coverage, circularity, and graph-path
  information.
- `flye.log`: main run log; include this when reporting problems upstream.
- `params.json`: run parameters and provenance.
- intermediate directories used for polishing, repeat resolution, resume, and
  debugging.

## Container

The Dockerfile builds Flye from the upstream `2.9.6` GitHub tag:

```text
https://github.com/mikolmogorov/Flye/archive/refs/tags/2.9.6.tar.gz
sha256: f05a3889b1c7aafed4cc0ed1adc1f19c22618c1c7b97ab5f80d388c8192bd32a
```

The image includes the upstream Python package, compiled C++ modules, bundled
`flye-minimap2`, bundled `flye-samtools`, configuration files, docs, and
upstream toy test data. No external database is required.
`flye --version` reports the upstream runtime string `2.9.6-b1802`; the
packaged upstream release version remains `2.9.6`.
During container build, the Dockerfile applies a narrow build-only Makefile
compatibility patch so Linux `aarch64` containers use Flye's existing ARM NEON
minimap2 build path. No runtime code or scientific defaults are changed.

Native build platforms are declared as `linux/amd64,linux/arm64`. The app does
not require GPU runtime flags.

## Smoke Tests

The TAFFISH smoke metadata is self-contained and offline. It checks:

- `flye`, `flye-modules`, `flye-minimap2`, `flye-samtools`, `python3`, `bash`,
  and `gzip` exist.
- runtime version is exactly `2.9.6-b1802`;
- upstream help exposes core PacBio, ONT, and metagenome modes;
- Python package version imports correctly;
- bundled native executables have no unresolved shared libraries;
- upstream `flye.tests.test_toy` completes successfully.

The toy test assembles the upstream bundled small E. coli fixture. It proves the
container can run a real Flye assembly path, but it is not a scientific
benchmark and does not represent production memory, CPU, or disk requirements.

## Scope and Boundaries

This TAFFISH app preserves the upstream Flye command-line interface. It does not
wrap a separate workflow, add read QC, perform post-assembly polishing with
external tools, annotate contigs, bin metagenomes, phase diploid assemblies, or
visualize graphs. Those steps should be handled by dedicated tools or flows.

Flye can assemble PacBio/ONT long reads and has metagenome mode. It produces
collapsed mosaic assemblies for diploid genomes by default; users who need
haplotype-resolved output should follow upstream Flye/HapDup guidance.

## Upstream

- Project: Flye
- Repository: <https://github.com/mikolmogorov/Flye>
- Manual: <https://github.com/mikolmogorov/Flye/blob/flye/docs/USAGE.md>
- Release: <https://github.com/mikolmogorov/Flye/releases/tag/2.9.6>
- License: BSD-3-Clause
- Main citation for isolate assembly: Kolmogorov et al. 2019,
  doi:10.1038/s41587-019-0072-8
- Main citation for metagenome assembly: Kolmogorov et al. 2020,
  doi:10.1038/s41592-020-00971-x
