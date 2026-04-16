from spack.package import *


class AdjointPetsc(CMakePackage):
    """adjoint-PETSc is a beta library that provides algorithmic
    differentiation support for PETSc, currently targeting the subset
    of functionality required by ISSM.

    Features:
      - vector mode support
      - online activity analysis
      - implemented with C++23
      - C++11 interface

    Current restriction:
      - hard-coded to use CoDiPack
    """

    homepage = "https://github.com/SciCompKL/adjoint-PETSc"
    git      = "https://github.com/SciCompKL/adjoint-PETSc.git"

    license("LGPL-3.0-only")

    version("main", branch="main")

    variant("shared", default=True, description="Build shared libraries")
    variant("examples", default=False, description="Build examples")
    variant("tests", default=False, description="Build tests")

    depends_on("cmake@3.16:", type="build")
    depends_on("pkgconfig", type="build")

    depends_on("petsc")
    depends_on("codipack")
    depends_on("cxx", type="build")  # optional in some repos; can remove if your Spack setup dislikes it

    conflicts("%gcc@:10", when="@", msg="adjoint-PETSc requires C++23 support")
    conflicts("%clang@:14", when="@", msg="adjoint-PETSc requires C++23 support")
    conflicts("%apple-clang@:15", when="@", msg="adjoint-PETSc requires C++23 support")

    def cmake_args(self):
        args = [
            self.define_from_variant("BUILD_SHARED_LIBS", "shared"),
            self.define_from_variant("BUILD_EXAMPLES", "examples"),
            self.define_from_variant("BUILD_TESTING", "tests"),
            self.define("CoDiPack_DIR", self.spec["codipack"].prefix),
            self.define("PETSc_DIR", self.spec["petsc"].prefix),
            self.define("CMAKE_CXX_STANDARD", 23),
            self.define("CMAKE_CXX_STANDARD_REQUIRED", True),
        ]
        return args