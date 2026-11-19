# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class Jigsaw(CMakePackage):
    """Unstructured mesh generator and tessellation library."""

    homepage = "https://github.com/dengwirda/jigsaw"
    git = "https://github.com/dengwirda/jigsaw.git"

    # This is a custom license, free for non-commercial use, but requires a license for commercial use. 
    # See LICENSE file in the source code.
    license("LicenseRef-JIGSAW", checked_by="aidan")

    version("develop", branch="master", preferred=True, no_cache=True)
    version("0.9.14", sha256="f312ea0bc3ca697ea0f559b8404d0afe3e35dd0b39efc0efdfb9a9a57bee16d7")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("cmake@3.9.4:", type="build")

    def patch(self):
        if self.spec.satisfies("@0.9.14"):
            # The install rule is in src/, but the public headers are in the top-level inc/.
            filter_file(
                "DIRECTORY inc/",
                'DIRECTORY "${PROJECT_SOURCE_DIR}/inc/"',
                "src/CMakeLists.txt",
                string=True,
            )
