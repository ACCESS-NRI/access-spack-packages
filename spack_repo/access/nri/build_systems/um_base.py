# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# Copyright 2024-2026 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py

import configparser
from spack_repo.builtin.build_systems.generic import Package
from spack.util.executable import ProcessError
from spack.package import *
import spack.llnl.util.tty as tty
import spack.util.git
import spack.fetch_strategy as fs

class UmBasePackage(Package):
    """
    UmBasePackage is the base build system class for numerical weather
    prediction and climate modelling software packages based on
    the UK Met Office and Momentum Partnership Unified Model.
    """

    homepage = "https://code.metoffice.gov.uk/trac/um"
    _svn_mirror = "file:///g/data/ki32/mosrs/um/main/trunk"

    # See 'fcm kp fcm:um.xm' for release versions.
    # Needed only for Subversion builds.
    _revision = {
        "13.0": 111272,
        "13.1": 114076,
        "13.2": 116723,
        "13.3": 118802,
        "13.4": 120750,
        "13.5": 123226,
        "13.6": 124981,
        "13.7": 127030,
        "13.8": 128625,
        "13.9": 130128,
    }
    _max_minor = 9
    for v in range(1 + _max_minor):
        _version = f"13.{v}"
        version(_version, revision=_revision[_version], preferred=(v == 8))

    maintainers("penguian")

    _projects = (
        "casim",
        "jules",
        "shumlib",
        "socrates",
        "ukca",
        "um",
    )

    # Bool variants have their default value set to True here.
    _bool_variants = (
        "DR_HOOK",
        "eccodes",
        "netcdf")
    for var in _bool_variants:
        variant(var, default=True, description=var)

    # Off/on variants have 3-value "none" "off", "on" logic.
    _off_on_variants = (
        "openmp",
        "platagnostic",
        "thread_utils")
    for var in _off_on_variants:
        variant(var, default="none", description=var,
            values=("none", "off", "on"), multi=False)

    # String variants have their default values set to "none" here.
    # For all string variants other than Git reference variants,
    # the real default is set by the model.

    # Project-based collections.

    # Revision variants. Needed only for Subversion sources.
    _rev_variants = []
    # Sources variants.  Needed only for Subversion sources.
    _sources_variants = []
    # Configuraion items to use when GitHub sources are needed.
    _project_cfg = {}

    for _project in _projects:
        # Revision variants.
        if _project != "um":
            _rev_var = f"{_project}_rev"
            _rev_variants.append(_rev_var)
            variant(_rev_var, default="none", values="*", multi=False,
                description=f"Subversion revision for {_project}. "
                            f"Defaults to automatic versioning if 'none'.")

        # Sources variants
        _sources_var = f"{_project}_sources"
        _sources_variants.append(_sources_var)
        variant(_sources_var, default="none", values="*", multi=False,
            description=f"FCM diff extract location of {_project}.")

        # Git reference variants.
        _ref_var = f"{_project}_ref"
        variant(_ref_var, default="none", values="*", multi=False,
            description=f"Git branch/tag/commit for {_project}. "
                        f"Overrides Subversion. "
                        f"Defaults to automatic tagging if 'none'.")

        # Configuraion items to use when GitHub sources are needed.
        _project_cfg[_project] = {
            "location_var": f"{_project}_project_location",
            "sources_var": f"{_project}_sources",
            "url": f"https://github.com/ACCESS-NRI/{_project}.git",
            "ref_var": _ref_var,
        }

    # Other string variants.
    _other_variants = [
        "compile_atmos",
        "compile_createbc",
        "compile_crmstyle_coarse_grid",
        "compile_pptoanc",
        "compile_recon",
        "compile_scm",
        "compile_sstpert_lib",
        "compile_wafccb_lib",
        "config_revision",
        "config_root_path",
        "config_type",
        "COUPLER",
        "extract",
        "fcflags_overrides",
        "gwd_ussp_precision",
        "jules_sources",
        "land_surface_model",
        "ldflags_overrides_prefix",
        "ldflags_overrides_suffix",
        "ls_precipitation_precision",
        "mirror",
        "mpp_version",
        "optimisation_level",
        "platform_config_dir",
        "portio_version",
        "prebuild",
        "recon_mpi",
        "stash_version",
        "timer_version",
    ]

    for _var in _other_variants:
        variant(_var, default="none", values="*", multi=False, description=_var)

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    # The 'site=nci-gadi' variant of fcm defines the keywords
    # used by the FCM configuration of UM.
    depends_on("fcm site=nci-gadi", type="build")
    depends_on("fiat@um", type=("build", "link", "run"),
        when="+DR_HOOK")
    depends_on("eccodes +fortran +netcdf", type=("build", "link", "run"),
        when="+eccodes")
    depends_on("netcdf-fortran@4.5.2", type=("build", "link", "run"),
        when="+netcdf")

    phases = ["build", "install"]

    # The dependency name, include paths, and ld_flags from
    # the FCM config for each library configured via FCM.
    _lib_cfg = {
        "DR_HOOK": {
            "includes": [
                join_path("include", "fiat"),
                join_path("module", "fiat"),
                join_path("module", "parkind_dp")],
            "dep_name": "fiat",
            "fcm_name": "drhook",
            "fcm_ld_flags": "-lfiat -lparkind_dp"},
        "eccodes": {
            "includes": ["include"],
            "dep_name": "eccodes",
            "fcm_name": "eccodes",
            "fcm_ld_flags": "-leccodes_f90 -leccodes"},
        "netcdf": {
            "includes": ["include"],
            "dep_name": "netcdf-fortran",
            "fcm_name": "netcdf",
            "fcm_ld_flags": "-lnetcdff -lnetcdf"}}

    # List of model variants that have Github sources.
    # Should be overridden by child classes.
    github_models = ()

    # List of projects to be used by this package.
    # Defaults to all projects.
    # Should be overridden by child classes if needed.
    projects_needed = _projects

    def _config_file_path(self, model):
        """
        Return the pathname of the Rose app config file
        corresponding to model.
        """
        return join_path(
            self.package_dir, "model", model, "rose-app.conf")


    def _project_ref(self, project):
        """
        Return the git reference for a resource, applying automatic tagging
        if the variant is 'none'.
        """
        spec = self.spec
        ref_var = self._project_cfg[project]["ref_var"]
        ref_value = spec.variants[ref_var].value
        if ref_value == "none":
            if ref_var == "um_ref":
                return f"UKMO_vn{spec.version}"
            if ref_var == "jules_ref":
                # JULES version = UM version - 6.0
                return f"JULES_vn{spec.version[0] - 6}.{spec.version[1]}"
            return f"um{spec.version}"
        return ref_value


    def _project_path(self, project):
        """
        Return the absolute path to a resource in the stage directory.
        """
        return join_path(self.stage.source_path, "resources", project)


    @property
    def fetcher(self):
        """
        Return the fetch strategy based on the model variant.
        """
        spec = self.spec
        model = spec.variants["model"].value
        if model in self.github_models:
            # GitHub: Return a Git fetch strategy
            project = "um"
            cfg = self._project_cfg[project]
            url = cfg["url"]
            ref = self._project_ref(project)
            return fs.from_kwargs(git=url, tag=ref)
        else:
            # Subversion: Return a Subversion fetch strategy
            # Recover the revision from the version definition if available
            rev = None
            if spec.version in self.versions:
                rev = self.versions[spec.version].get("revision")
            return fs.from_kwargs(svn=self._svn_mirror, revision=rev)


    def _get_linker_args(self, spec, fcm_libname):
        """
        Return the linker flags corresponding to fcm_libname,
        a library name configured via FCM.
        """
        dep_name = self._lib_cfg[fcm_libname]["dep_name"]
        ld_flags = [
            spec[dep_name].libs.ld_flags,
            self._lib_cfg[fcm_libname]["fcm_ld_flags"]]
        # The reason for the explicit -rpath is:
        # https://github.com/ACCESS-NRI/access-spack-packages/issues/14#issuecomment-1653651447
        rpaths = ["-Wl,-rpath=" + d for d in spec[dep_name].libs.directories]

        # Both ld_flags and rpaths are lists of strings.
        return " ".join(ld_flags + rpaths)


    def setup_build_environment(self, env):
        """
        Set environment variables to their required values.
        """

        def check_model_vs_spec(model, config_env, var, spec_value):
            """
            Check whether the value spec_value for the variant var
            agrees with the model's configured value config_env[var],
            and produce an appropriate warning or debug message.
            """
            if var not in config_env:
                tty.warn(
                    f"The {model} model does not specify {var}. "
                    f"The value {spec_value} will be used.")
            else:
                model_value = config_env[var]
                if model_value != "" and model_value != spec_value:
                    tty.warn(
                        f"The {model} model sets {var}={model_value} but "
                        f"the spec sets {var}={spec_value}. "
                        f"The value {spec_value} will be used.")


        def check_model_vs_project(
            model,
            config_env,
            project_cfg):
            """
            This function is needed while some models still use Subversion.
            Check the values set by the variant sources_var against any
            existing sources value in config_env, and remind the user
            that the sources_var value and the location_var value will
            be overridden by the empty string.
            """
            sources_var = project_cfg["sources_var"]
            location_var = project_cfg["location_var"]
            sources_value = spec.variants[sources_var].value
            if sources_value == "none":
                # In this case, the spec value for sources_var has not
                # overridden the model configuration value, if any.
                if sources_var not in config_env:
                    tty.info(
                        f"The {model} model does not specify {sources_var}.")
                else:  # sources_var in config_env
                    env_value = config_env[sources_var]
                    if env_value == "":
                        tty.info(
                            f"The {model} model sets {sources_var}=''.")
                    else:
                        tty.warn(
                            f"The {model} model sets "
                            f"{sources_var}={env_value}.")
            else:  # sources_value != "none"
                # In this case, the spec value for sources_var has already
                # overridden the model configuration value, if any.
                assert sources_value == config_env[sources_var]
                tty.warn(f"The spec sets {sources_var}={sources_value}.")
            tty.info(
                f"Both {location_var} and {sources_var} will be set to the empty string."
            )


        def check_model_vs_root_path_vs_um_ref(
            model,
            config_env,
            project_path):
            """
            Check the values set by the variants "config_root_path" and "um_ref"
            against any existing config_root_path value in config_env, and remind
            that the config_root_path value will be overridden by project_path.
            """
            root_path_var = "config_root_path"
            ref_var = self._project_cfg["um"]["ref_var"]
            root_path_value = spec.variants[root_path_var].value
            ref_value = spec.variants[ref_var].value
            tty.info(f"The spec sets {ref_var}={ref_value}")
            if root_path_value == "none":
                # In this case, the spec value for root_path_var has not
                # overridden the model configuration value, if any.
                if root_path_var not in config_env:
                    tty.info(
                        f"The {model} model does not specify {root_path_var}.")
                else:  # root_path_var in config_env
                    env_value = config_env[root_path_var]
                    if env_value == "":
                        tty.info(
                            f"The {model} model sets {root_path_var}=''.")
                    else:
                        tty.warn(
                            f"The {model} model sets "
                            f"{root_path_var}={env_value}.")
            else:  # root_path_value != "none"
                # In this case, the spec value for root_path_var has already
                # overridden the model configuration value, if any.
                assert root_path_value == config_env[root_path_var]
                tty.warn(f"The spec sets {root_path_var}={root_path_value}.")
            tty.info(
                f"The value {project_path} will be used for {root_path_var}.")
            tty.info("The config_revision will be set to the empty string.")


        spec = self.spec

        # Use rose-app.conf to set config options.
        config = configparser.ConfigParser()
        # Ensure that keys are case sensitive.
        # https://docs.python.org/3/library/configparser.html#customizing-parser-behaviour
        config.optionxform = lambda option: option
        model = spec.variants["model"].value
        config.read(self._config_file_path(model))

        # Modify the config as per points 8 and 9 of
        # https://metomi.github.io/rose/2019.01.8/html/api/configuration/rose-configuration-format.html
        config_env = {}
        for key in config["env"]:
            if len(key) > 0 and key[0] != '!':
                config_env[key] = config["env"][key].replace("\n=", "\n")

        # Override the model UM revision based on the spec UM version.
        key = "um_rev"
        spec_um_rev = f"vn{spec.version}"
        check_model_vs_spec(model, config_env, key, spec_um_rev)
        config_env[key] = spec_um_rev

        # Override those environment variables where a bool variant is specified.
        bool_to_str = lambda b: "true" if b else "false"
        for var in self._bool_variants:
            spec_str_value = bool_to_str(spec.variants[var].value)
            check_model_vs_spec(model, config_env, var, spec_str_value)
            config_env[var] = spec_str_value

        # Override those environment variables where an off/on variant is specified.
        off_on_to_str = lambda off_on: "true" if off_on == "on" else "false"
        for var in self._off_on_variants:
            spec_value = spec.variants[var].value
            if spec_value != "none":
                spec_str_value = off_on_to_str(spec_value)
                check_model_vs_spec(model, config_env, var, spec_str_value)
                config_env[var] = spec_str_value

        # Override those environment variables where a revision variant is specified.
        # If the variant is left unspecified, and the model does not specify a revision,
        # then use a component revision based on the spec UM version.
        for var in self._rev_variants:
            spec_value = spec.variants[var].value
            if spec_value != "none":
                check_model_vs_spec(model, config_env, var, spec_value)
                config_env[var] = spec_value
            elif var not in config_env or config_env[var] == "":
                config_env[var] = f"um{spec.version}"

        # Override those environment variables where any other string variant is specified.
        for var in self._sources_variants + self._other_variants:
            spec_value = spec.variants[var].value
            if spec_value != "none":
                check_model_vs_spec(model, config_env, var, spec_value)
                config_env[var] = spec_value

        # Define CPATH and FPATH for dependencies that need include files or modules.
        for path in ["CPATH", "FPATH"]:
            env.prepend_path(path, spec["gcom"].prefix.include)
            for var in self._bool_variants:
                if config_env[var] == "true":
                    prefix = spec[self._lib_cfg[var]["dep_name"]].prefix
                    for include in self._lib_cfg[var]["includes"]:
                        env.prepend_path(path, prefix.join(include))
            tty.info(f"{path}={[p.value for p in env.group_by_name()[path]]}")

        # The gcom library does not contain shared objects and
        # therefore must be statically linked.
        env.prepend_path("LIBRARY_PATH", spec["gcom"].prefix.lib)

        # Get the linker arguments for some dependencies.
        for var in self._bool_variants:
            if config_env[var] == "true":
                fcm_name = self._lib_cfg[var]["fcm_name"]
                linker_args = self._get_linker_args(spec, var)
                config_env[f"ldflags_{fcm_name}_on"] = linker_args

        # The project_cfg is relevant for models that use Github URLs.
        if model in self.github_models:
            # Add sources to the environment
            for project in self.projects_needed:
                project_cfg = self._project_cfg[project]
                location_var = project_cfg["location_var"]
                sources_var = project_cfg["sources_var"]
                if project == "um":
                    # Check and update config_root_path if necessary.
                    # Output appropriate warning messages.
                    project_path = self._project_path(project)
                    check_model_vs_root_path_vs_um_ref(
                        model,
                        config_env,
                        project_path)
                    # Set the config_env variables to the required values.
                    config_env["config_root_path"] = project_path
                    config_env["config_revision"] = ""

                # Output appropriate warning messages if overriding existing env.
                check_model_vs_project(
                    model,
                    config_env,
                    project_cfg)
                config_env[location_var] = ""
                config_env[sources_var] = ""
        else:
            # The model uses Subversion and ignores ref variants.
            for project in self._projects:
                ref_var = self._project_cfg[project]["ref_var"]
                ref_value = spec.variants[ref_var].value
                if ref_value != "none":
                    tty.warn(
                        f"The {model} model ignores the variant "
                        f"{ref_var}={ref_value}.")

        # Set environment variables based on config_env.
        for key in config_env:
            tty.info(f"{key}={config_env[key]}")
            env.set(key, config_env[key])

        # Add the location of the FCM executable to PATH.
        env.prepend_path("PATH", spec["fcm"].prefix.bin)


    def build_dir(self):
        """
        Return the build directory.
        """
        return join_path(self.stage.source_path, "..", "spack-build")


    def patch(self):
        """
        Patch the staging directory just before building.
        """

        # This patch is relevant for models that use Github URLs (Phase 2).
        spec = self.spec
        model = spec.variants["model"].value
        if model in self.github_models:
            # Checkout sources from Github
            for project in self.projects_needed:
                self._dynamic_resource(project)


    def build(self, spec, prefix):
        """
        Use FCM to build the executables.
        """
        original_config = join_path(self.package_dir, "fcm-make.cfg")
        build_dir = self.build_dir()
        mkdirp(build_dir)

        model = spec.variants["model"].value
        if model in self.github_models:
            # Create a dynamic wrapper config to override the extract.location
            # (e.g. extract.location[um] = $um_base@$um_rev) with
            # the project path.
            dynamic_config = join_path(build_dir, "fcm-make-dynamic.cfg")
            with open(dynamic_config, "w") as f:
                f.write(f"include = {original_config}\n")
                for project in self.projects_needed:
                    # Set the extract location to the project path.
                    project_path = self._project_path(project)
                    f.write(f"extract.location[{project}] = {project_path}\n")
            config_file = dynamic_config
        else:
            config_file = original_config

        fcm = which("fcm")
        fcm("make",
            "--new",
            f"--config-file={config_file}",
            f"--directory={build_dir}",
            "--jobs=4")


    def _dynamic_resource(self, project):
        """
        Check out resource dynamically based on a branch/tag/commit.

        Parameters
        ----------
        project : str
            Project name (e.g. 'jules').
        """
        project_cfg = self._project_cfg[project]
        url = project_cfg["url"]
        ref = self._project_ref(project)
        dst_dir = self._project_path(project)

        # Create the destination directory
        mkdirp(dst_dir)

        git = spack.util.git.git()

        # Attempt to check out branch to dir
        try:
            tty.msg(f"Attempting to checkout branch {ref}")
            git("clone", "--depth", "1", "--branch", ref, url, dst_dir)
        except ProcessError:
            tty.warn(f"ref '{ref}' may be a commit/tag, retrying.")
            git("clone", url, dst_dir)
            with working_dir(dst_dir):
                git("checkout", ref)

        tty.msg(f"{ref} checked out from {url} to {dst_dir}")
