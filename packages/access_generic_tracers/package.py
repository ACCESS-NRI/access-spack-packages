# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class AccessGenericTracers(CMakePackage):
    """This is a fork of the NOAA-GFDL/ocean_BGC repo managed by NOAA-GFDL.
    It contains a collection of tracers and associated code for use with
    the MOM and GOLD ocean models. This fork includes generic tracer
    implementations of the suite of WOMBAT models used in ACCESS earth-system
    models."""

    homepage = "https://github.com/ACCESS-NRI/GFDL-generic-tracers"
    git = "https://github.com/ACCESS-NRI/GFDL-generic-tracers.git"

    maintainers("harshula", "dougiesquire")

    # TODO: Delete the "main" version once it is no longer being used anywhere.
    version("main", branch="main")
    version("stable", branch="main", preferred=True)
    version("2025.09.000", tag="2025.09.000", commit="8454a9f569782fd7bb5efbaf8b993cf6f14de2de")
    version("2025.08.000", tag="2025.08.000", commit="cdec99a0d8a8d26dca01ccd93ed47e96829b9cd4")
    version("2025.07.002", tag="2025.07.002", commit="799b95697d0a874120de6d812f03091d60fd7485")
    version("2025.07.001", tag="2025.07.001", commit="20faef70cdf2d8b508825d57bfd981cdd78921c1")
    version("2025.07.000", tag="2025.07.000", commit="5ba87f81fac49314e15ff895f329d94cf2f99de0")
    version("2025.04.001", tag="2025.04.001", commit="2b461ad2cae882c1fc9df8f73c4f5bb12ef3aeac")
    version("2024.08.001", tag="2024.08.001", commit="c17138303f8c6a206a89593eed5b16bdf7af174b")

    variant(
        "shared",
        default=False,
        description="Build shared/dynamic libraries"
    )
    # NOTE: access-fms@mom5 should be used in OM2, ESM1.5 and ESM1.6 to preserve
    # answers with previous releases
    variant(
        "use_access_fms",
        default=True,
        description="If True, depend on access-fms, otherwise depend on fms"
    )

    depends_on("mpi")
    depends_on("access-mocsy@2025.07.001:")  # >= 2025.07.001 for CMake BS with "mocsy" target name
    # TODO: Make conditional once Spack v0.23 or newer is used. The newer
    #       versions contain an fms SPR with variant shared.
    depends_on("fms@2025.02:", when="~use_access_fms")
    with when("+shared"):
        depends_on("access-mocsy+shared")
        depends_on("access-fms+shared", when="+use_access_fms")
    with when("~shared"):
        depends_on("access-mocsy")
        depends_on("access-fms", when="+use_access_fms")

    # TODO: We should try to remove this. The responsibility for including
    #       internal library dependencies for linking purposes should
    #       be in the source package's build system.
    @property
    def libs(self):
        libraries = find_libraries(
            "libgtracers",
            root=self.prefix,
            shared=self.spec.variants.get("shared"),
            recursive=True
        )
        # mocsy is an internal lib dependency of this static library.
        # Hence we need to propagate it.
        return libraries + self.spec["access-mocsy"].libs

    def cmake_args(self):
        return [self.define_from_variant("BUILD_SHARED_LIBS", "shared")]
