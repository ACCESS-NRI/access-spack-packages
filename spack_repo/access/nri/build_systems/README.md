# ACCESS-NRI Build Systems

This directory contains shared build system logic and base classes used by ACCESS-NRI Spack packages.

Currently, **`um_base.py`** is the only build system implemented here. It provides the foundation for programs based on the Unified Model (UM), such as `um` and `um-createbc`.

---

## UM Build System (`um_base.py`)

The `um_base.py` module was introduced by refactoring the common logic from the `um` and `um-createbc` Spack package recipes into a shared base class, `UmBasePackage`.

### Hybrid Source Support
The build system supports a "hybrid" source model. A single package version can fetch from either **Subversion** (for legacy builds on NCI Gadi) or **GitHub** (for modern development and CI environments) depending on the `model` variant.

To achieve this, the system follows a hierarchical design:
1.  **`UmBasePackage` (`um_base.py`)**: Implements the technical logic for dynamic fetching, environment "wiring", and resource management.
2.  **Spack Package Recipes** (`packages/um/`, `packages/um_createbc/`): Inherit from the base class, define specific model variants, and declare GitHub support via the `github_models` attribute.

### Dynamic Fetch Strategy
Standard Spack recipes use static `git` or `svn` attributes. Because the source location for UM changes based on the `model` variant, `UmBasePackage` overrides the **`fetcher` property**. This allows the recipe to detect when a model has moved to GitHub and bypass Subversion mirrors entirely when appropriate.

### Project Resolution
The system uses a centralized **`_project_cfg`** dictionary, indexed by project name (e.g., `"um"`, `"jules"`), to manage component metadata. Two helper methods build on this:

1.  **`_project_ref(project)`**: Returns the resolved Git reference (branch, tag, or commit), applying automatic tagging when the corresponding `*_ref` variant is `"none"`.
2.  **`_project_path(project)`**: Returns the absolute path to the project's checkout directory inside the stage (`<source_path>/resources/<project>`).

| Field | Purpose |
| :--- | :--- |
| **`location_var`** | FCM env variable name for direct project location (e.g., `jules_project_location`). |
| **`sources_var`** | FCM env variable name for source overrides (e.g., `jules_sources`). |
| **`url`** | The GitHub repository URL for the component. |
| **`ref_var`** | The variant name holding the Git branch/tag/commit (e.g., `jules_ref`). |

### Environment Management
In `setup_build_environment`, the build system reads the model's `rose-app.conf` and builds a `config_env` dict that is then exported as environment variables. Key steps:

- **Bool variants** (`DR_HOOK`, `eccodes`, `netcdf`): always set; override the model config value.
- **Off/on variants** (`openmp`, `platagnostic`, `thread_utils`): set only when not `"none"`.
- **Revision variants** (`casim_rev`, `jules_rev`, …): set when explicitly specified; otherwise default to `um<version>` if the model config provides no value.
- **Sources and other string variants**: set only when explicitly specified (not `"none"`).
- **Linker flags**: computed via `_get_linker_args()` and placed in `ldflags_<lib>_on` variables.

For **GitHub-sourced models** (`model in github_models`):
- `config_root_path` is set to the staged UM project path; `config_revision` is cleared.
- Each project's `<project>_project_location` and `<project>_sources` variables are both set to the empty string, forcing FCM to use the staged checkout rather than any Subversion or environment-based source definition.

For **Subversion-sourced models**:

### Patching and Checkout
For GitHub-sourced models, `UmBasePackage` handles the checkout of required projects during the **`patch` phase**. The **`_dynamic_resource()`** method:
- Clones components from the ACCESS-NRI GitHub organization into `<source_path>/resources/`.
- Attempts a fast clone using branch names, falling back to a full clone then checkout for specific commits or tags.

### Build Execution
During the **`build` phase**, the system:
1.  Locates the package's default `fcm-make.cfg`.
2.  For GitHub models, generates a **`fcm-make-dynamic.cfg`** in the build directory. This wrapper includes the original configuration but overrides each component's `extract.location` to point to the staged project path.
3.  Invokes `fcm make` with the calculated configuration and a parallel job count.
