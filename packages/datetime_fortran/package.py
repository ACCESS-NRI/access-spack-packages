# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install datetime-fortran
#
# You can edit this file again by typing:
#
#     spack edit datetime-fortran
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack_repo.builtin.build_systems.autotools import AutotoolsPackage
from spack.package import *


class DatetimeFortran(AutotoolsPackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://github.com/wavebitscientific/datetime-fortran/tree/main"

    maintainers('aidanheerdegen', 'milancurcic')

    version('1.7.0', sha256='cff4c1f53af87a9f8f31256a3e04176f887cc3e947a4540481ade4139baf0d6f')
    version('1.6.2', sha256='765f4ea77e9057f099612f66e52f92162f9f6325a8d219e67cb9d5ebaa41b67e')
    version('1.6.1', sha256='a503319209c6b9abe2fd0dc46f3b0d096154ac6edad9a106270f82aef6d248c0')
    version('1.6.0', sha256='e46c583bca42e520a05180984315495495da4949267fc155e359524c2bf31e9a')
    version('1.5.0', sha256='e9a200767b744afd2a3b10363315eacb7c92293c7e638d45bf16ebbce168860d')
    version('1.4.3', sha256='e3cb874fde0d36a97e282689eef459e8ce1973183d9acd95568149bc2d74436d')
    version('1.4.2', sha256='5b70c6e5d38032951e879b437e9ac7c5d483860ce8a9f6bbe6f1d6cd777e737f')
    version('1.4.1', sha256='4a178b63301f0016b7634625062278742a44026f4c37cafcb9e8ba9649db85e0')

    depends_on("fortran", type="build")

    patch("0001-Enable-deterministic-builds-using-D-flag-for-ar.patch", when="@1.7.0")

    def url_for_version(self, version):
        return "https://github.com/wavebitscientific/datetime-fortran/releases/download/v{0}/datetime-fortran-{0}.tar.gz".format(version)

    # https://spack-tutorial.readthedocs.io/en/ecp21/tutorial_advanced_packaging.html
    @property
    def libs(self):
        libraries = ["libdatetime"]
        return find_libraries(
            libraries, root=self.prefix, shared=False, recursive=True
        )
