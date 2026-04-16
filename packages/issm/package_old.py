# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 Angus Gibson
# Modified by Justin Kin Jun Hew, 2025
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Issm(AutotoolsPackage):
    """Ice-sheet and Sea-Level System Model"""

    homepage = "https://issm.jpl.nasa.gov/"
    git = "https://github.com/ACCESS-NRI/ISSM.git"
    
    version("main", branch="main", preferred=True)
    version("4.24", sha256="c71d870e63f0ce3ae938d6a669e80dc2cecef827084db31a4b2cfc3a26a44820")

    variant("wrappers", default=False, description="Enable building with wrappers")

    depends_on("autoconf", type="build")
    depends_on("automake", type="build")
    depends_on("libtool", type="build")
    depends_on("m4", type="build")

    depends_on("mpi")
    depends_on("petsc+metis+mumps+scalapack")
    depends_on("m1qn3")

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/ISSM/tarball/v{0}".format(version)

    def autoreconf(self, spec, prefix):
        autoreconf("--install", "--verbose", "--force")

    def configure_args(self):
        args = [
            "--enable-debugging",
            "--enable-development",
            "--enable-shared",
            "--without-kriging",
        ]

        if "+wrappers" in self.spec:
            args.append("--with-wrappers=yes")
        else:
            args.append("--with-wrappers=no")

        args.append("--with-petsc-dir={0}".format(self.spec["petsc"].prefix))
        args.append("--with-metis-dir={0}".format(self.spec["metis"].prefix))
        args.append("--with-mumps-dir={0}".format(self.spec["mumps"].prefix))
        args.append("--with-m1qn3-dir={0}".format(self.spec["m1qn3"].prefix.lib))

        # Even though we set the MPI compilers manually, the build system
        # wants us to explicitly request an MPI-enabled build by telling
        # it the MPI include directory.
        args.append("--with-mpi-include={0}".format(self.spec["mpi"].prefix.include))
        args.append("CC=" + self.spec["mpi"].mpicc)
        args.append("CXX=" + self.spec["mpi"].mpicxx)
        args.append("FC=" + self.spec["mpi"].mpifc)
        args.append("F77=" + self.spec["mpi"].mpif77)

        return args
