# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class AccessRam3(BundlePackage):
    """
    ACCESS-RAM3 bundle containing the UM Package.

    This is used to version the entirety of a released deployment, including
    the package, it's dependencies, and the version of
    spack-packages/spack-config that it is bundled with
    """

    homepage = "https://www.access-nri.org.au"

    git = "https://github.com/ACCESS-NRI/ACCESS-RAM3.git"

    maintainers("harshula", "penguian")

    version("latest")

    depends_on("um")
