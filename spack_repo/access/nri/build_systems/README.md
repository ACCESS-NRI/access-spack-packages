# ACCESS-NRI Build Systems

This directory contains shared build system logic and base classes used by ACCESS-NRI Spack packages.

Currently, **`um_base.py`** is the only build system implemented here. It provides the foundation for programs based on the Unified Model (UM), such as `um` and `um-createbc`.

---

## UM Build System (`um_base.py`)

The `um_base.py` module was introduced by refactoring the common logic from the `um` and `um-createbc` Spack package recipes into a shared base class, `UmBasePackage`.

### Hybrid Source Support
The build system supports a "hybrid" source model. A single package version can fetch from either **SVN** (for legacy builds on NCI Gadi) or **GitHub** (for modern development and CI environments) depending on the `model` variant.

To achieve this, the system follows a hierarchical design:
1.  **`UmBasePackage` (`um_base.py`)**: Implements the technical logic for dynamic fetching, environment "wiring", and resource management.
2.  **Product Packages** (`packages/um/`, `packages/um_createbc/`): Inherit from the base class, define specific model variants, and declare GitHub support via the `_github_models` attribute.

### Dynamic Fetch Strategy
Standard Spack recipes use static `git` or `svn` attributes. Because the source location for UM changes based on the `model` variant, `UmBasePackage` overrides the **`fetcher` property**. This allows the recipe to detect when a model has moved to GitHub and bypass legacy SVN mirrors entirely when appropriate.

### Resource Resolution
The system uses a centralized **`_resource_cfg`** dictionary, indexed by project name (e.g., `"um"`, `"jules"`), to manage component metadata:

1.  **`_get_project(project)`**: Retrieves Git metadata (URLs, Tags, SHAs).
2.  **`_get_resource_info(project)`**: Combines Git metadata with the resolved local **`path`** in the staging directory.

| Field | Purpose |
| :--- | :--- |
| **`ref`** | Resolved branch, tag, or commit (handles automatic tagging). |
| **`url`** | The GitHub repository URL for the component. |
| **`sources_var`** | The environment variable name for source overrides (e.g., `jules_sources`). |
| **`location_var`** | The variable name for direct project locations (e.g., `jules_project_location`). |
| **`path`** | The absolute location in the staging directory where the code lives. |

### Environment Management
In the `setup_build_environment` phase, the build system:
- Sets project environment variables (e.g., `jules_project_location`) to their staging paths.
- Clears corresponding `*_sources` variables. This forces the build process to use the calculated project locations, ensuring consistency regardless of the underlying source (SVN or GitHub).

### Usage
Build a supported version with default tagging:
```bash
spack install um@13.8 model=vn13
```

Use a custom branch for a specific subcomponent:
```bash
spack install um@13.8 model=vn13 jules_ref=my_feature_branch
```
