# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.bundle import BundlePackage
from spack.package import *


class AccessOm3(BundlePackage):
    """
    ACCESS-OM3 bundle containing the ACCESS-OM3 Package.

    This is used to version the entirety of a released deployment, including
    the package, it's dependencies, and the version of
    spack-packages/spack-config that it is bundled with
    """

    homepage = "https://www.access-nri.org.au"

    git = "https://github.com/ACCESS-NRI/ACCESS-OM3.git"

    maintainers("harshula")

    version("latest")

    depends_on("access3")
