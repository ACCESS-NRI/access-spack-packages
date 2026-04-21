# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# Copyright 2024-2026 ACCESS-NRI

from spack_repo.builtin.build_systems.generic import Package
from spack.package import *


class Gcom(Package):
    """
    GCOM is a wrapper around multiprocessing libraries such as MPI
    """

    homepage = "https://github.com/ACCESS-NRI/gcom"
    git = "https://github.com/ACCESS-NRI/gcom"

    maintainers("scottwales", "paulleopardi")

    version("7.8", tag="vn7.8", commit="65c857cc3201833360ff62b285e49082378dae42")
    version("7.9", tag="vn7.9", commit="6319ae016dcadc192842a06178f3dbd21a8af64f")
    version("8.0", tag="vn8.0", commit="5a122e9e2147c9a7486a00b9588356eb65324af9")
    version("8.1", tag="vn8.1", commit="e061e2787bd643d9a65679f153fb8e3ffd9d3186")
    version("8.2", tag="vn8.2", commit="fd143bb38e21fe03c7150c0754852c80e15df3d4")
    version("8.3", tag="vn8.3", commit="b7b890a181d8e31e4e80b731b9f8ad9a6e1a8bed")
    version("8.4", tag="vn8.4", commit="f4fa92eb4af4f1e4cf9d608b441e3c96f77b6a6d")

    variant("mpi", default=True, description="Build with MPI")

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    depends_on("fcm", type="build")
    depends_on("mpi", when="+mpi", type=("build", "link", "run"))
    # For the default MPI version for NCI, see (e.g.)
    # https://code.metoffice.gov.uk/trac/gcom/browser/main/trunk/rose-stem/site/nci/suite.rc
    # For cherry picking virtual dependencies, see
    # https://github.com/spack/spack/releases/tag/v0.21.0 Feature 4
    depends_on("openmpi@4.1.3:", when="+mpi^[virtuals=mpi] openmpi", type=("build", "link", "run"))

    def gcom_machine(self, spec):
        """
        Determine the machine configuration name
        """
        if spec.satisfies("%intel"):
            mach_c = "ifort"
        elif spec.satisfies("%gcc"):
            mach_c = "gfortran"
        else:
            raise NotImplementedError("Unknown compiler")
        if spec.satisfies("+mpi"):
            mach_m = "mpp"
        else:
            mach_m = "serial"
        return f"nci_gadi_{mach_c}_{mach_m}"


    def patch(self):
        """
        Fix serial builds on Gadi by replacing mpicc/mpif90 with serial compilers
        in the machine configuration files.
        See https://github.com/ACCESS-NRI/gcom/blob/vn8.4/fcm-make/machines/nci_gadi_ifort_serial.cfg
        """
        spec = self.spec
        if spec.satisfies("~mpi"):
            machine = self.gcom_machine(self.spec)
            cfg_path = join_path("fcm-make", "machines", f"{machine}.cfg")
            filter_file("mpicc", "cc", cfg_path)
            filter_file("mpif90", "fc", cfg_path)


    def install(self, spec, prefix):
        fcm = which("fcm")

        # Set up variables used by fcm-make/gcom.cfg
        env["ACTION"] = "preprocess build"
        env["GCOM_SOURCE"] = "$HERE/.."
        env["DATE"] = ""
        env["REMOTE_ACTION"] = ""
        env["ROSE_TASK_MIRROR_TARGET"] = "localhost"

        # Decide on the build variant
        env["GCOM_MACHINE"] = self.gcom_machine(spec)

        # Do the build with fcm
        fcm("make", "-f", "fcm-make/gcom.cfg")

        self.__create_pkgconfig(spec, prefix)

        # Install the library
        mkdirp(prefix.lib)
        install("build/lib/libgcom.a", prefix.lib + "/libgcom.a")
        install_tree("build/lib/pkgconfig", prefix.lib + "/pkgconfig")
        install_tree("build/include", prefix.include)

    def __create_pkgconfig(self, spec, prefix):

        version = self.spec.version.string

        # Location to install pkgconf file
        pkgdir = "build/lib/pkgconfig"
        mkdirp(pkgdir)

        for k in ["gcom"]:

            lib = f"lib{k}.a"
            text = f"""\
prefix={prefix}
exec_prefix=${{prefix}}
libdir=${{exec_prefix}}/lib
includedir=${{prefix}}/include

Name: {lib}
Description: GCOM {version} {lib} Library for Fortran
Version: {version}
Libs: -L${{libdir}} -l{lib}
Cflags: -I${{includedir}}
"""
            pcpath = join_path(pkgdir, f"lib{k}.pc")
            with open(pcpath, "w", encoding="utf-8") as pc:
                nchars_written = pc.write(text)

            if nchars_written < len(text):
                raise OSError