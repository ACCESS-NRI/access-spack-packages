# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *

class AccessWw3(CMakePackage):
    """WAVEWATCH III® is a community wave modeling framework that includes the
    latest scientific advancements in the field of wind-wave modeling and
    dynamics. This package builds using the Access3Share common libraries for
    ACCESS3 models."""

    homepage = "https://github.com/noaa-emc/ww3/"
    git = "https://github.com/ACCESS-NRI/WW3"
    maintainers("anton-seaice", "harshula")
    license("LGPL-3.0-only", checked_by="anton-seaice")

    version("stable", branch="dev/2025.08", preferred=True)   # need to update branch for new major versions
    version("2025.08.000", tag="2025.08.000", commit="5ccdad475003c711ccb660039847759cc952519f")
    version("2025.03.0", tag="2025.03.0", commit="d980dececb8843da1769470f24bc633982073db6")

    variant("openmp", default=False, description="Enable OpenMP")
    variant(
        "access3",
        default=True,
        description="Install WW3 as library for Access3 models"
    )

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    depends_on("access3-share", when="+access3")
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")

    def cmake_args(self):
        args = [
            self.define_from_variant("WW3_OPENMP", "openmp"),
            self.define_from_variant("WW3_ACCESS3", "access3"),
        ]

        return args