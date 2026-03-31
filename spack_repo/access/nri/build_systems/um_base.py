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

class UmBasePackage(Package):
    """
    UmBasePackage is the base build system class for numerical weather
    prediction and climate modelling software packages based on
    the UK Met Office and Momentum Partnership Unified Model.
    """

    homepage = "https://code.metoffice.gov.uk/trac/um"
    git = "https://github.com/ACCESS-NRI/um.git"

    # UM versions 13.0 to 13.9 use Git tags.
    version("13.0", tag="UKMO_vn13.0")
    version("13.1", tag="UKMO_vn13.1")
    version("13.2", tag="UKMO_vn13.2")
    version("13.3", tag="UKMO_vn13.3")
    version("13.4", tag="UKMO_vn13.4")
    version("13.5", tag="UKMO_vn13.5")
    version("13.6", tag="UKMO_vn13.6")
    version("13.7", tag="UKMO_vn13.7")
    version("13.8", tag="UKMO_vn13.8", preferred=True)
    version("13.9", tag="UKMO_vn13.9")

    maintainers("penguian")

    _projects = (
        "casim",
        "jules",
        "shumlib",
        "socrates",
        "ukca",
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

    # Configuraion items to use when GitHub sources are needed.
    _project_cfg = {}

    for _project in _projects:
        # Git reference variants.
        _ref_var = f"{_project}_ref"
        variant(_ref_var, default="none", values="*", multi=False,
            description=f"Git branch/tag/commit for {_project}. "
                        f"Defaults to automatic tagging if 'none'.")

        # Configuraion items to use when GitHub sources are needed.
        _project_cfg[_project] = {
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
            if ref_var == "jules_ref":
                # Use a JULES repo tag, e.g. JULES_vn7.8
                # JULES version = UM version - 6.0
                return f"JULES_vn{spec.version[0] - 6}.{spec.version[1]}"
            # Use a CASIM, SHUMLIB, etc. repo tag, e.g. um13.8
            return f"um{spec.version}"
        return ref_value


    def _project_path(self, project):
        """
        Return the absolute path to a resource in the stage directory.
        """
        return join_path(self.stage.path, "resources", project)




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

        # Override those environment variables where any other string variant is specified.
        for var in self._other_variants:
            spec_value = spec.variants[var].value
            if spec_value != "none":
                check_model_vs_spec(model, config_env, var, spec_value)
                config_env[var] = spec_value
        # If config_revision is left unspecified, and the model does not specify it,
        # then leave it empty.
        var = "config_revision"
        if spec.variants[var].value == "none" and (var not in config_env or config_env[var] == ""):
             config_env[var] = ""

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

        # Set environment variables for all GitHub sources.
        # Set config_root_path to self.stage.source_path.
        project_path = self.stage.source_path
        config_env["config_root_path"] = project_path
        config_env["config_revision"] = ""

        # Set location, rev, and sources variables to empty strings.
        for project in ("um",) + self.projects_needed:
            config_env[f"{project}_project_location"] = ""
            config_env[f"{project}_rev"] = ""
            config_env[f"{project}_sources"] = ""

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
        # Checkout other resources from Github
        for project in self.projects_needed:
            self._dynamic_resource(project)


    def build(self, spec, prefix):
        """
        Use FCM to build the executables.
        """
        original_config = join_path(self.package_dir, "fcm-make.cfg")
        build_dir = self.build_dir()
        mkdirp(build_dir)

        # Create a dynamic wrapper config to override the extract.location
        # (e.g. extract.location[um] = $um_base@$um_rev) with
        # the project path.
        dynamic_config = join_path(build_dir, "fcm-make-dynamic.cfg")
        with open(dynamic_config, "w") as f:
            f.write(f"include = {original_config}\n")
            # Set the extract location for 'um' to the contents of self.stage.source_path.
            f.write(f"extract.location[um] = {self.stage.source_path}\n")
            for project in self.projects_needed:
                # Set the extract location to the project path.
                project_path = self._project_path(project)
                f.write(f"extract.location[{project}] = {project_path}\n")
        config_file = dynamic_config

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
