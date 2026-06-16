# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.version.version_types import GitVersion, StandardVersion
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class Mom5(CMakePackage):
    """MOM is a numerical ocean model based on the hydrostatic primitive equations."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/mom5.git"

    maintainers("dougiesquire", "harshula")

    # https://github.com/ACCESS-NRI/MOM5#LGPL-3.0-1-ov-file
    license("LGPL-3.0-only", checked_by="dougiesquire")

    version("mom_solo", branch="master")
    version("mom_sis", branch="master")
    version("access-om2", branch="master", preferred=True)
    version("legacy-access-om2-bgc", branch="master")
    version("access-esm1.5", branch="access-esm1.5")
    version("access-esm1.6", branch="master")

    depends_on("c", type="build")
    depends_on("fortran", type="build")
    depends_on("cmake@3.18:", type="build")

    # NOTE: @mom matches both mom_solo and mom_sis
    build_system(
        conditional("cmake", when="@mom,access-om2,legacy-access-om2-bgc,access-esm1.6"),
        default="cmake",
    )

    with when("@mom,access-om2,legacy-access-om2-bgc,access-esm1.6"):
        depends_on("netcdf-c@4.7.4:")
        depends_on("netcdf-fortran@4.5.2:")
        # Depend on virtual package "mpi".
        depends_on("mpi")

    with when("@access-om2,legacy-access-om2-bgc"):
        depends_on("datetime-fortran")
        depends_on("libaccessom2+deterministic", when="+deterministic")
        depends_on("libaccessom2~deterministic", when="~deterministic")

    with when("@access-om2,legacy-access-om2-bgc,access-esm1.6"):
        depends_on("oasis3-mct+deterministic", when="+deterministic")
        depends_on("oasis3-mct~deterministic", when="~deterministic")

    # NOTE: Spack will also match "access-om2-legacy-bgc" here, that's why
    #       it has been renamed to "legacy-access-om2-bgc".
    with when("@access-om2,access-esm1.6"):
        depends_on("access-fms")
        depends_on("access-generic-tracers")

    # legacy-access-om2-bgc builds with access-generic-tracers but it
    # is not configured for use in ACCESS-OM2-BGC configurations.
    with when("@legacy-access-om2-bgc"):
        depends_on("access-fms")
        depends_on("access-generic-tracers")

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

    with when("@access-esm1.5"):
        depends_on("netcdf-c@4.7.1:")
        depends_on("netcdf-fortran@4.5.1:")
        depends_on("openmpi")
        depends_on("oasis3-mct@access-esm1.5")

    root_cmakelists_dir = "cmake/"

    phases = ("setup", "cmake", "build", "install")

    # NOTE: The keys in the __builds variable are required to check whether
    #       a valid version was passed in by the user.
    __builds = {
        "mom_solo": "MOM5_SOLO",
        "mom_sis": "MOM5_SIS",
        "access-om2": "MOM5_ACCESS_OM",
        "access-esm1.6": "MOM5_ACCESS_ESM",
        "legacy-access-om2-bgc": "MOM5_ACCESS_OM_BGC"
    }
    __version = "INVALID"

    # NOTE: This functionality will hopefully be implemented in the Spack core
    #       in the future. Till then, this approach can be used in other SPRs
    #       where this functionality is required.
    def setup(self, spec, prefix):
        if isinstance(spec.version, GitVersion):
            self.__version = spec.version.ref_version.string
        elif isinstance(spec.version, StandardVersion):
            self.__version = spec.version.string
        else:
            raise ValueError("version=" + spec.version.string)

        # The rest of the checks are only required if a __builds member
        # variable exists
        if self.__version not in self.__builds.keys():
            raise ValueError(
                f"CMakeBuilder doesn't support version {self.__version}. The version must "
                "be selected from: " + ", ".join(self.__builds.keys())
            )

        print("INFO: version=" + self.__version +
                " type=" + self.__builds[self.__version])

    def cmake_args(self):
        args = [
            self.define("MOM5_TYPE", self.__builds[self.__version]),
            self.define_from_variant("MOM5_DETERMINISTIC", "deterministic"),
        ]
        return args
