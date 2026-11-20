# Flye

`flye` packages the upstream Flye long-read assembler for TAFFISH.

Package identity:

- name: `flye`
- command: `taf-flye`
- kind: `tool`
- version: `2.9.7-r1`
- license: Apache-2.0 (TAFFISH packaging); BSD-3-Clause (Flye)
- upstream: [mikolmogorov/Flye](https://github.com/mikolmogorov/Flye)

## What This App Packages

The official [Flye 2.9.7 release](https://github.com/mikolmogorov/Flye/releases/tag/2.9.7),
built from source. The default command is `flye`; the wrapper does not replace
its assembly or polishing algorithms. Upstream identifies this release as a
performance update without logical changes. This is not a packaging benchmark
or a promise of bit-identical assemblies: upstream notes inherent nondeterminism.

## Scope

This app supports isolate and metaFlye assembly, upstream polishing, graph output,
and checkpoint-based restart. It runs without a reference database or an online
service. It does not include read QC, independent annotation/binning/phasing tools,
a graph GUI, or a web server.

Flye writes GFA/GV files; [AGB](https://github.com/almiheenko/AGB) and
[Bandage](https://github.com/rrwick/Bandage) are independent downstream viewers.
The assembler does not invoke them. Use a separately installed viewer or
TAFFISH app after assembly; this image does not open ports or supply a browser UI.

## Container Contents

- `flye`: assembly/polishing CLI and Python package, built-in configuration,
  scoring matrices, and the upstream small test dataset.
- `flye-modules`, `flye-minimap2`, `flye-samtools`: bundled helpers used by Flye;
  these are upstream's versions, not replacements for current standalone tools.
- Python 3.11, Bash, gzip, CA certificates and runtime libraries.
- Upstream documentation/licenses at `/opt/flye/share/doc/flye`; bundled third-party
  notices below its `third-party/` directory.

## Usage

Install the version when it is published:

```sh
taf install flye 2.9.7-r1
taf-flye --help
taf-flye -- --help
taf-flye -- --version
```

PacBio HiFi assembly:

```sh
taf-flye --pacbio-hifi reads.fastq.gz -o assembly -t 8
```

ONT high-quality assembly, or uneven coverage:

```sh
taf-flye flye --nano-hq reads.fastq.gz -o ont_assembly -t 8
taf-flye --nano-hq reads.fastq.gz --meta -o meta_assembly -t 8
```

Resume a stopped run, retaining the original inputs and stage directories:

```sh
taf-flye --pacbio-hifi reads.fastq.gz -o assembly -t 8 --resume
```

Run only the upstream polisher:

```sh
taf-flye --pacbio-hifi reads.fastq.gz --polish-target draft.fasta -o polished -t 8
```

## Command Mode

Non-option-leading commands select an executable in the same image:
`taf-flye flye --help`, `taf-flye flye-minimap2 --version`, or
`taf-flye flye-samtools --version`. Wrapper `--help`/`--version` describe the
TAFFISH package; `-- --help`/`-- --version` reach Flye.

## Inputs

FASTA/FASTQ reads may be gzip-compressed; multiple files of the same read type are
allowed. Do not mix read types. Select `--pacbio-raw`, `--pacbio-corr`,
`--pacbio-hifi`, `--nano-raw`, `--nano-corr`, or `--nano-hq` according to the
upstream manual and your data. `--meta` changes the coverage model.

Flye rejects spaces in the absolute path of a read file, including any parent
directory. Its internal samtools calls also fail when the output path contains
spaces. Both are upstream restrictions, not repaired by quoting. Use space-free
read/output paths and working directory, or explicitly mount a read directory at
`/reads:ro` as below. A symlink/explicit mount must remain valid and readable
throughout the run; this app does not search for or download missing input files.

The wrapper joins forwarded arguments into shell text. Use simple filenames
without quote characters, commas or shell metacharacters; do not pass arbitrary
untrusted strings. Shell quoting alone does not make a path with spaces safe for
Flye. The explicit-mount example below handles host directory spaces without
exposing those spaces to Flye's input/output paths.

## Output Notes

`-o DIR` must have an existing writable parent. Main products are
`assembly.fasta`, `assembly_graph.gfa`/`assembly_graph.gv`, and
`assembly_info.txt`; `flye.log`, `params.json` and stage directories enable
diagnosis and restart. GFA edges are not necessarily the same sequences as
extended final contigs. Standalone polishing writes `polished_1.fasta` and
associated statistics for one iteration.

Do not start an unrelated fresh run in an existing output directory: upstream
can overwrite files. Use `--stop-after assembly` to stop at a checkpoint and
`--resume` with the same inputs/output to continue. Completed-run resume is not
transactional idempotency; Flye may rerun its final stage. Missing or damaged
intermediates can require restarting in a new output directory. Preserve the
old directory until the new results have been checked.

## Resources, Databases, and Platform

Linux amd64 and arm64 CPU images are declared; no GPU is used. Configuration,
scoring matrices and the upstream test fixture are small, immutable package
resources tied to Flye 2.9.7. No external database/model/catalog or installer is
needed; project reads and an optional polish target are explicit user inputs.
Normal assembly does not download anything. Large examples linked in upstream
documentation are optional and are not fetched by this image.

Input directories may be shared read-only between users. Their owner supplies
them once, with directory traversal and file-read permissions for each user;
each user runs in a separate writable working/output directory. The wrapper
does not chmod, chown, register, copy or delete shared inputs. No auto-discovery
environment variables or silently selected resource versions are added.

## Backend Usage and Capability Matrix

Ordinary assembly uses the same `taf-flye` arguments on all three backends.
The wrapper encodes the calling UID/GID for Docker and Podman (keep-id user
namespace); Apptainer uses its normal host-user execution. No manual user flags
are required. Select a backend with `TAFFISH_CONTAINER_BACKEND`. The only different syntax
below is an optional explicit read-only directory outside the working directory:

| Capability | Docker | Podman | Apptainer |
| --- | --- | --- | --- |
| Shared reads | `--volume /data/reads:/reads:ro` | `--volume /data/reads:/reads:ro` | `--bind /data/reads:/reads:ro` |

```sh
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS="--volume /data/reads:/reads:ro" taf-flye --pacbio-hifi /reads/sample.fastq.gz -o assembly -t 8
TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS="--volume /data/reads:/reads:ro" taf-flye --pacbio-hifi /reads/sample.fastq.gz -o assembly -t 8
TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_APPTAINER_RUN_ARGS="--bind /data/reads:/reads:ro" taf-flye --pacbio-hifi /reads/sample.fastq.gz -o assembly -t 8
```

Replace `/data/reads` with a directory accessible to the selected container engine.
Docker/Podman Desktop must share that host path. Shared storage or SIF setup is
site policy, not an app-intrinsic flag.

If the host output directory contains spaces, create it first, mount it at a
space-free container path and pass that absolute path to Flye. The inner quotes
below preserve the complete mount specification; they do not change upstream
filename handling. Read filenames within `/data/reads` must still be space-free.

```sh
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS="--volume /data/reads:/reads:ro --volume '/data/run with spaces:/results'" taf-flye --pacbio-hifi /reads/sample.fastq.gz -o /results/assembly -t 8
TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS="--volume /data/reads:/reads:ro --volume '/data/run with spaces:/results'" taf-flye --pacbio-hifi /reads/sample.fastq.gz -o /results/assembly -t 8
TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_APPTAINER_RUN_ARGS="--bind /data/reads:/reads:ro --bind '/data/run with spaces:/results'" taf-flye --pacbio-hifi /reads/sample.fastq.gz -o /results/assembly -t 8
```

## Build and Reproducibility

Official tag `2.9.7`, commit
`f52d39b967441e4b6572d94878b84505f17edb90`; source tar SHA256:
`041635b3b7e7afc69fd50ab9cbf040db4749b04ae626ba65c8b08f550642351f`.
The official display string is `2.9.7-b1802`; build 1802 is unchanged upstream,
not a TAFFISH fabrication.

The existing one-line Makefile compatibility adjustment recognizes Linux
`aarch64` alongside `arm64`, selecting Flye's own ARM NEON minimap2 path.
No runtime Python, algorithm, model or threshold is patched. Debug symbols are
stripped; runtime helpers, data and licenses are retained.

The Debian 12 base is digest-pinned. Debian/security repositories remain rolling:
dependency revisions and availability may change, so rebuilds are not guaranteed
byte-identical. Preserve validated OCI/SIF artifacts/digests; repository changes
require review and revalidation rather than disabling checksums. Build tools and
download caches stay outside the final image. The Action is copied unchanged
from a fresh TAFFISH template; it builds the two native architectures separately.

## Boundaries

Assembly memory/disk use depends strongly on data size and coverage; choose
threads conservatively. `--asm-coverage` requires `--genome-size`. The package
does not claim a speedup, clinical suitability, species-specific accuracy or
production-dataset equivalence. HapDup/strainy and graph viewers remain separate.

## Troubleshooting

- `Path to reads contain spaces`: relocate or explicitly mount reads at a
  space-free container path; quoting does not remove this upstream check.
- A samtools path truncated at a space, or an empty intermediate consensus:
  check the absolute output path and working directory. Preserve the failure log
  and rerun in a new space-free output path; do not accept partial results.
- Cannot resume: retain `params.json` and all stage outputs. Use the same input
  paths; do not delete or overwrite the previous directory to suppress an error.
- Permission denied: verify shared-file readability and output-parent ownership.
  Use your ordinary UID; do not make an immutable image or shared input writable.
- A failed process or exhausted memory: inspect `flye.log`, available RAM/disk
  and threads; do not treat partial output as a finished assembly.
- “command not found” in a viewer: AGB/Bandage are independent installations.

## Testing

Build-time gates cover exact version/status, imports, help, helper executables,
shared libraries and bundled files. Full assembly is intentionally a runtime
gate, not a heavy ARM64 Dockerfile assertion.

Release verification uses the fixed upstream toy fixture, detached fresh
containers, no network, read-only-root ordinary users and real generated
wrappers. It checks output structure rather than nondeterministic assembly
byte equality. Native platform/backend results, artifact identities, resume,
shared-input integrity, negative cases, permissions and cleanup are recorded in
the maintainer release evidence. No production data or external database is
downloaded for these checks; they are packaging verification, not scientific
validation.

## License and Citation

TAFFISH packaging: Apache-2.0. Flye: BSD-3-Clause. Bundled components retain their
own license notices in the image; see `third-party/` under the upstream docs.

- Kolmogorov et al. (2019), [Assembly of long, error-prone reads using repeat graphs](https://doi.org/10.1038/s41587-019-0072-8).
- Kolmogorov et al. (2020), [metaFlye: scalable long-read metagenome assembly using repeat graphs](https://doi.org/10.1038/s41592-020-00971-x).
- [Versioned upstream manual](https://github.com/mikolmogorov/Flye/blob/2.9.7/docs/USAGE.md).
