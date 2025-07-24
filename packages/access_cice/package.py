# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class AccessCice(CMakePackage):
    """CICE is a computationally efficient model for simulating the growth,
    melting, and movement of polar sea ice. CICE is maintained and developed by
    the CICE-Consortium. This package builds using the Access3Share common
    libraries for ACCESS3 models."""

    homepage = "https://github.com/CICE-Consortium/CICE"
    git = "https://github.com/ACCESS-NRI/CICE"
    submodules = True
    maintainers("anton-seaice", "harshula")

    license("BSD-3-Clause", checked_by="anton-seaice")

    version("stable", branch="CICE6.6.1-x", preferred=True)  # need to update branch for new major versions
    version("CICE6.6.1-0", tag="CICE6.6.1-0", commit="6bceb915e232f46a8c84992a3176b98ee0acd8b5")
    version("CICE6.6.0-3", tag="CICE6.6.0-3", commit="2c444bd9d2fad1f1df4d855debc2801d4b23487d")
    version("CICE6.6.0-1", tag="CICE6.6.0-1", commit="964a4455db3127d0c4681e6533f6d9733a5e8255")

    variant("openmp", default=False, description="Enable OpenMP")
    variant(
        "access3",
        default=True,
        description="Install CICE as library for Access3 models"
    )

    variant("io_type", 
        default="NetCDF",
        values=("NetCDF", "PIO", "Binary"),
        description="CICE IO Method"
    )

    variant("driver",
            default="none",
            values=("none", "nuopc/cmeps", "access/cmeps", "standalone/cice"),
            description="CICE driver path"
    )

    depends_on("access3-share", when="+access3") 
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:", when="io_type=NetCDF")
    depends_on("parallelio@2.5.3:", when="io_type=PIO")

    root_cmakelists_dir = "configuration/scripts/cmake"

    def cmake_args(self):
        args = [
            self.define_from_variant("CICE_OPENMP", "openmp"),
            self.define_from_variant("CICE_IO", "io_type"),
            self.define_from_variant("CICE_ACCESS3", "access3"),
        ]

        if self.spec.variants["driver"].value != "none":
            args.append(self.define_from_variant("CICE_DRIVER", "driver"))
        # if driver="none" respect default set through CMake

        return args
