# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack_repo.builtin.build_systems.bundle import BundlePackage
from spack.package import *


class CoastriRoms(BundlePackage):
    """ROMS is a free-surface, terrain-following,
    primitive equations ocean model widely used by
    the scientific community for a diverse range of applications

    This bundle package used to version the entirety of a released deployment, including
    the package, it's dependencies, and the version of
    spack-packages/spack-config that it is bundled with
    """

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/CoastRI-ROMS.git"

    version("latest")

    depends_on("ancoms-roms")