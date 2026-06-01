# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)!

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *


class AdjointPetsc(CMakePackage):
    """adjoint-PETSc is a beta library that provides algorithmic
    differentiation support for PETSc, currently targeting the subset
    of functionality required by ISSM.

    Warning: This library is no longer under active development,
    but is available for use in ISSM for users who need it.

    Features:
      - vector mode support
      - online activity analysis
      - implemented with C++23
      - C++11 interface

    Current restriction:
      - hard-coded to use CoDiPack

    This recipe is intentionally ACCESS-local rather than upstreamed because it
    currently targets ISSM-specific AD workflows and carries local compiler
    constraints that are not broadly useful to the wider Spack ecosystem.
    """

    homepage = "https://github.com/SciCompKL/adjoint-PETSc"
    git      = "https://github.com/SciCompKL/adjoint-PETSc.git"

    maintainers("justinh2002")

    license("LGPL-3.0-only", checked_by="justinh2002")

    version("stable", branch="master", preferred=True)

    variant("shared", default=True, description="Build shared libraries")
    variant("examples", default=False, description="Build examples")
    variant("build-tests", default=False, description="Enable CMake BUILD_TESTING targets")

    depends_on("cmake@3.20:", type="build")
    depends_on("pkgconfig", type="build")
    depends_on("cxx", type="build")

    # dependencies required for adjoint-PETSc, but not necessarily for PETSc itself.
    # This PETSc variant set reflects what adjoint-PETSc and ISSM AD builds need;
    # upstream source does not expose a robust feature matrix for weaker PETSc configs.
    depends_on("petsc~examples+metis+mumps+scalapack")
    depends_on("codipack")

    # adjoint-PETSc requires C++23 support
    # Note: GCC 11+ supports C++23, but full support is not available until GCC 12.
    conflicts("%gcc@:10", msg="adjoint-PETSc requires C++23 support (GCC 11+). Release notes: https://gcc.gnu.org/projects/cxx-status.html#cxx23")
    conflicts("%clang@:14", msg="adjoint-PETSc requires C++23 support (Clang 15+). Release notes: https://clang.llvm.org/cxx_status.html#cxx23")
    conflicts("%apple-clang@:15", msg="adjoint-PETSc requires C++23 support (Apple Clang 16+). Release notes: https://developer.apple.com/documentation/xcode-release-notes")
    conflicts("%intel", msg="adjoint-PETSc is not supported with classic Intel compilers in this recipe. Release notes: https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-dpcpp-cpp-compiler-release-notes.html")
    conflicts("%oneapi", msg="adjoint-PETSc is not currently supported with oneAPI in this recipe. Release notes: https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-dpcpp-cpp-compiler-release-notes.html")

    def cmake_args(self):
        args = [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define_from_variant("BUILD_EXAMPLES", "examples"),
            self.define_from_variant("BUILD_TESTING", "build-tests"),
            self.define("CoDiPack_DIR", join_path(self.spec["codipack"].prefix, "share", "CoDiPack", "cmake")),
            self.define("PETSc_DIR", self.spec["petsc"].prefix),
            self.define("CMAKE_CXX_STANDARD", 23),
            self.define("CMAKE_CXX_STANDARD_REQUIRED", True),
        ]
        return args