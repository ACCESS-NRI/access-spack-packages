# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.access.nri.build_systems.um_base import UmBasePackage
from spack.package import *

class Um(UmBasePackage):
    """
    UM is a numerical weather prediction and climate modelling software package.
    """

    variant("model", default="vn13", description="Model configuration.",
        values=("vn13", "vn13p0-rns", "vn13p1-am", "vn13p5-rns"), multi=False)

    _github_models = ("vn13", "vn13p1-am")

    # Include openmpi directly https://github.com/ACCESS-NRI/spack-packages/issues/293
    variant("mpi", default=True, description="Build with MPI")
    depends_on("mpi", when="+mpi", type=("build", "link", "run"))

    def setup_run_environment(self, env):
        """
        Set the built path into the environment.
        """
        # Add the built executables to the path
        env.prepend_path("PATH", join_path(self.prefix, "build-atmos", "bin"))
        env.prepend_path("PATH", join_path(self.prefix, "build-recon", "bin"))


    def install(self, spec, prefix):
        """
        Install executables and accompanying files into the prefix directory,
        according to the directory structure of EXEC_DIR, as described in (e.g.)
        https://code.metoffice.gov.uk/trac/roses-u/browser/b/y/3/9/5/trunk/meta/rose-meta.conf
        """
        for um_exe in ["atmos", "recon"]:
            bin_dir = join_path(f"build-{um_exe}", "bin")
            build_bin_dir = join_path(self._build_dir(), bin_dir)
            install_bin_dir = join_path(prefix, bin_dir)
            mkdirp(install_bin_dir)
            install_tree(build_bin_dir, install_bin_dir)
