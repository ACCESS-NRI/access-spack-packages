# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *

# See https://spack.readthedocs.io/en/latest/packaging_guide.html for a guide
# on how this file works.


class Cable(CMakePackage):
    """The CSIRO Atmosphere Biosphere Land Exchange (CABLE) model."""

    homepage = "https://github.com/CABLE-LSM/CABLE"
    git = "https://github.com/CABLE-LSM/CABLE.git"

    maintainers("SeanBryan51", "Whyborn")
    
    license("LicenseRef-CSIRO-Open-Source-Software-License-v1.0", checked_by="anton-seaice")

    version("stable", branch="main", preferred=True)
    version("2025.11.000", tag="2025.11.000", commit="15f639dd33dfb15819304332d72c2b405b51b85e")

    variant(
        "mpi",
        default=True,
        description="Build MPI executable.",
    )

    variant(
        "library",
        default="none",
        values=(
            "none",
            "access-esm1.6"
        ),
        description="Build CABLE science library object.",
    )

    variant(
        "build_type",
        default="Release",
        description="CMake build type",
        values=("Debug", "Release"),
    )

    depends_on("netcdf-fortran@4.5.2:")
    depends_on("mpi", when="+mpi")

    def cmake_args(self):
        args = []
        args.append(self.define_from_variant("CABLE_MPI", "mpi"))
        args.append(self.define("CABLE_LIBRARY", self.spec.variants["library"].value != "none"))
        args.append(self.define_from_variant("CABLE_LIBRARY_TARGET", "library"))
        return args
