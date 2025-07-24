# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright 2025 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class AccessIssm(BundlePackage):
    """
    ACCESS-ISSM bundle containing the issm Package.

    This is used to version the entirety of a released deployment, including
    the package, it's dependencies, and the version of
    spack-packages/spack-config that it is bundled with
    """

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/ACCESS-ISSM.git"

    maintainers("harshula", "justinh2002")

    version("latest")

    depends_on("issm")
