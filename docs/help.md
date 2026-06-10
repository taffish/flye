taf-flye 2.9.6-r1

TAFFISH wrapper for Flye, a de novo assembler for PacBio and Oxford
Nanopore long reads using repeat graphs. The default in-container command is
flye.

Usage:
  taf-flye [flye options]
  taf-flye -- [flye options]
  taf-flye flye [flye options]
  taf-flye flye-minimap2 [options]
  taf-flye flye-samtools [options]

Wrapper options:
  -h, --help       Show this TAFFISH help
  -v, --version    Show the TAFFISH package version
  --compile        Print generated shell code instead of running it
  --               Stop parsing TAFFISH wrapper options

Common upstream Flye examples:
  taf-flye -- --help
  taf-flye -- --version

  taf-flye --pacbio-hifi reads.fastq.gz --genome-size 5m \
    --threads 8 --out-dir flye-hifi-out

  taf-flye --nano-hq ont-q20.fastq.gz --genome-size 5m \
    --threads 8 --out-dir flye-ont-out

  taf-flye --nano-raw ont-raw.fastq.gz --genome-size 5m \
    --threads 8 --out-dir flye-raw-out

  taf-flye --nano-hq reads.fastq.gz --meta \
    --threads 16 --out-dir metaflye-out

Input modes:
  --pacbio-raw       PacBio CLR reads, typically below 20% error.
  --pacbio-corr      PacBio reads corrected by another method.
  --pacbio-hifi      PacBio HiFi reads, typically below 1% error.
  --nano-raw         Oxford Nanopore regular reads, older/high-error mode.
  --nano-corr        Corrected Oxford Nanopore reads.
  --nano-hq          ONT high-quality reads, such as Guppy5+ SUP or Q20/R10.
  --meta             Metagenome or uneven-coverage assembly mode.

Outputs:
  Flye writes all assembly outputs into --out-dir. Typical important files
  include assembly.fasta, assembly_graph.gfa, assembly_info.txt, flye.log,
  params.json, and intermediate files used for resume/debugging.

Included executables:
  flye
  flye-modules
  flye-minimap2
  flye-samtools

Notes:
  - This app packages Flye 2.9.6 from the upstream GitHub tag.
  - Upstream flye --version reports 2.9.6-b1802 for this release.
  - The TAFFISH wrapper is intentionally thin and preserves the upstream CLI.
  - command_mode is enabled: taf-flye flye-minimap2 ... runs bundled helpers
    inside the same container.
  - No external database is required.
  - Large assemblies can be CPU, memory, and disk intensive. Smoke tests only
    run the upstream toy test and do not represent production resource needs.
  - Flye produces a collapsed mosaic assembly for diploid genomes by default;
    use Flye/HapDup guidance if phased haplotypes are required.

Upstream:
  homepage: https://github.com/mikolmogorov/Flye
  manual:   https://github.com/mikolmogorov/Flye/blob/flye/docs/USAGE.md
  release:  https://github.com/mikolmogorov/Flye/releases/tag/2.9.6
