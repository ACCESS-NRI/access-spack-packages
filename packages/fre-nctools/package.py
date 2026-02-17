# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright 2025 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class FreNctools(AutotoolsPackage):
    """FRE-NCtools is a collection of tools for creating grids and mosaics
    commonly used in climate and weather models, the remapping of data among
    grids, and the creation and manipulation of netCDF files. These tools were
    largely written by members of the GFDL Modeling Systems Group primarily for
    use in the Flexible Modeling System (FMS) Runtime Environment (FRE)
    supporting the work of the Geophysical Fluid Dynamics Laboratory (GFDL)."""

    homepage = "https://github.com/NOAA-GFDL/FRE-NCtools"
    git = "https://github.com/ACCESS-NRI/FRE-NCtools.git"
    url = "https://github.com/ACCESS-NRI/FRE-NCtools/archive/refs/tags/2022.02.tar.gz"
    maintainers("dougiesquire")

    license("LGPL-3.0-only")

    # A number of versions are excluded from this spack package due to bugs:
    # - 2024.05.02: see https://github.com/NOAA-GFDL/FRE-NCtools/issues/344
    # - 2024.05.01: see https://github.com/NOAA-GFDL/FRE-NCtools/issues/344
    # - 2024.03: implicit funcion delcaration in mppncscatter.c; fixed in edcdf78
    # - 2024.01: implicit function declaration in make_topog.c; fixed in 6b4d2fb
    # - 2023.01.02: implicit function declaration in make_topog.c; fixed in 6b4d2fb
    # - 2023.01.01: implicit function declaration in make_topog.c; fixed in 6b4d2fb
    # - 2023.01: implicit function declaration in make_topog.c; fixed in 6b4d2fb

    version("2024.05-1", sha256="3cef66c9196211780687e1c58cdc86316e6db221c6f0547ed8b72fdd60697ecb")
    version("2024.05", sha256="61cec52aa03e066b64bed794ef9dc3eb28654c3d1b872aef1b69ce99ef7a9c65")
    version("2024.04", sha256="e27346d7ade1b67af163bb7f327a47a288d5e475fe797323bd7cee3a46385de0")
    version("2024.02", sha256="90d52abc1b467d635dd648185b0046efcc6d58a232143b0ccaf9a0bff23d2f5d")
    version("2022.02", sha256="bd90c9c3becdb19ff408c0915e61141376e81c12651a5c1b054c75ced9a73ad2")

    variant("mpi", default=False, description="Builds with MPI support")

    depends_on("autoconf", type="build")
    depends_on("automake", type="build")
    depends_on("libtool", type="build")
    depends_on("netcdf-c")
    depends_on("netcdf-fortran")
    depends_on("mpi", when="+mpi")
    depends_on("nco", when="@2024.05:")

    def configure_args(self):
        spec = self.spec
        args = []

        # ocean_model_grid_generator subproject removed in 2023.01
        if spec.version <= Version("2022.02"):
            args.append("--disable-ocean-model-grid-generator")

        if "+mpi" in spec:
            args.append("--with-mpi")

        return args
