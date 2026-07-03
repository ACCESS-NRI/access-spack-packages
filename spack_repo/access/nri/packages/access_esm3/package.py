# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.bundle import BundlePackage
from spack.package import *


class AccessEsm3(BundlePackage):
    """
    ACCESS-ESM3 bundle containing the ACCESS-EM3 Package.

    This is used to version the entirety of a released deployment, including
    the package, it's dependencies, and the version of
    spack-packages/spack-config that it is bundled with
    """

    homepage = "https://www.access-nri.org.au"

    git = "https://github.com/ACCESS-NRI/ACCESS-ESM3.git"

    maintainers("anton-seaice")

    version("latest")

    depends_on("access3")
