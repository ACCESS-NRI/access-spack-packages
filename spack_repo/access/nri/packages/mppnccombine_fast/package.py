# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright 2025 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class MppnccombineFast(CMakePackage):
    """mppnccombine-fast is a fast version of mppnccombine, a tool for combining
    multiple netCDF files into a single file. It is designed to be used with
    large datasets and provides significant performance improvements over the
    standard mppnccombine."""

    homepage = "https://github.com/coecms/mppnccombine-fast"
    git = "https://github.com/ACCESS-NRI/mppnccombine-fast.git"
    url = "https://github.com/ACCESS-NRI/mppnccombine-fast/archive/refs/tags/2025.07.000.tar.gz"
    maintainers("dougiesquire")

    license("Apache-2.0", checked_by="dougiesquire")

    version("2025.07.000", sha256="d74ef9b47aa6a6aac2d2f802f146b59d585104a780b65571fe7fda78e69af553")

    depends_on("c", type="build")
    depends_on("cxx", type="build")

    depends_on("cmake@3.10:", type="build")
    depends_on("mpi")
    depends_on("hdf5")
    depends_on("netcdf-c")
