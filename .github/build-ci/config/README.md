# Build CI Custom Config

This folder details build-ci-specific spack configuration that is inherited by all component repositories (CRs) and this `access-spack-packages` (ASP) repository. It is higher precedence than `spack-config`.

It is structured in this format:

```txt
.github/build-ci/config/
├── base
├── include
└── local
```

Each configuration folder included will be explained from highest to lowest precedence below:

## include: Common Entrypoint Include For All CRs/ASP

This folder is explicitly included from all CRs, and ASP manifests, via a section in a manifest (or other included file) like:

```yaml
include:
  - git: https://github.com/ACCESS-NRI/access-spack-packages
    branch: api-v2
    paths:
    - .github/build-ci/config/include
```

Its purpose is to remain a stable include directory in ASP so CRs don't have to be updated to use different paths as things change. Within this directory there is a single `include.yaml` that includes configuration described below, but essentially it contains:

* An optional scope of configuration if `vars.CALLER_REPOSITORY_CONFIG_PATH` is set in special caller repositories. In ASP we use it and call it `local`.
* A `base` scope of configuration.

## local: ASP-specific Config for PRs/Workflows Running In ASP

This configuration directory is only used by ASP. It is used because `vars.CALLER_REPOSITORY_CONFIG_PATH` is set to that path.

This allows custom configuration to be defined in and used by "special repositories" (like ASP, `upstream-spack-packages`, `spack-config`, etc.) that overrides the base config (explained below).

In ASPs case, we want to use the PR branch of `access-spack-packages` as a package repository when building, rather than the default branch.

If we wanted to use a specific ref of `builtin` as well as the PR branch of ASP, we could edit the `repos.yaml` to use a different `builtin` ref here.

## base: Lowest-Precedence Include For Common Config

This configuration directory is the lowest precedence and contains the most common concretization, package and repo settings, to reduce duplication in CRs and ASP.

> [!NOTE]
> This scope shouldn't be edited by users unless they have tested it extensively - it will most likely affect the concretization process for all callers.

If this is specific to ASP, one should put changed config in `local`.
