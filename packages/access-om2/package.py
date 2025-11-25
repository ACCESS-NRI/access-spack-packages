# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class AccessOm2(BundlePackage):
    """ACCESS-OM2 bundle contains the coupled CICE5 and MOM5 models."""

    homepage = "https://www.access-nri.org.au"

    git = "https://github.com/ACCESS-NRI/ACCESS-OM2.git"

    maintainers("harshula")

    version("latest")

    variant("deterministic", default=False, description="Deterministic build.")

    depends_on("libaccessom2+deterministic", when="+deterministic", type="run")
    depends_on("libaccessom2~deterministic", when="~deterministic", type="run")
    depends_on("cice5+deterministic model=access-om2 build_system=makefile", when="+deterministic", type="run")
    depends_on("cice5~deterministic model=access-om2", when="~deterministic", type="run")
    depends_on("mom5+deterministic", when="+deterministic", type="run")
    depends_on("mom5~deterministic", when="~deterministic", type="run")

    # There is no need for install() since there is no code.
