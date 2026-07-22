# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on gcom/package.py by scottwales 2023
# and https://github.com/coecms/access-esm-build-gadi/blob/master/Makefile
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.generic import Package
from spack.package import *


class Gcom4(Package):
    """
    GCOM is a wrapper around multiprocessing libraries such as MPI
    Gcom4 is a package for older versions of GCOM as used by UM vn7.3 in ACCESS ESM 1.5
    """

    homepage = "https://code.metoffice.gov.uk/trac/gcom"
    git = "https://github.com/ACCESS-NRI/GCOM4.git"

    maintainers("penguian")

    version("stable", branch="access-esm1.6", preferred=True)
    version(
        "2025.08.000",
        tag="2025.08.000",
        commit="d401980e663267be2a039dbb06bf684e2641ee3d"
    )
    version(
        "2024.05.28",
        tag="2024.05.28",
        commit="e123dea738209ab10e194a10e2f19017aac2b032"
    )
    version(
        "2024.05.22",
        tag="2024.05.22",
        commit="1ff765f12ff2413b85bdc18a4bdecd152cfcf1f1"
    )
    version(
        "2024.05.21",
        tag="2024.05.21",
        commit="5c50f725145636862f9e82854244c25bd1d5fe9a"
    )

    variant("mpi", default=True, sticky=True, description="Build with MPI")

    conflicts(
        "@access-esm1.5",
        msg="access-esm1.5 is only available in access-spack-packages versions older than 2026.08.000."
    )
    conflicts(
        "%gcc",
        when="@:2025.08.000",
        msg="gcom4 version 2025.08.000 and older cannot be compiled with gcc."
    )

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    depends_on("fcm", type="build")
    depends_on("mpi", when="+mpi")

    def gcom_machine(self, spec):
        """
        Determine the machine configuration name
        """
        if spec.satisfies("%intel"):
            mach_c = "ifort"
        elif spec.satisfies("%oneapi"):
            mach_c = "oneapi"
        # https://github.com/ACCESS-NRI/access-spack-packages/issues/85
        # versions 4.7 and 4.8 support the gcc Fortran compiler,
        # but versions 4.5 and 4.6 do not.
        elif spec.satisfies("%gcc"):
            mach_c = "gfortran"
        else:
            raise NotImplementedError("Unknown compiler")
        if "+mpi" in spec:
            mach_m = "openmpi"
        else:
            mach_m = "serial"
        return f"nci_{mach_c}_{mach_m}"


    def patch(self):
        """
        Perform the equivalent of the following sed commands:
        sed -i '/build.target{ns}/d' $@/fcm-make/gcom.cfg
        sed -i 's/-openmp/-qopenmp/g' $@/fcm-make/machines/nci_ifort_openmpi.cfg
        sed -i 's/-openmp/-qopenmp/g' $@/fcm-make/machines/nci_ifort_serial.cfg
        """
        filter_file(
            r"build\.target\{ns\}.*", "#",
            join_path("fcm-make", "gcom.cfg"))
        # MS: The oneAPI config already uses the `-qopenmp` flag, so a
        # substitution is not required for oneAPI.
        if self.spec.satisfies("%intel"):
            machine = self.gcom_machine(self.spec)
            filter_file(
                r"-openmp", "-qopenmp",
                    join_path("fcm-make", "machines", f"{machine}.cfg"))


    def build(self, spec, prefix):
        """
        Build the library.
        """
        fcm = which("fcm")
        if fcm is None:
            raise FileNotFoundError("fcm not found in $PATH")

        # Set up variables used by fcm-make/gcom.cfg
        env["ACTION"] = "preprocess build"
        env["DATE"] = ""
        env["GCOM_SOURCE"] = "$HERE/.."
        env["MIRROR"] = ""
        env["REMOTE_ACTION"] = ""
        env["ROSE_TASK_MIRROR_TARGET"] = "localhost"

        # Decide on the build variant
        env["GCOM_MACHINE"] = self.gcom_machine(spec)

        # Do the build with fcm
        fcm("make", "-f", join_path("fcm-make", "gcom.cfg"))


    def install(self, spec, prefix):
        """
        Build and install the library.
        """
        self.build(spec, prefix)
        mkdirp(prefix.lib)
        install(
            join_path("build", "lib", "libgcom.a"),
            join_path(prefix.lib, "libgcom.a"))
        install_tree(join_path("build", "include"), prefix.include)
