# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/coecms/access-esm-build-gadi/blob/master/Makefile
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Dummygrib(MakefilePackage):
    """
    dummygrib is a Dummy GRIB library to use with the Met Office Unified Model.
    """

    homepage = "https://github.com/ACCESS-NRI/dummygrib"
    git = "https://github.com/ACCESS-NRI/dummygrib.git"

    maintainers("penguian")

    version("1.0", branch="master")


    def install(self, spec, prefix):

        # Install the library
        mkdirp(prefix.lib)
        install(
            "libdummygrib.a",
            join_path(prefix.lib, "libdummygrib.a"))

