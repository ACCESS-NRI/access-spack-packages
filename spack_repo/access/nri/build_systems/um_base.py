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

    # Top level variant that decides how the package should build
    variant(
        "MOSRS_build",
        default=False,
        description="Retrieve the FCM build config from MOSRS."
        )

    homepage = "https://code.metoffice.gov.uk/trac/um"
    git = "https://github.com/ACCESS-NRI/UM"
    _svn = "file:///g/data/ki32/mosrs/um/main/trunk"

    # Set up the versions- the version setup will differ depending on whether
    # we get the build from MOSRS or Github. We only configure spack versions 
    # for the versions of the UM we have tested. Other versions are still
    # retrievable by explicitly setting the _ref or _rev variants.
    version("13.1", git=git, tag="UKMO_vn13.1", commit="90088a4acfc99091f5a837de16341afb21855a76")
    version("13.5", git=git, tag="UKMO_vn13.5", commit="e2ba73bd64c31f0fa986a1ede4f96802d14e22a9")
    version("13.8", git=git, tag="UKMO_vn13.8", commit="eeb15ab24ee6f76a9316b083dd7f85109518a16a", preferred=True)

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

    maintainers("penguian")

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
        # The _rev variants specify components to retrieve from the MOSRS
        # SVN repository
        variant(
            f"{component}_rev",
            default="none",
            sticky=True,
            values=str,
            description=f"SVN revision to use for {component}."
            )

        # The _sources variants specify changesets to add from MOSRS
        variant(
            f"{component}_sources",
            multi=True,
            default="none",
            sticky=True,
            values=str,
            description=f"Additional changesets to retrieve for {component}."
            )

        # The _ref variants specify components to retrieve from Github
        variant(
            f"{component}_ref",
            default="none",
            sticky=True,
            values=str,
            description=f"Github ref to use for {component}."
            )

    # Set up a few variants that decide what is built. In the original
    # rose-app.conf files, these all follow the same template of
    # compile_<name>=preprocess-<name> build-<name>, so we'll make
    # compile_<name> the variant which maps to desired name when setting the
    # build environment.
    variant(
        "compile_atmos",
        default=True,
        sticky=True,
        description="Preprocess and compile atmosphere executable."
        )

    variant(
        "compile_recon",
        default=True,
        sticky=True,
        description="Preprocess and compile atmosphere executable."
        )

    variant(
        "compile_createbc",
        default=False,
        sticky=True,
        description="Preprocess and compile createbc executable."
        )

    variant(
        "compile_scm",
        default=False,
        sticky=True,
        description="Preprocess and compile single-column model executable."
        )

    # Now just take a subset of the other build options available in the
    # rose-app.conf and set them meaningfully, based off the previously defined
    # base rose-app.conf (i.e. vn13).
    variant(
        "platform_config_dir",
        default="nci-x86-ifort",
        values=str,
        description="Which FCM build configuration to use."
        )

    variant(
        "optimisation_level",
        default="safe",
        values=("safe", "debug", "rigorous", "high"),
        description="Base optimisation level to apply."
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
        
        # We need to run through the variants, and turn them into the values
        # expected by the FCM build.
        if self.spec.satisfies("+MOSRS_build"):
            # If building from MOSRS, use the MOSRS config
            env.set("config_root_path", "fcm:um.xm_tr")
            env.set("config_revision", f"@{self.version}")
        else:
            # If we're using a Github build config, need to override the config
            # root path
            env.set(
                "config_root_path",
                join_path(self.stage.source_path,
                    "resources",
                    "um"
                    )
                )
            env.set("config_revision", "")

        env.set("config_type", "atmos")

        # Now set the library variants
        converter = lambda v: "true" if v else "false"
        for lib in ("DR_HOOK", "eccodes", "netcdf", "cable"):
            as_FCM_value = converter(self.spec.variants[lib].value)
            env.set(lib, as_FCM_value)

            if self.spec.variants[lib].value:
                # Set up CPATH and FPATH for the environment
                for path in ("CPATH", "FPATH"):
                    prefix = self.spec[self._lib_cfg[lib]["dep_name"]].prefix
                    for inc in self._lib_cfg[lib]["includes"]:
                        env.prepend_path(path, prefix.join(inc))

                # Set up the linker args, used by FCM
                dep_name = self._lib_cfg[lib]["dep_name"]
                ld_flags = [
                    self.spec[dep_name].libs.ld_flags,
                    self._lib_cfg[lib]["fcm_ld_flags"]
                    ]
                # The reason for the explicit -rpath is:
                # https://github.com/ACCESS-NRI/access-spack-packages/issues/14#issuecomment-1653651447
                rpaths = ["-Wl,-rpath=" + d for d in self.spec[dep_name].libs.directories]
                env.set(f"ldflags_{lib}_on", " ".join(ld_flags + rpaths))

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

        # Now we handle the components. We need more complex logic here- it's
        # not allowed to specify a _rev and a _ref for the same component, and
        # _sources cannot be mixed with _ref for a component.
        for component in self._components:
            component_rev = self.spec.variants[f"{component}_rev"].value
            component_sources = self.spec.variants[f"{component}_sources"].value
            component_ref = self.spec.variants[f"{component}_ref"].value

            if component_rev != "none" and component_ref != "none":
                # Specified a rev and a ref- this is not allowed
                raise KeyError("""Cannot specify a _rev and a _ref for the same
                    component.""")

            if component_ref != "none" and component_sources[0] != "none":
                # Specified a ref and sources- this is not allowed
                raise KeyError("""Cannot specify a _ref and _sources for the
                    same component- _sources is strictly a SVN/MOSRS 
                    concept.""")

            # Now we can set the revs in the environment- the refs don't need
            # this, as they are retrieved dynamically at patch time.
            if component_rev != "none":
                env.set(f"{component}_rev", component_rev)
            
            # For the sources, we need to make sure they're in the right format
            # which is one source per line
            if component_sources[0] != "none":
                as_FCM_value = "\n".join(component_sources)
                env.set(f"{component}_sources", as_FCM_value)

        # ---- Finish setting up the component information ---- #

        # Now set the executables to compile
        converter = lambda v: f"preprocess-{v} build-{v}"
        for exe in ("atmos", "recon", "createbc", "scm"):
            if self.spec.variants[f"compile_{exe}"].value:
                as_FCM_value = converter(exe)
                env.set(f"compile_{exe}", as_FCM_value)

        # Finally, the last 2 variants can be taken simply as is
        env.set(
            "platform_config_dir",
            self.spec.variants["platform_config_dir"].value
            )
        env.set(
            "optimisation_level",
            self.spec.variants["optimisation_level"].value
            )


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
                dest_dir = join_path(
                    self.stage.source_path,
                    "resources",
                    component
                    )

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
        Use FCM to build the executables.
        """
        orig_config = join_path(self.package_dir, "fcm-make.cfg")
        build_path = self.build_dir()
        mkdirp(build_path)

        # Set up the config for the components, by setting 'extract' locations
        # for the cloned components and diffs for any sources
        copy(orig_config, build_path)
        new_config = join_path(build_path, "fcm-make.cfg")
        with open(new_config, "a") as f:
            for component in self._components:
                if self.spec.variants[f"{component}_ref"].value != "none":
                    f.write(f"extract.location[{component}] = {self._component_path(component)}\n") 
                if self.spec.variants[f"{component}_sources"].value[0] != "none":
                    f.write(f"extract.location{{diff}}[{component}] = {component}_sources")

        fcm = which("fcm")
        fcm(
            "make",
            f"--config-file={new_config}",
            f"--directory={build_path}",
            "--jobs=4"
            )
        

    def _component_path(self, component):
        return join_path(self.stage.source_path, "resources", component)
