# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class AccessMocsy(CMakePackage):
    """Routines to model ocean carbonate system thermodynamics. ACCESS NRI's fork."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/mocsy.git"

    maintainers("dougiesquire", "harshula")

    # https://github.com/ACCESS-NRI/mocsy/blob/master/LICENSE
    license("MIT", checked_by="dougiesquire")

    version("stable", branch="gtracers", preferred=True)
    version("2025.07.002", tag="2025.07.002", commit="bfbf7f87244bb42db53cd304ddfead567e990312")
    version("2025.07.001", tag="2025.07.001", commit="156b3c8f50562e20882c686988022e3ef19f8526")
    version("2025.07.000", tag="2025.07.000", commit="1e4bc055519a6446232dcff803e7b80e56c49424")

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    depends_on("cmake@3.22:", type="build")
    depends_on("mpi")

    variant(
        "shared",
        default=False,
        sticky=True,
        description="Build shared/dynamic libraries",
        when="@2025.07.002:",
    )
    variant(
        "build_type",
        default="RelWithDebInfo",
        sticky=True,
        description="CMake build type",
        values=("Debug", "Release", "RelWithDebInfo", "MinSizeRel"),
    )
    variant(
        "precision",
        default="2",
        sticky=True,
        description="Precision to use (1 or 2)",
        values=("1", "2"),
    )

    def cmake_args(self):
        args = [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define_from_variant("MOCSY_PRECISION", "precision"),
        ]
        return args
