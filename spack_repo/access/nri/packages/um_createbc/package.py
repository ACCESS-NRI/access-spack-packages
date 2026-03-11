# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.access.nri.build_systems.um_base import UmBasePackage
from spack.package import *

class UmCreatebc(UmBasePackage):
    """
    UmCreatebc creates local boundary conditions for the UM weather and climate model.
    """

    variant("model", default="vn13", description="Model configuration.",
        values=("vn13", "vn13p5-rns"), multi=False)

    _github_models = ("vn13",)

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
        build_bin_dir = join_path(self._build_dir(), "build-createbc", "bin")
        install_bin_dir = prefix.bin
        mkdirp(install_bin_dir)
        install_tree(build_bin_dir, install_bin_dir)
