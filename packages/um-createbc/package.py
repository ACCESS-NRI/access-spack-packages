# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import configparser
from spack.package import *
import llnl.util.tty as tty
import spack.util.git
from spack.util.environment import EnvironmentModifications

class UmCreatebc(Package):
    """
    UmCreatebc creates local boundary conditions for the UM weather and climate model.
    """

    homepage = "https://code.metoffice.gov.uk/trac/um"
    svn = "file:///g/data/ki32/mosrs/um/main/trunk"

    # See 'fcm kp fcm:um.xm' for release versions.
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
    version("13.0", revision=_revision["13.0"], preferred=True)
    for v in range(1, 1 + _max_minor):
        _version = f"13.{v}"
        version(_version, revision=_revision[_version])

    maintainers("penguian")

    variant("model", default="vn13", description="Model configuration.",
        values=("vn13", "vn13p5-rns"), multi=False)

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
    # The real default is set by the model.

    # Revision variants.
    _rev_variants = (
        "casim_rev",
        "jules_rev",
        "shumlib_rev",
        "socrates_rev",
        "ukca_rev")

    # Git reference variants.
    _ref_variants = (
        "jules_ref",
        "um_ref")

    # Other string variants.
    _other_variants = (
        "casim_sources",
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
        "shumlib_sources",
        "socrates_sources",
        "stash_version",
        "timer_version",
        "ukca_sources",
        "um_sources"
        )

    _str_variants = _rev_variants + _ref_variants + _other_variants

    for var in _str_variants:
        variant(var, default="none", description=var, values="*", multi=False)

    # The 'site=nci-gadi' variant of fcm defines the keywords
    # used by the FCM configuration of UMCreateBC.
    depends_on("fcm site=nci-gadi", type="build")

    # For GCOM versions, see
    # https://code.metoffice.gov.uk/trac/gcom/wiki/Gcom_meto_installed_versions
    depends_on("gcom~mpi@7.8", when="@:13.0", type=("build", "link"))
    depends_on("gcom~mpi@7.9", when="@13.1", type=("build", "link"))
    depends_on("gcom~mpi@8.0", when="@13.2", type=("build", "link"))
    depends_on("gcom~mpi@8.1", when="@13.3", type=("build", "link"))
    depends_on("gcom~mpi@8.2", when="@13.4", type=("build", "link"))
    depends_on("gcom~mpi@8.3", when="@13.5:13.7", type=("build", "link"))
    depends_on("gcom~mpi@8.4", when="@13.8", type=("build", "link"))
    depends_on("gcom~mpi@8.4:", when="@13.9:", type=("build", "link"))
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

    # Optional Github sources to be used in build (i.e. AM3)
    _resource_cfg = {
        "jules_ref": {
            "sources_var": "jules_sources",
            "git_url": "https://github.com/ACCESS-NRI/JULES.git",
            "subdir": "jules"},
        "um_ref": {
            "sources_var": "um_sources",
            "git_url": "https://github.com/ACCESS-NRI/UM.git",
            "subdir": "um"}}


    def _config_file_path(self, model):
        """
        Return the pathname of the Rose app config file
        corresponding to model.
        """
        return join_path(
            self.package_dir, "model", model, "rose-app.conf")


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
        # https://github.com/ACCESS-NRI/spack-packages/issues/14#issuecomment-1653651447
        rpaths = ["-Wl,-rpath=" + d for d in spec[dep_name].libs.directories]

        # Both ld_flags and rpaths are lists of strings.
        return " ".join(ld_flags + rpaths)


    def setup_run_environment(self, env):
        """
        Set the built path into the environment.
        """
        # Add the built executables to the path
        env.prepend_path("PATH", self.prefix.bin)


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


        def check_model_vs_sources_vs_ref(
            model,
            config_env,
            sources_var,
            ref_var,
            resource_path):
            """
            Check the values set by the variants sources_var and ref_var
            against any existing sources value in config_env, and remind
            that the sources value will be overridden by resource_path.
            """
            sources_value = spec.variants[sources_var].value
            ref_value = spec.variants[ref_var].value
            tty.info(f"The spec sets {ref_var}={ref_value}")
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
                f"The value {resource_path} will be used for {sources_var}.")


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
        config_env = dict()
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
        for var in self._other_variants:
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

        # The _resource_cfg is relevant only for models that use Github URLs.
        # Only one model so far, but this may change in future.
        if model == "vn13p1-am":
            # Get the root to the resources
            resources_root = join_path(self.stage.source_path, "resources")
            # Add sources to the environment if requested
            for ref_var in self._resource_cfg:
                ref_value = spec.variants[ref_var].value
                if ref_value != "none":
                    sources_var = self._resource_cfg[ref_var]["sources_var"]
                    subdir = self._resource_cfg[ref_var]["subdir"]
                    resource_path = join_path(resources_root, subdir)
                    # Output appropriate warning messages.
                    check_model_vs_sources_vs_ref(
                        model,
                        config_env,
                        sources_var,
                        ref_var,
                        resource_path)
                    config_env[sources_var] = resource_path
        else:
            # The model does not use Github URLs and ignores the ref variants.
            for ref_var in self._resource_cfg:
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


    def _build_dir(self):
        """
        Return the build directory.
        """
        return join_path(self.stage.source_path, "..", "spack-build")


    def patch(self):
        """
        Patch the staging directory just before building.
        """

        # This patch is relevant only for models that use Github URLs.
        # Only one model so far, but this may change in future.
        spec = self.spec
        model = spec.variants["model"].value
        if model == "vn13p1-am":
            # Get the root to the resources
            resources_root = join_path(self.stage.source_path, "resources")

            # Optional sources (i.e. AM3)
            for ref_var in self._resource_cfg:
                ref_value = spec.variants[ref_var].value
                if ref_value != "none":
                    git_url = self._resource_cfg[ref_var]["git_url"]
                    subdir = self._resource_cfg[ref_var]["subdir"]
                    resource_path = join_path(resources_root, subdir)
                    self._dynamic_resource(
                        url=git_url,
                        ref=ref_value,
                        dst_dir=resource_path)


    def build(self, spec, prefix):
        """
        Use FCM to build the executables.
        """
        build_dir = self._build_dir()
        mkdirp(build_dir)
        fcm = which("fcm")
        config_file = join_path(
            self.package_dir,
            "fcm-make.cfg")
        fcm("make",
            "-vv",
            "--new",
            f"--config-file={config_file}",
            f"--directory={build_dir}",
            "--jobs=4")


    def install(self, spec, prefix):
        """
        Install executables and accompanying files into the prefix directory.
        """
        build_bin_dir = join_path(self._build_dir(), "build-createbc", "bin")
        install_bin_dir = prefix.bin
        mkdirp(install_bin_dir)
        install_tree(build_bin_dir, install_bin_dir)


    def _dynamic_resource(self, url, ref, dst_dir):
        """
        Check out resource dynamically based on a branch/tag/commit.

        Parameters
        ----------
        url : str
            Git URL.
        ref : str
            branch, commit or tag
        dst_dir : str
            Checkout path.
        """

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
