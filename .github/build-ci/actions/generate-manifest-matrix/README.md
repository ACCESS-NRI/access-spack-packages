# Generate Manifest Matrix

Action that generates a GitHub Actions matrix of repository, manifest path, and package tuples for passing to `ACCESS-NRI/build-ci`.

> [!NOTE]
> Requires an installation of spack on the runner to be able to interpolate `git` variables

## Description

For each provided package, this action discovers build manifests in the following order:

1. Read `git = "..."` from the package's `package.py`, if it exists, clone that repository and search for manifests under `.github/build-ci/manifests`.
2. Search this repository under `.github/build-ci/manifests/<package>/`.
3. If none are found in 1 or 2, use default manifests under `.github/build-ci/manifests/`.

Each matrix entry contains:

- `template_value`: package name with underscores converted to hyphens, suitable for jinja templating the package name in the manifest
- `repository`: source repository in `owner/repo` format
- `ref`: Git commit checked out from the above repository
- `filepath`: path to the selected manifest template, relative to the repository

## Inputs

| Name | Type | Description | Required | Default | Examples |
| ---- | ---- | ----------- | -------- | ------- | -------- |
| `packages` | `string` (space-separated) | Space-separated list of spack package names to generate matrix entries for | `true` | N/A | `"mom5 cice5 cable"` |
| `ref` | `string` (git ref) | Ref for the fallback access-spack-packages repository to checkout | `false` | Default branch of `access-spack-packages`, `api-v*` | `api-v2` |
| `token` | `string` (GitHub PAT) | GitHub PAT with access to the repositories to checkout and read from. Only required if any of the repositories are private | `false` | `github.token` | `gh_pat_XXX` |

## Outputs

| Name | Type | Description |
| ---- | ---- | ----------- |
| `matrix` | JSON array | A GitHub Actions matrix of `{template_value, repository, ref, filepath}` tuples |
| `exclude-matrix` | JSON array | A GitHub Actions matrix of packages to exlude from matrix generation |

## Example

### Basic Usage

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.gen-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4

      - id: gen-matrix
        uses: ./.github/build-ci/actions/generate-manifest-matrix
        with:
          packages: "mom5 cice5"
          packages-root-dir: spack_repo/access/nri/packages

  test:
    needs: setup
    strategy:
      matrix:
        packages: ${{ fromJson(needs.setup.outputs.matrix) }}
        exclude: ${{ fromJson(needs.setup.outputs.exclude-matrix) }}
    uses: access-nri/build-ci/.github/workflows/ci.yml@v3
    with:
      spack-manifest-repository: ${{ matrix.config.repository }}
      spack-manifest-path: ${{ matrix.config.filepath }}
      ref: ${{ matrix.config.ref }}
      spack-manifest-data-pairs: |-
        package ${{ matrix.config.template_value }}
```

## Example Output

### Matrix

```json
[
  {
    "template_value": "mom5",
    "repository": "ACCESS-NRI/MOM5",
    "ref": "main",
    "filepath": ".github/build-ci/manifests/intel.spack.yaml.j2"
  },
  {
    "template_value": "cice5",
    "repository": "ACCESS-NRI/access-spack-packages",
    "ref": "main",
    "filepath": ".github/build-ci/manifests/cice5/intel.spack.yaml.j2"
  },
  {
    "template_value": "cice5",
    "repository": "access-nri/access-spack-packages",
    "ref": "main",
    "filepath": ".github/build-ci/manifests/cice5/gcc.spack.yaml.j2"
  }
]
```

### Exclude Matrix

In this example, the packages below are excluded because they are all Spack Bundle Recipes (SBRs), which are tested and deployed separately in Model Deployment Repositories (MDRs).

```json
[
  "access-om2",
  "access-om2-bgc",
  "access-om3",
  "access-esm1p5",
  "access-esm1p6",
  "access-am3",
  "access-ram3",
  "access-issm",
  "access-test",
  "coastri-roms"
]
```

## Notes

- `repository` is extracted from HTTPS git URLs in `owner/repo` format.
- Manifest discovery supports `.yml`, `.yaml`, and `.j2`.
