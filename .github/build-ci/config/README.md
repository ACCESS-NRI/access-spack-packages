# Build CI Custom Config

This folder details build-ci-specific spack configuration that is inherited by all component repositories (CRs) and this `access-spack-packages` repository. It is higher precedence than `spack-config`.

The structure is:

```txt
.github/build-ci/config/
├── include
├── local
└── base
```

Each configuration folder included will be explained from highest to lowest precedence below:

## include: Common Entrypoint Include For All CRs/`access-spack-packages`

This folder is explicitly included from all CRs, and `access-spack-packages` manifests, via a section in a manifest (or other included file) like:

```yaml
include:
  - git: https://github.com/ACCESS-NRI/access-spack-packages
    branch: api-v2
    paths:
    - .github/build-ci/config/include
```

Its purpose is to remain a stable include directory in `access-spack-packages` so CRs don't have to be updated to use different paths as things change. Within this directory there is a single `include.yaml` that includes configuration described below, but essentially it contains:

* An optional scope of configuration if `vars.CALLER_REPOSITORY_CONFIG_PATH` is set in special caller repositories. In `access-spack-packages` we use it and call it `local`.
* A `base` scope of configuration.

## local: `access-spack-packages`-specific Config for PRs/Workflows Running In `access-spack-packages`

This configuration directory is only used by `access-spack-packages`. It is used because `vars.CALLER_REPOSITORY_CONFIG_PATH` is set to that path.

This allows custom configuration to be defined in and used by "special repositories" (like `access-spack-packages`, `upstream-spack-packages`, `spack-config`, etc.) that overrides the base config (explained below).

In `access-spack-packages`s case, we want to use the PR branch of `access-spack-packages` as a package repository when building, rather than the default branch.

If we wanted to use a specific ref of `builtin` as well as the PR branch of `access-spack-packages`, we could edit the `repos.yaml` to use a different `builtin` ref here.

## base: Lowest-Precedence Include For Common Config

This configuration directory is the lowest precedence and contains the most common settings, to reduce duplication in CRs and `access-spack-packages`.

> [!NOTE]
> This scope should only be edited by `access-spack-packages` maintainers after testing it extensively - it will most likely affect the concretization process for all callers.

If proposed config changes are specific to `access-spack-packages`, one should put them in `local`.
