# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *

# These are the default layouts, inc 3 executables for OM2
# alternatively, supply the 5 layout variants to produce 1 executable
OM2_LAYOUTS = [
        {"nxglob": "360", "nyglob": "300", "blckx": "15", "blcky": "300", "mxblcks": "1"},
        {"nxglob": "1440", "nyglob": "1080", "blckx": "30", "blcky": "27", "mxblcks": "4"},
        {"nxglob": "3600", "nyglob": "2700", "blckx": "40", "blcky": "30", "mxblcks": "12"},
    ]
ESM1P6_LAYOUTS = [
    {"nxglob": "360", "nyglob": "300", "blckx": "30", "blcky": "300", "mxblcks": "1"},
]


def _int_validator(s):
    """Test a string variant is a valid integer"""
    if (s != "none"):
        if (s.isdigit() and int(s) > 0):
            return True
        else:
            print(f"ERROR: {s} not a valid integer")
            return False


class Cice5(CMakePackage):
    """The Los Alamos sea ice model (CICE) is the result of an effort to develop 
    a computationally efficient sea ice component for a fully coupled 
    atmosphere-land global climate model."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/cice5.git"

    maintainers("anton-seaice", "harshula")
    license("BSD-3-Clause", checked_by="anton-seaice")

    version("stable", branch="master", preferred=True)
    version("2026.01.000", tag="2026.01.000", commit="cf5df9d4d26265dc5c79e558e5a67834b51fd38d")
    # TODO: the versions below can be removed once we are convinced they are not in use anywhere
    version("access-om2", branch="master")
    version("access-esm1.6", branch="access-esm1.6")

    variant(
        "model",
        default="access-om2",
        values=("access-om2", "access-esm1.6"),
        description="Which model this build is coupled with"
    )

    conflicts(
        "model=access-esm1.6",
        when="@access-om2",
        msg="model=access-esm1.6 not included in @access-om2"
    )

    conflicts(
        "model=access-om2",
        when="@access-esm1.6",
        msg="model=access-om2 not included in @access-esm1.6"
    )

    variant("deterministic", default=False, description="Deterministic build.")

    variant("io_type", default="NetCDF", values=("NetCDF", "PIO"), description="CICE IO Method")
    # User set integer cmake options:
    variant("nxglob", default="none", values=_int_validator, description="Size of model grid in x")
    variant("nyglob", default="none", values=_int_validator, description="Size of model grid in y")
    variant("blckx", default="none", values=_int_validator, description="Size of computational blocks in x")
    variant("blcky", default="none", values=_int_validator, description="Size of computational blocks in y")
    variant("mxblcks", default="none", values=_int_validator, description="Max number of blocks per task")
    depends_on("cmake@3.18:", type="build")

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    # Depend on virtual package "mpi".
    depends_on("mpi")
    depends_on("netcdf-fortran@4.5.2:")
    depends_on("netcdf-c@4.7.4:")
    depends_on("datetime-fortran")
    depends_on("oasis3-mct+deterministic", when="+deterministic")
    depends_on("oasis3-mct~deterministic", when="~deterministic")

    # With cmake, can be configued to use NetCDF or PIO
    # For release 2026.01 and later, needs parallelio 2.6.8
    # TODO: For initial verification we are going to use static pio.
    #       Eventually we plan to move to shared pio
    #       ~shared requires: https://github.com/spack/spack/pull/34837

    with when("io_type=PIO"):
        depends_on("parallelio~pnetcdf~timing~shared")
        depends_on("parallelio@2.6.8:", when="@2026.01:")

    with when("model=access-om2"):
        depends_on("libaccessom2+deterministic", when="+deterministic")
        depends_on("libaccessom2~deterministic", when="~deterministic")

    phases = ["set_layouts", "cmake", "build", "install"]

    _all_layouts = [{}]  # all layouts to build,
    # see OM2_LAYOUTS and ESM1P6_LAYOUTS for examples
    _layout = {}  # current layout being setup/built/installed

    def cmake_args(self):
        """List of the arguments that must be passed to cmake.
        These are set based on the values in _layout.
        cmake_args is called during super().cmake()
        """
        if self.spec.variants["model"].value == "access-esm1.6":
            args = [self.define("CICE_DRIVER", "access")]
        else:  # access-om2
            args = [self.define("CICE_DRIVER", "auscom")]

        args.extend([
            self.define("CICE_NXGLOB", self._layout['nxglob']),
            self.define("CICE_NYGLOB", self._layout['nyglob']),
            self.define("CICE_BLCKX", self._layout['blckx']),
            self.define("CICE_BLCKY", self._layout['blcky']),
            self.define("CICE_MXBLCKS", self._layout['mxblcks']),
            self.define_from_variant("CICE_IO", "io_type"),
            self.define_from_variant("CICE_DETERMINISTIC", "deterministic"),
        ])

        return args

    @property
    def build_dirname(self) -> str:
        """Directory name to use when building the package. 
        We modify this using _layout to ensure uniqueness with multiple builds
        """
        build = (
            f"{self._layout['nxglob']}x{self._layout['nyglob']}_"
            f"{self._layout['blckx']}x{self._layout['blcky']}_"
            f"{self._layout['mxblcks']}"
        )
        return f"{super().build_dirname}/{build}"

    def set_layouts(self, spec, prefix):
        """Layout of cice processors to use. If variants are set, use those. 
        Otherwise, use defaults."""
        layout_variants = OM2_LAYOUTS[0].keys()

        # if all 5 layouts variants are available, set the layouts dict
        if all([
            self.spec.variants[variant].value != 'none' 
            for variant in layout_variants
        ]):
            layouts = [{variant: self.spec.variants[variant].value
                for variant in layout_variants}]
        # else if no layout variants are available, use the defaults
        elif all([
            self.spec.variants[variant].value == 'none' 
            for variant in layout_variants
        ]):
            if self.spec.variants["model"].value == "access-esm1.6":
                layouts = ESM1P6_LAYOUTS
            else:
                layouts = OM2_LAYOUTS
        else:
            raise Error(f"All of {layout_variants} "
                        "variants must be set if any are set")

        self._all_layouts = layouts

    def cmake(self, spec, prefix):
        for layout in self._all_layouts:
            self._layout = layout
            super().cmake(spec, prefix)

    def build(self, spec, prefix):
        for layout in self._all_layouts:
            self._layout = layout
            super().build(spec, prefix)

    def install(self, spec, prefix):
        for layout in self._all_layouts:
            self._layout = layout
            super().install(spec, prefix)

