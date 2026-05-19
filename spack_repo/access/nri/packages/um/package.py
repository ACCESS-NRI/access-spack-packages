# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# Copyright 2024-2026 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py

from spack_repo.access.nri.build_systems.um_base import UmBasePackage
from spack.package import *

class Um(UmBasePackage):
    """
    UM is a numerical weather prediction and climate modelling software package.
    """

    # Gets URL from the base package
    variant("model", default="vn13", description="Model configuration.",
        values=("vn13", "vn13p0-rns", "vn13p1-am", "vn13p5-rns"), multi=False)

    # List of model variants that have been migrated to Github sources.
    # Defined in parent class and overridden here.
    github_models = ("vn13", "vn13p1-am")

    # List of projects to be used by this package.
    # Defined in parent class as all projects and left to default here.
    # projects_needed = super().projects_needed

    # For GCOM versions, see
    # https://code.metoffice.gov.uk/trac/gcom/wiki/Gcom_meto_installed_versions
    depends_on("gcom@7.8", when="@:13.0", type=("build", "link"))
    depends_on("gcom@7.9", when="@13.1", type=("build", "link"))
    depends_on("gcom@8.0", when="@13.2", type=("build", "link"))
    depends_on("gcom@8.1", when="@13.3", type=("build", "link"))
    depends_on("gcom@8.2", when="@13.4", type=("build", "link"))
    depends_on("gcom@8.3", when="@13.5:13.7", type=("build", "link"))
    depends_on("gcom@8.4", when="@13.8", type=("build", "link"))
    depends_on("gcom@8.4:", when="@13.9:", type=("build", "link"))

    # Include openmpi directly.
    # https://github.com/ACCESS-NRI/access-spack-packages/issues/293
    variant("mpi", default=True, description="Build with MPI")
    depends_on("mpi", when="+mpi", type=("build", "link", "run"))

    variant("access3", default=False,
        description="Install UM as library for Access3 models")

    with when("+access3"):
        depends_on("esmf@8.7.0:")
        conflicts("~netcdf")

    phases = ["build", "create_pkgconfig", "install"]


    def setup_run_environment(self, env):
        """
        Set the built path into the environment.
        """
        # Add the built executables to the path
        if not self.spec.variants["access3"].value:
            env.prepend_path("PATH", join_path(self.prefix, "build-atmos", "bin"))
        env.prepend_path("PATH", join_path(self.prefix, "build-recon", "bin"))


    def install(self, spec, prefix):
        """
        Install executables and libraries into spack release folder (prefix)
        When ~access3, this package installs um-atmos.exe
        When +access3, the package installs libum-atmos.a
        um-recon.exe is always installed.
        """

        # List of executables to install, always install recon
        um_exe = ["recon"]

        if self.spec.variants["access3"].value:
            # Install library files from build-atmos directory straight into prefix path
            # so it is in the expected CMAKE_PREFIX_PATH for dependents
            for dir_name in ["lib", "include"]:
                dir_path = join_path("build-atmos", dir_name)
                build_dir = join_path(self.build_dir(), dir_path)
                install_dir = join_path(prefix, dir_name)
                mkdirp(install_dir)
                install_tree(build_dir, install_dir)
        else:
            # Install atmos executable
            um_exe.append("atmos")

        # Install executables and accompanying files into the prefix directory,
        # according to the directory structure of EXEC_DIR, as described in (e.g.)
        # https://code.metoffice.gov.uk/trac/roses-u/browser/b/y/3/9/5/trunk/meta/rose-meta.conf
        for exe in um_exe:
            bin_dir = join_path(f"build-{exe}", "bin")
            build_bin_dir = join_path(self.build_dir(), bin_dir)
            install_bin_dir = join_path(prefix, bin_dir)
            mkdirp(install_bin_dir)
            install_tree(build_bin_dir, install_bin_dir)

    def create_pkgconfig(self, spec, prefix):
        """
        If a um-atmos library has been created, make a pkgconfig file for it
        """
        k = "um-atmos"
        libdir = f"{self.build_dir()}/build-atmos/lib"
        lib = f"lib{k}"

        if exists(f"{libdir}/{lib}.a"):

            pkgdir = f"{libdir}/pkgconfig"
            mkdirp(pkgdir)

            # Workaround for https://github.com/spack/spack/issues/50118
            Version = self.spec.version
            if isinstance(Version, StandardVersion):
                version_str = Version.string
            else:
                version_str = "unknown"

            text = f"""\
prefix={prefix}
exec_prefix=${{prefix}}
libdir=${{exec_prefix}}/lib
includedir=${{prefix}}/include

Name: {lib}
Description: UM {version_str} {lib} Library for Fortran
Version: {version_str}
Requires: libgcom
Libs: -L${{libdir}} -l{k}
Cflags: -I${{includedir}}
"""
            pcpath = join_path(pkgdir, f"{lib}.pc")
            with open(pcpath, "w", encoding="utf-8") as pc:
                nchars_written = pc.write(text)

            if nchars_written < len(text):
                raise OSError