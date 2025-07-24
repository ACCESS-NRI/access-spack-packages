# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class AccessOm2Bgc(BundlePackage):
    """ACCESS-OM2-BGC bundle contains the coupled CICE5 and MOM5 (BGC variant) models."""

    homepage = "https://www.access-nri.org.au"

    git = "https://github.com/ACCESS-NRI/ACCESS-OM2-BGC.git"

    maintainers("harshula")

    version("latest")

    variant("deterministic", default=False, description="Deterministic build.")

    depends_on("libaccessom2+deterministic", when="+deterministic", type="run")
    depends_on("libaccessom2~deterministic", when="~deterministic", type="run")
    depends_on("cice5+deterministic", when="+deterministic", type="run")
    depends_on("cice5~deterministic", when="~deterministic", type="run")
    depends_on(
        "mom5@legacy-access-om2-bgc+deterministic",
        when="+deterministic",
        type="run"
    )
    depends_on(
        "mom5@legacy-access-om2-bgc~deterministic",
        when="~deterministic",
        type="run"
    )

    # There is no need for install() since there is no code.
