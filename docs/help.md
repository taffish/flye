Flye 2.9.7-r1

Purpose:
  Assemble PacBio or Oxford Nanopore long reads into contigs and repeat graphs.

Usage:
  taf-flye --pacbio-hifi reads.fastq.gz -o assembly -t 8
  taf-flye flye --nano-hq reads.fastq.gz -o assembly -t 8
  taf-flye -- --help

Common tasks:
  taf-flye --nano-hq reads.fastq.gz --meta -o meta_assembly -t 8
  taf-flye --pacbio-hifi reads.fastq.gz -o assembly -t 8 --resume
  taf-flye --pacbio-hifi reads.fastq.gz --polish-target draft.fasta -o polished -t 8
  taf-flye -- --version

Required inputs:
  FASTA/FASTQ long reads, optionally gzip-compressed; select one read type.
  Read and output paths, including parent directories, must not contain spaces.
  Use a new writable output directory; keep intermediates for --resume.

Common options:
  --pacbio-raw / --pacbio-corr / --pacbio-hifi  PacBio read type.
  --nano-raw / --nano-corr / --nano-hq         ONT read type.
  -o, --out-dir DIR  Output directory (parent must already exist).
  -t, --threads N    Worker threads; choose for available memory and CPU.
  -g, --genome-size SIZE  Genome size, for example 5m; required with --asm-coverage.
  --meta            Uneven-coverage/metagenome mode.
  --resume          Continue the same run using its output directory and inputs.
  --stop-after NAME Stop after a named stage; --resume continues it later.

Key outputs:
  assembly/assembly.fasta       Final contigs.
  assembly/assembly_graph.gfa   Repeat graph for a separate viewer.
  assembly/assembly_info.txt    Contig statistics.
  assembly/flye.log, params.json and stage directories support diagnosis/resume.

Backend-specific use:
  Optional read-only input directory outside the working directory:
  Docker:
    TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS="--volume /data/reads:/reads:ro" taf-flye --pacbio-hifi /reads/sample.fastq.gz -o assembly -t 8
  Podman:
    TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS="--volume /data/reads:/reads:ro" taf-flye --pacbio-hifi /reads/sample.fastq.gz -o assembly -t 8
  Apptainer:
    TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_APPTAINER_RUN_ARGS="--bind /data/reads:/reads:ro" taf-flye --pacbio-hifi /reads/sample.fastq.gz -o assembly -t 8

Immediate notes:
  No database download is needed. Reads stay unchanged; output can be large.
  Do not start a fresh run in an old output directory: it can overwrite results.
  A completed --resume can rerun the final stage; it is not a no-op guarantee.
  Use a space-free working directory for relative paths. Quoting does not fix
  upstream path limitations. Host directories with spaces can be explicitly
  mounted at space-free paths; see README. Avoid quotes and shell metacharacters.

More help:
  taf-flye flye --help
  https://github.com/taffish/flye

Wrapper options:
  taf-flye --help       Show this TAFFISH help.
  taf-flye --version    Show TAFFISH wrapper version.
  taf-flye --compile    Print the generated wrapper shell.
  taf-flye -- --help    Show upstream Flye help.
