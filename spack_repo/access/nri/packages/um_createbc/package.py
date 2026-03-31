# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# Copyright 2024-2026 ACCESS-NRI

from spack_repo.access.nri.build_systems.um_base import UmBasePackage
from spack.package import *

class UmCreatebc(UmBasePackage):
    """
    UmCreatebc creates local boundary conditions for the UM weather and climate model.
    """

    variant("model", default="vn13", description="Model configuration.",
        values=("vn13",), multi=False)

    # List of projects to be used by this package.
    # Defined in parent class and overridden here.
    projects_needed = ("shumlib", "um")

    # For GCOM versions, see
    # https://code.metoffice.gov.uk/trac/gcom/wiki/Gcom_meto_installed_versions
    # um_createbc uses the ~mpi variants of gcom exclusively.
    depends_on("gcom~mpi@7.8", when="@:13.0", type=("build", "link"))
    depends_on("gcom~mpi@7.9", when="@13.1", type=("build", "link"))
    depends_on("gcom~mpi@8.0", when="@13.2", type=("build", "link"))
    depends_on("gcom~mpi@8.1", when="@13.3", type=("build", "link"))
    depends_on("gcom~mpi@8.2", when="@13.4", type=("build", "link"))
    depends_on("gcom~mpi@8.3", when="@13.5:13.7", type=("build", "link"))
    depends_on("gcom~mpi@8.4", when="@13.8", type=("build", "link"))
    depends_on("gcom~mpi@8.4:", when="@13.9:", type=("build", "link"))

    def setup_run_environment(self, env):
        """
        Set the built path into the environment.
        """
        # Add the built executables to the path
        env.prepend_path("PATH", self.prefix.bin)


    def install(self, spec, prefix):
        """
        Install executables and accompanying files into the prefix directory.
        """
        build_bin_dir = join_path(self.build_dir(), "build-createbc", "bin")
        mkdirp(prefix.bin)
        install_tree(build_bin_dir, prefix.bin)
