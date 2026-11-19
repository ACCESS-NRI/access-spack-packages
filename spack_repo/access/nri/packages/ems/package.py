# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.makefile import MakefilePackage
from spack.package import *


class Ems(MakefilePackage):
    """CSIRO Environmental Modelling Suite, including SHOC and COMPAS."""

    homepage = "https://github.com/csiro-coasts/EMS"
    git = "https://github.com/csiro-coasts/EMS.git"

    # Custom CSIRO license. Free and open to use with conditions, see LICENSE.md 
    # in the source tree for details.
    license("LicenseRef-CSIRO-EMS", checked_by="aidan")

    maintainers("aidan", "helenmacdonald", "frizwi")

    version("1.5.3", tag="v1.5.3", commit="a0f8eb016cebb64470c01407d1362d5ecba61343")

    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("netcdf-c")
    depends_on("metis@5:~int64")
    # EMS uses double-precision JIGSAW mesh values; develop uses single precision.
    depends_on("jigsaw@0.9.14")

    def setup_build_environment(self, env):
        env.set("NETCDF_ROOT", self.spec["netcdf-c"].prefix)

    def edit(self, spec, prefix):
        if spec.satisfies("platform=darwin"):
            # Upstream's library search does not recognize macOS shared libraries.
            filter_file(
                "for ac_extension in a so sl;",
                "for ac_extension in a so sl dylib;",
                "conf/configure",
                string=True,
            )
            # macOS lacks values.h; use the standard floating-point limits instead.
            filter_file("#include <values.h>", "#include <float.h>", "lib/geom/poly.c", string=True)
            # MAXDOUBLE comes from values.h; DBL_MAX is its standard equivalent.
            filter_file("MAXDOUBLE", "DBL_MAX", "lib/geom/poly.c", string=True)
            # The grid code needs integer limits, not the unavailable values.h.
            filter_file("#include <values.h>", "#include <limits.h>", "lib/grid/xytoij.c", string=True)
            # Replace the nonstandard finite() with the C99 isfinite() macro.
            filter_file(
                r"\bfinite\(",
                "isfinite(",
                "model/lib/ecology/cell.c",
                "model/lib/ecology/ecofunct.c",
                "model/lib/sediments/hd2sed.c",
                "model/lib/sediments/sed2hd.c",
            )
        # Ecology calls these model functions without declarations, which modern C compilers reject.
        filter_file(
            '#include "bio_opt.h"',
            '#include "bio_opt.h"\n'
            "void write_text_att(int, int, const char *, const char *);\n"
            "void write_date_created(int);",
            "model/lib/ecology/include/ecology_internal.h",
            string=True,
        )
        # COMPAS calls concave_hull without declaring its pointer return type.
        filter_file(
            "point *convex_hull(point *v,  int *count);",
            "point *convex_hull(point *v,  int *count);\n"
            "point *concave_hull(delaunay *, point *, int *, int *, int **);",
            "model/hd-us/include/proto.h",
            string=True,
        )
        # Declare the ecology tracer predicate before its first use.
        filter_file(
            "int is_tracer_type_optical(int type);",
            "int is_tracer_type_ecology(int type);\nint is_tracer_type_optical(int type);",
            "model/hd-us/tracers/tracer_info.c",
            string=True,
        )
        # Semaphore fields exist only when pthread support is enabled.
        filter_file(
            "  e->sm_fill = NULL;",
            "#ifdef HAVE_PTHREADS\n  e->sm_fill = NULL;",
            "model/hd/control/scheduler.c",
            "model/hd-us/control/scheduler.c",
            string=True,
        )
        # Close the pthread guard after initializing both semaphore fields.
        filter_file(
            "  e->sm_dump = NULL;",
            "  e->sm_dump = NULL;\n#endif",
            "model/hd/control/scheduler.c",
            "model/hd-us/control/scheduler.c",
            string=True,
        )
        configure = Executable("./conf/configure")
        configure("--prefix={0}".format(prefix), "--with-metis={0}".format(spec["metis"].prefix))

        # Link COMPAS against Spack's JIGSAW rather than the bundled copy.
        makefile = FileFilter("model/hd-us/makefile")
        makefile.filter(r"^JIGSAWINC=.*", "JIGSAWINC=-I{0}".format(spec["jigsaw"].prefix.include))
        makefile.filter(r"^JIGSAWLIB=.*", "JIGSAWLIB=-L{0} -ljigsaw".format(spec["jigsaw"].prefix.lib))
        makefile.filter(r" -Xlinker -rpath=[^ ]*/ext/jigsaw/lib", "")
        # Replace the bundled JIGSAW's hard-coded version in COMPAS output.
        filter_file(
            r"jigsaw\\t\\t 0\.9\.7\\text",
            r"jigsaw\\t\\t {0}\\text".format(spec["jigsaw"].version),
            "model/hd-us/control/main.c",
        )

    def build(self, spec, prefix):
        # The upstream top-level makefile masks failures in its recursive loop.
        for directory in (
            "lib",
            "model/lib/ecology",
            "model/lib/sediments",
            "model/lib/tracerstats",
            "model/lib/waves",
            "model/hd",
            "model/hd-us",
        ):
            make("-C", directory)

    def install(self, spec, prefix):
        mkdirp(prefix.bin)
        install("model/hd/shoc", prefix.bin)
        install("model/hd-us/compas", prefix.bin)
        install("LICENSE.md", prefix)
