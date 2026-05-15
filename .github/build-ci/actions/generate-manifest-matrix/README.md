# Generate Manifest Matrix

Action that generates a GitHub Actions matrix of manifest paths and package names for spack package testing.

## Description

For each provided package, this action discovers spack build manifests by:

1. Looking for package-specific manifests in this repository under `.github/build-ci/manifests/<package>/`
2. Falling back to default manifests in this repository under `.github/build-ci/manifests/`

The action returns a matrix suitable for use with `strategy.matrix` in a GitHub Actions workflow, where each entry contains the package name, and manifest file path.

## Inputs

| Name | Type | Description | Required | Default |
| ---- | ---- | ----------- | -------- | ------- |
| `packages` | string (space-separated) | Space-separated list of spack package names to generate matrix entries for | true | N/A |

## Outputs

| Name | Type | Description |
| ---- | ---- | ----------- |
| `matrix` | JSON array | A GitHub Actions matrix of `{template_value, filepath}` tuples |

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
          packages: "mom5 cice5 cable"

  test:
    needs: setup
    strategy:
      matrix:
        config: ${{ fromJson(needs.setup.outputs.matrix) }}
    uses: access-nri/build-ci/.github/workflows/ci.yml@v3
    with:
      spack-manifest-path: ${{ matrix.config.filepath }}
      spack-manifest-data-pairs: |-
        package ${{ matrix.config.template_value }}
```

## Example Output

For packages with git URLs defined in their `package.py`:

```json
[
  {"template_value": "mom5", "filepath": ".github/build-ci/manifests/intel.spack.yaml.j2"},
  {"template_value": "mom5", "filepath": ".github/build-ci/manifests/gcc.spack.yaml.j2"},
  {"template_value": "cice5", "filepath": ".github/build-ci/manifests/cice5/spack.yaml.j2"},
  {"template_value": "cable", "filepath": ".github/build-ci/manifests/cable/intel.spack.yaml.j2"}
]
```

## Notes

- The action automatically handles package name normalization (underscores to hyphens for `template_value`)
