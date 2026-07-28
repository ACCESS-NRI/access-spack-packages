# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.bundle import BundlePackage
from spack.package import *

class AccessEsm1p6(BundlePackage):
    """ACCESS-ESM1.6 bundle contains the coupled UM7, CICE4/CICE5 and MOM5
       models.

    ACCESS-ESM1.6 comprises of:

    * The UKMO UM atmospheric model (v7.3), in the same configuration as
      ACCESS1.4, at N96 (1.875×1.25 degree), 38 level resolution
    * The CABLE land surface model with biogeochemistry (CASA-CNP) (CABLE2.4)
    * The GFDL MOM5 ocean model at 1 degree resolution
    * The WOMBATlite ocean BGC model (generic tracer version)
    * The LANL CICE5 sea ice model with UM/ACCESS modifications for coupling
    * The OASIS-MCT coupler
    """

    homepage = "https://www.access-nri.org.au"

    git = "https://github.com/ACCESS-NRI/ACCESS-ESM1.6.git"

    maintainers("dougiesquire", "harshula")

    version("latest")

    variant(
        "cice",
        default="5",
        sticky=True,
        description="(Deprecated) choose the version of the CICE sea-ice model.",
        values=("5"),
        multi=False,
    )
    variant(
        "um",
        default="access-esm1.6",
        sticky=True,
        description="Choose the branch of um7.",
        values=("access-esm1.5", "access-esm1.6"),
        multi=False,
    )

    depends_on("cice5 model=access-esm1.6", type="run")
    depends_on("mom5 model=access-esm1.6", type="run")
    # um7 is in a private repository
    depends_on("um7@2024.10.17", type="run", when="um=access-esm1.5")
    depends_on("um7", type="run", when="um=access-esm1.6")

    # There is no need for install() since there is no code.
