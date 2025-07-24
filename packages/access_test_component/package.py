# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# Based on spack/var/spack/repos/builtin/packages/fiat/package.py

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class AccessTestComponent(CMakePackage):
    """ACCESS Test Component is a small test FORTRAN model component
       used to test CI workflows."""

    githubrepo = "ACCESS-NRI/access-test-component"

    homepage = f"https://github.com/{githubrepo}"
    git = f"https://github.com/{githubrepo}.git"

    maintainers("aidanheerdegen", "codegat", "harshula")

    license("Apache-2.0")

    version("main", branch="main", no_cache=True)

    variant("mpi", default=True, description="Use MPI")

    depends_on("mpi", when="+mpi")

    root_cmakelists_dir = "stub"

    def url_for_version(self, version):
        return f"https://github.com/{self.githubrepo}/tarball/{version}"
