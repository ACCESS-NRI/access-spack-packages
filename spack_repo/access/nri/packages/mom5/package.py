# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class Mom5(CMakePackage):
    """MOM is a numerical ocean model based on the hydrostatic primitive equations."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/mom5.git"

    maintainers("dougiesquire", "harshula")

    # https://github.com/ACCESS-NRI/MOM5#LGPL-3.0-1-ov-file
    license("LGPL-3.0-only", checked_by="dougiesquire")

    version("stable", branch="master", preferred=True)
    version(
        "2026.02.001",
        tag="2026.02.001",
        commit="56261d353c3803e075408ed8421e8c7bf1802887"
    )
    version(
        "2026.02.000",
        tag="2026.02.000",
        commit="995fe497e1b91342f465cbed66eaa1336f183ec0"
    )
    version(
        "2025.08.000",
        tag="2025.08.000",
        commit="627a321f7490afc69b4a8e777992bcfb1f58b5ae"
    )
    version(
        "2025.05.000",
        tag="2025.05.000",
        commit="9f575d8532579a0f717002c571e68037e79c7396"
    )

    _types = {
        "mom_solo": "MOM5_SOLO",
        "mom_sis": "MOM5_SIS",
        "access-om2": "MOM5_ACCESS_OM",
        "access-esm1.6": "MOM5_ACCESS_ESM",
        "access-om2-legacy-bgc": "MOM5_ACCESS_OM_BGC"
    }

    variant(
        "model",
        default="access-om2",
        sticky=True,
        description="MOM5 build type",
        values=tuple(_types.keys())
    )
    variant(
        "build_type",
        default="RelWithDebInfo",
        sticky=True,
        description="CMake build type",
        values=("Debug", "Release", "RelWithDebInfo")
    )
    variant(
        "deterministic",
        default=False,
        sticky=True,
        description="Deterministic build"
    )

    depends_on("c", type="build")
    depends_on("fortran", type="build")
    depends_on("cmake@3.18:", type="build")

    # Depend on virtual package "mpi".
    depends_on("mpi")
    depends_on("netcdf-c@4.7.4:")
    depends_on("netcdf-fortran@4.5.2:")

    for _m in ("access-om2", "access-om2-legacy-bgc"):
        with when(f"model={_m}"):
            depends_on("datetime-fortran")
            depends_on("libaccessom2+deterministic", when="+deterministic")
            depends_on("libaccessom2~deterministic", when="~deterministic")

    # access-om2-legacy-bgc builds with access-generic-tracers but it
    # is not configured for use in ACCESS-OM2-BGC configurations.
    for _m in ("access-om2", "access-esm1.6", "access-om2-legacy-bgc"):
        with when(f"model={_m}"):
            depends_on("oasis3-mct+deterministic", when="+deterministic")
            depends_on("oasis3-mct~deterministic", when="~deterministic")
            depends_on("access-fms")
            depends_on("access-generic-tracers")

    for _m in ("access-esm1.5", "legacy-access-om2-bgc") + tuple(_types.keys()):
        conflicts(
            f"@{_m}",
            msg=f"Version @{_m} is only available in access-spack-packages versions older than 2026.08.000. Use variant 'model' instead."
        )

    del _m

    root_cmakelists_dir = "cmake"

    def cmake_args(self):
        args = [
            self.define("MOM5_TYPE", self._types[self.spec.variants["model"].value]),
            self.define_from_variant("MOM5_DETERMINISTIC", "deterministic"),
        ]
        return args
