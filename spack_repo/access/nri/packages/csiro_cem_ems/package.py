# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.bundle import BundlePackage
from spack.package import *


class CsiroCemEms(BundlePackage):
    """Bundle for the CSIRO Environmental Modelling Suite."""

    homepage = "https://github.com/csiro-coasts/EMS"

    version("latest")

    depends_on("ems")
