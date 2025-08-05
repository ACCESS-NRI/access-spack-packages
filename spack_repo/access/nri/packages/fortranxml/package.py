# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.autotools import AutotoolsPackage
from spack.package import *


class Fortranxml(AutotoolsPackage):
    """Fortran XML (FoX) s a library, written entirely in Fortran, designed to allow
    the easy use of XML from Fortran programs. FoX caters for both XML output
    and input.
    """

    homepage = "https://github.com/andreww/fox"
    git = "https://github.com/andreww/fox.git"

    maintainers("harshula")

    version("4.1.2", sha256="1938725be45b8be5387a51fa0b25ee78ffee87ca8a497b82545ab870f33f8b88")

    depends_on("fortran", type="build")

    def url_for_version(self, version):
        return "https://github.com/andreww/fox/tarball/{0}".format(version)

    def install(self, spec, prefix):
        super(AutotoolsPackage, self).install(spec, prefix)

        pkgconfig_dir = join_path(prefix.lib, "pkgconfig")
        pkgconfig_file = join_path(pkgconfig_dir, "fox.pc")
        mkdir(pkgconfig_dir)

        with open(pkgconfig_file, "w", encoding="utf-8") as pc:
            pc.write(f"""\
prefix={prefix}
exec_prefix=${{prefix}}
libdir=${{exec_prefix}}/lib
includedir=${{prefix}}/finclude

Name: Fortran XML (FoX)
Description: A Fortran XML library
Version: {spec.version}
Libs: -L${{libdir}} -lFoX_dom -lFoX_sax -lFoX_wcml -lFoX_wkml -lFoX_wxml -lFoX_common -lFoX_utils -lFoX_fsys
Cflags: -I${{includedir}}
""")
