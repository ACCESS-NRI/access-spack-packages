# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright 2025 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.bundle import BundlePackage
from spack.package import *


class AccessAm3(BundlePackage):
    """
    ACCESS-AM3 bundle containing the UM Package.
    """

    homepage = "https://www.access-nri.org.au"

    git = "https://github.com/ACCESS-NRI/ACCESS-AM3.git"

    maintainers("bschroeter", "harshula")

    version("latest")

    depends_on("um")
