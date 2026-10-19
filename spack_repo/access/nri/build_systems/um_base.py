# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# Copyright 2024-2026 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py

import configparser
from spack_repo.builtin.build_systems.generic import Package
from spack.util.executable import ProcessError
from spack.version import ver, GitVersion
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
    git = "https://github.com/ACCESS-NRI/UM"

    # Set up the versions- the version setup will differ depending on whether
    # we get the build from MOSRS or Github. We only configure spack versions 
    # for the versions of the UM we have tested. Other versions are still
    # retrievable by explicitly setting the _ref or _rev variants.
    version("13.1", git=git, tag="UKMO_vn13.1", commit="90088a4acfc99091f5a837de16341afb21855a76")
    version("13.5", git=git, tag="UKMO_vn13.5", commit="e2ba73bd64c31f0fa986a1ede4f96802d14e22a9")
    version("13.8", git=git, tag="UKMO_vn13.8", commit="eeb15ab24ee6f76a9316b083dd7f85109518a16a", preferred=True)

    maintainers("paul-leopardi", "Whyborn")

    # The variants correspond to the meaningful entries in the build
    # rose-app.conf files.

    # Start with the boolean variants, which set library inclusions
    variant("DR_HOOK", default=True, sticky=True, description="DR_HOOK")
    variant("eccodes", default=True, sticky=True, description="eccodes")
    variant("netcdf", default=True, sticky=True, description="netcdf")
    variant("cable", default=False, sticky=True, description="CABLE library")

    # Each of the libraries needs information about how to locate them at
    # build time
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
            "fcm_ld_flags": "-lnetcdff -lnetcdf"},
        "cable": {
            "includes": ["include"],
            "dep_name": "cable",
            "fcm_name": "cable",
            "fcm_ld_flags": ""}}

    # Now set up component variants, which are used to specify where to source
    # components from. Given we need to construct a few variants for each of
    # these components, we'll do it iteratively.
    _components = ("casim", "jules", "shumlib", "socrates", "ukca", "um")
    for component in _components:
        # The _ref variants specify components to retrieve from Github
        variant(
            f"{component}_ref",
            default="none",
            sticky=True,
            values=str,
            description=f"Github ref to use for {component}."
            )

    # Use variants to decide which component to build. The possible components
    # are:
    # "atmos", which builds both um-atmos and um-recon
    # "scm", which builds um-scm (single column model)
    # "createbc", which creates um-createbc
    variant(
        "config_type",
        values=any_combination_of("atmos", "scm", "createbc"),
        sticky=True,
        description="Which UM executables to build."
        )

    variant(
        "optimisation_level",
        default="safe",
        values=("safe", "debug", "rigorous", "high"),
        description="Base optimisation level to apply."
        )

    # Now just take a subset of the other build options available in the
    # rose-app.conf and set them meaningfully, based off the previously defined
    # base rose-app.conf (i.e. vn13).
    variant(
        "platform_config",
        default="nci-x86-ifort",
        values=str,
        description="Which FCM build configuration to use."
        )
    variant(
        "openmp",
        default=True,
        description="Whether to include openmp."
        )

    variant(
        "thread_utils",
        default=True,
        description="Whether to include multi-threading utils."
        )

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    # The 'site=nci-gadi' variant of fcm defines the keywords
    # used by the FCM configuration of UM.
    depends_on("fcm site=nci-gadi", type="build")
    depends_on("fiat@um", type=("build", "link", "run"),
        when="+DR_HOOK")
    depends_on("eccodes +fortran +netcdf", type=("build", "link", "run"),
        when="+eccodes")
    depends_on("netcdf-fortran@4.5.2:", type=("build", "link", "run"),
        when="+netcdf")
    depends_on("cable library='access3'", type=("build", "link", "run"),
        when="+cable")

    phases = ["build", "install"]

    def setup_build_environment(self, env):
        """
        Configure the environment using the specified variants, for the FCM
        build.

        This means setting the environment variable that are expected by the
        FCM build, as well as setting up the environment PATH for linking the
        desired libraries.
        """
        
        # Now set the library env variables based on the variants
        # Unfortunately these are still necessary due to the way FCM picks
        converter = lambda v: "true" if v else "false"
        for lib in ("DR_HOOK", "eccodes", "netcdf", "cable"):
            as_FCM_value = converter(self.spec.variants[lib].value)
            env.set(lib, as_FCM_value)

            if self.spec.satisfies(f"+{lib}"):
                # Set up CPATH and FPATH for the environment
                for path in ("CPATH", "FPATH"):
                    prefix = self.spec[self._lib_cfg[lib]["dep_name"]].prefix
                    for inc in self._lib_cfg[lib]["includes"]:
                        env.prepend_path(path, prefix.join(inc))

                # Set up the linker args, used by FCM
                dep_name = self._lib_cfg[lib]["dep_name"]
                fcm_name = self._lib_cfg[lib]["fcm_name"]
                ld_flags = [
                    self.spec[dep_name].libs.ld_flags,
                    self._lib_cfg[lib]["fcm_ld_flags"]
                    ]
                # The reason for the explicit -rpath is:
                # https://github.com/ACCESS-NRI/access-spack-packages/issues/14#issuecomment-1653651447
                rpaths = ["-Wl,-rpath=" + d for d in self.spec[dep_name].libs.directories]
                env.set(f"ldflags_{fcm_name}_on", " ".join(ld_flags + rpaths))

        # The gcom library does not contain shared objects and
        # therefore must be statically linked.
        env.prepend_path("LIBRARY_PATH", self.spec["gcom"].prefix.lib)

        # And finally locate the FCM binary
        env.prepend_path("PATH", self.spec["fcm"].prefix.bin)

        # ---- Finish setting up the external libraries ---- #

        # Now the interal true/false variants
        converter = lambda v: "true" if v else "false"
        for var in ("openmp", "thread_utils"):
            as_FCM_value = converter(self.spec.variants[var].value)
            env.set(var, as_FCM_value)

    def resource_path(self, component):
        """
        Set the location for the component resource.
        """
        return join_path(self.stage.source_path, "resources", component)

    def patch(self):
        """
        Patch the staging directory, by copying the desired Github components
        into the stage directory as dynamic resources.
        """
        for component in self._components:
            component_ref = self.spec.variants[f"{component}_ref"].value
            if component_ref != "none":
                # The ref is non-empty, so we want it to come from Github
                url = f"https://github.com/ACCESS-NRI/{component}.git"
                dest_dir = self.resource_path(component)

                mkdirp(dest_dir)

                git = spack.util.git.git()

                # Check out the repository at the desired ref
                try:
                    git("clone", "--depth", "1", "--branch", component_ref, url, dest_dir)
                except ProcessError:
                    git("clone", url, dest_dir)
                    with working_dir(dest_dir):
                        git("checkout", component_ref)

    def build_dir(self):
        return join_path(self.stage.source_path, "..", "spack-build")

    def build(self, spec, prefix):
        """
        Use FCM to build the executables. Creates the `fcm-make.cfg`
        dynamically based on the supplied variants.
        """
        build_path = self.build_dir()
        mkdirp(build_path)
        fcm = which("fcm")

        # For each executable we want to build, build the dynamic fcm-make
        # file. The contents of each are going to be effectively the same- an
        # "include" line, which points to the desired machine config to use,
        # and lists of possible _sources and extract locations.

        # In the original fcm-make.cfg file, the include line looks like:
        # include = $conf_path/fcm-make/$platform_config_dir/um-$config_type-$optimisation_level.cfg
        # where the environment variables are interpolated in. It's easier to
        # simply set them directly here.

        # The "include" line is the only one that will change, so build a base
        # config file and append the correct include line for each executable.
        # Even then, the only part of the "include" line that will change is
        # the config type.
        
        conf_path = self.resource_path("um")

        platform = spec.variants["platform_config"].value
        optim = spec.variants["optimisation_level"].value

        # Now build the base config
        base_config = join_path(build_path, "fcm-make.cfg")
        with open(base_config, "w") as f:
            # Set the unchanging bits
            for component in self._components:
                f.write(f"extract.location[{component}] = {self._component_path(component)}\n") 

        # Duplicate the base_config for each config type
        for exe in spec.variants["config_type"].value:
            exe_config = join_path(build_path, f"fcm-make-{exe}.cfg")
            copy(base_config, exe_config)
            # We open in read+write mode, as we want to insert the "include"
            # line at the top so that following options take precedence
            with open(exe_config, "r+") as f:
                include = f"include={conf_path}/fcm-make/{platform}/um-{exe}-{optim}.cfg\n"
                orig_contents = f.read()
                f.seek(0)
                f.write(include + orig_contents)

            fcm(
                "make",
                f"--config-file={exe_config}",
                f"--directory={build_path}",
                "--jobs=4"
                )
        
    def _component_path(self, component):
        return join_path(self.stage.source_path, "resources", component)
