# UM Build System Architecture

This directory contains the central build system logic for the Unified Model (UM) and associated programs like `um-createbc`. 

## Core Principles

The UM Spack recipes are designed to handle a "hybrid" migration: a single package version (e.g., `13.0`) must be able to fetch from **SVN** (for legacy builds on NCI Gadi) or **GitHub** (for CI environments and modern development) depending on chosen variants.

To achieve this, the system follows a hierarchical design:
1.  **`UmBasePackage` (`um_base.py`)**: Implements the technical logic for dynamic fetching, environment "wiring", and resource management.
2.  **Product Packages** (`packages/um/`, `packages/um_createbc/`): Define specific model variants and declare which models are "GitHub-enabled" via the `_github_models` attribute.

---

## Dynamic Fetch Strategy

Standard Spack recipes use static `git` or `svn` attributes. Because the source location for UM changes based on the `model` variant, we override the **`fetcher` property** in `UmBasePackage`.

### Why `@property`?
- **Lifecycle timing**: Spack's engine reads the `fetcher` attribute at the very start of the installation. By making it a decorated property, we can run a check against the user's `spec` variants dynamically.
- **CI Compatibility**: This allows the recipe to detect when a model has moved to GitHub and bypass the Gadi-specific `/g/data` SVN mirrors entirely, enabling the recipes to build in GitHub Actions.

## Resource Resolution

`UmBasePackage` uses a two-tiered resolution system to manage component metadata and file paths while avoiding circular dependencies with Spack's staging engine:

1.  **`_get_git_info(ref_var)`**: Retrieves pure Git metadata (URLs, Tags, SHAs). This is used by the `@property fetcher` to identify remote sources without needing to know the local file path.
2.  **`_get_resource_info(ref_var)`**: A wrapper that combines the Git metadata with the resolved local **`path`** in the staging directory. This is used during the `patch` and `build` phases.

| Field | Purpose | Provided By |
| :--- | :--- | :--- |
| **`ref`** | Resolved branch, tag, or commit (handles automatic tagging). | Both |
| **`url`** | The GitHub repository URL for the component. | Both |
| **`sources_var`** | The specific environment variable expected by FCM (e.g., `jules_sources`). | Both |
| **`path`** | The absolute location in the staging directory where the code lives. | `_get_resource_info` |

The `fetcher` uses the metadata function to enforce schema integrity; if a mandatory field is missing in the configuration, the build will fail immediately with a clear `KeyError`.

---

## Automatic Tagging Logic

If a git reference variant (e.g., `um_ref`) is set to `none`, the base class automatically calculates the appropriate tag:

| Component | GitHub Repository | Tag Convention | Note |
| :--- | :--- | :--- | :--- |
| **UM** | `ACCESS-NRI/UM` | `UKMO_vn<version>` | e.g., `UKMO_vn13.5` |
| **JULES** | `ACCESS-NRI/JULES` | `JULES_vn<version-6.0>` | e.g., `JULES_vn7.5` for UM 13.5 |
| **Others** | `casim`, `ukca`, etc. | `um<version>` | e.g., `um13.5` |

## Build Lifecycle

FCM (the UM build tool) expects subcomponent sources to be placed in specific locations. The Spack recipe handles this in two phases:

1.  **Environment Management** (`setup_build_environment`): It "wires" the environment by setting variables like `jules_sources` to their expected paths.
2.  **Source Fetching** (`patch`): It physically populates those paths using `git clone` or checkout. The core UM source is handled natively by Spack's primary fetcher and is reused in the staging area to avoid redundant downloads.

---

## Usage

Build the latest supported version with default tagging:
```bash
spack install um@13.5 model=vn13
```

Use a custom branch for a specific subcomponent:
```bash
spack install um@13.1 model=vn13p1-am ukca_ref=my_feature_branch
```
