# UM Build System Architecture

This directory contains the core build system logic for the Unified Model (UM) and its associated utility programs, such as `um-createbc`.

## Overview

The UM Spack packages follow a hierarchical design to minimize code duplication and ensure consistency across models:

1.  **`UmBasePackage` (`um_base.py`)**: A base class that inherits from Spack's `Package`. It provides the core implementation for:
    *   **Unified Variants**: Logic for revisions (`*_rev`), git references (`*_ref`), and local sources (`*_sources`).
    *   **GitHub-Enabled Variants**: The `_github_models` attribute (defaulting to empty) determines which model variants trigger the GitHub-based build logic.
    *   **Environment Management**: The `setup_build_environment` method, which handles dependency paths (GCOM, FCM, FIAT) and performs automatic redirection of `config_root_path` for GitHub-based models.
    *   **GitHub Integration**: The `patch` and `_dynamic_resource` methods for checking out subcomponents from GitHub with specialized tagging logic.
2.  **Package Classes**:
    *   **`Um` (`packages/um/package.py`)**: Inherits from `UmBasePackage`. It defines the specific model variants (e.g., `vn13`, `vn13p1-am`) and provides the logic for installing the main atmosphere and reconfiguration executables. It defines `_github_models = ("vn13", "vn13p1-am")`.
    *   **`UmCreatebc` (`packages/um_createbc/package.py`)**: Inherits from `UmBasePackage`. It manages the `um_createbc.exe` utility program, specifically used for the creation of lateral boundary conditions. It defines `_github_models = ("vn13",)`.

## GitHub Migration

Starting with the `vn13` series, the build system supports fetching subcomponent sources from GitHub instead of the legacy SVN (MOSRS). 

> [!NOTE]
> The list of supported models in the `Um` and `UmCreatebc` classes will evolve over time. The exact models available depend on which model variants have been migrated to the GitHub-based infrastructure and which ones remain on the legacy SVN system.

### Automatic Tagging Logic

When a git reference variant (e.g., `um_ref`, `jules_ref`) is set to `none`, `UmBasePackage` automatically determines the appropriate tag based on the UM version:

| Component | GitHub Repository | Tag Convention | Note |
| :--- | :--- | :--- | :--- |
| **UM** | `ACCESS-NRI/UM` | `UKMO_vn<version>` | e.g., `UKMO_vn13.5` |
| **JULES** | `ACCESS-NRI/JULES` | `JULES_vn<version-6.0>` | e.g., `JULES_vn7.5` for UM 13.5 |
| **Others** | `casim`, `ukca`, etc. | `um<version>` | e.g., `um13.5` |

### Source Precedence

The build system determines sources in the following order of priority:

1.  **Local Sources** (`*_sources`): Highest priority. Uses a local directory.
2.  **Git Reference** (`*_ref`): Clones from GitHub using the specified branch, tag, or commit.
3.  **Automatic Tagging**: Used if the selected `model` variant is GitHub-enabled and no explicit `*_ref` is provided.
4.  **Svn Revision** (`*_rev`): Legacy fallback for MOSRS-based builds.

## Build Lifecycle

The build system interacts with GitHub-sourced components in two distinct phases to ensure the FCM build system functions correctly:

1.  **Environment Management** (`setup_build_environment`): In this phase, the build system "wires" the environment by setting variables like `jules_sources` to their expected paths. This informs FCM where to look for source code, overriding its internal defaults.
2.  **Source Fetching** (`patch`): In this phase, the build system physically populates those paths. It performs the `git clone` or checkout operations to fetch the actual source code into the staging area.

This dual-phase approach is necessary because UM subcomponent versions are determined dynamically based on Spack variants, which prevents the use of standard static `resource()` directives.

## Usage

Users can typically build the latest supported version with default tagging:

```bash
spack install um@13.5 model=vn13
```

To use a custom branch for a specific subcomponent:

```bash
spack install um@13.1 model=vn13p1-am ukca_ref=my_feature_branch
```

For more details on available variants and descriptions, run `spack info um`.
