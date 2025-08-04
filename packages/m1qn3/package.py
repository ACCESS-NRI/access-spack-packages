# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 Angus Gibson
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack_repo.builtin.build_systems.makefile import MakefilePackage
from spack.package import *


class M1qn3(MakefilePackage):
    """Minimise functions depending on a very large number of variables."""

    homepage = "https://who.rocq.inria.fr/Jean-Charles.Gilbert/modulopt/optimization-routines/m1qn3/m1qn3.html"

    version("3.3", sha256="27c6a8f56a4080420c25ffb0743e3dece7c57cc1740776936f220b4ed28b89d9")

    depends_on("fortran", type="build")

    patch("m1qn3.patch")

    def url_for_version(self, version):
        url = "https://github.com/ISSMteam/ExternalPackages/raw/refs/heads/main/m1qn3-{0}-distrib.tgz"
        return url.format(version)

    def edit(self, spec, prefix):
        with open("Makefile", "w") as f:
            f.write(f"""
LIB_EXT=a
FC={spack_fc}
install: libm1qn3.$(LIB_EXT) libddot.$(LIB_EXT)
	install -D libm1qn3.$(LIB_EXT) {prefix}/lib/libm1qn3.$(LIB_EXT)
	install -D libddot.$(LIB_EXT) {prefix}/lib/libddot.$(LIB_EXT)
OBJECTS=src/m1qn3.o
libm1qn3.$(LIB_EXT): $(OBJECTS)
	ar -r $@ $(OBJECTS)
	ranlib $@
DDOT_OBJECTS=blas/ddot.o
libddot.$(LIB_EXT): $(DDOT_OBJECTS)
	ar -r $@ $(DDOT_OBJECTS)
	ranlib $@
%.o: %.f
	$(FC) $(FFLAGS) -fPIC -c $< -o $@
""")

