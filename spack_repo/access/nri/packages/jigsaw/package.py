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

    maintainers("aidan", "helenmacdonald")
    version("develop", branch="master", preferred=True, no_cache=True)
    version("0.9.14", tag="0.9.14", commit="e848583231b6d8a2a366037fa45123a819d4eec2")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("cmake@3.9.4:", type="build")

