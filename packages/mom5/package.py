# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.build_systems import cmake, makefile
from spack.version.version_types import GitVersion, StandardVersion
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.makefile import MakefilePackage
from spack.package import *


class Mom5(CMakePackage, MakefilePackage):
    """MOM is a numerical ocean model based on the hydrostatic primitive equations."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/mom5.git"

    maintainers("dougiesquire", "harshula", "penguian")

    # https://github.com/ACCESS-NRI/MOM5#LGPL-3.0-1-ov-file
    license("LGPL-3.0-only", checked_by="dougiesquire")

    version("mom_solo", branch="master")
    version("mom_sis", branch="master")
    version("access-om2", branch="master", preferred=True)
    version("legacy-access-om2-bgc", branch="master")
    version("access-esm1.5", branch="access-esm1.5")
    version("access-esm1.6", branch="master")

    # NOTE: @mom matches both mom_solo and mom_sis
    build_system(
        conditional("makefile", when="@access-om2,legacy-access-om2-bgc,access-esm1.5"),
        conditional("cmake", when="@mom,access-om2,legacy-access-om2-bgc,access-esm1.6"),
        default="cmake",
    )

    with when("build_system=cmake"):
        variant("build_type", default="RelWithDebInfo",
            description="CMake build type",
            values=("Debug", "Release", "RelWithDebInfo")
        )
        variant("deterministic", default=False, description="Deterministic build")

    with when("build_system=makefile"):
        variant("restart_repro", default=True, description="Reproducible restart build.")
        variant(
            "deterministic",
            default=False,
            description="Deterministic build",
            when="@access-om2,legacy-access-om2-bgc"
        )
        variant(
            "optimisation_report",
            default=False,
            description="Generate optimisation reports",
            when="@access-om2,legacy-access-om2-bgc"
        )

    with when("@mom,access-om2,legacy-access-om2-bgc,access-esm1.6"):
        depends_on("netcdf-c@4.7.4:")
        depends_on("netcdf-fortran@4.5.2:")
        # Depend on virtual package "mpi".
        depends_on("mpi")

    with when("@access-om2,legacy-access-om2-bgc"):
        depends_on("datetime-fortran")
        depends_on("libaccessom2+deterministic", when="+deterministic")
        depends_on("libaccessom2~deterministic", when="~deterministic")

    with when("@access-om2,legacy-access-om2-bgc,access-esm1.6"):
        depends_on("oasis3-mct+deterministic", when="+deterministic")
        depends_on("oasis3-mct~deterministic", when="~deterministic")

    # NOTE: Spack will also match "access-om2-legacy-bgc" here, that's why
    #       it has been renamed to "legacy-access-om2-bgc".
    with when("@access-om2,access-esm1.6"):
        depends_on("access-fms")
        depends_on("access-generic-tracers")

    # legacy-access-om2-bgc builds with access-generic-tracers but it
    # is not configured for use in ACCESS-OM2-BGC configurations.
    with when("@legacy-access-om2-bgc"):
        depends_on("access-fms", when="build_system=cmake")
        depends_on("access-generic-tracers", when="build_system=cmake")

    with when("@access-esm1.5"):
        depends_on("netcdf-c@4.7.1:")
        depends_on("netcdf-fortran@4.5.1:")
        depends_on("openmpi")
        depends_on("oasis3-mct@access-esm1.5")

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/mom5/tarball/{0}".format(version)


class CMakeBuilder(cmake.CMakeBuilder):
    root_cmakelists_dir = "cmake/"

    phases = ("setup", "cmake", "build", "install")

    # NOTE: The keys in the __builds variable are required to check whether
    #       a valid version was passed in by the user.
    __builds = {
        "mom_solo": "MOM5_SOLO",
        "mom_sis": "MOM5_SIS",
        "access-om2": "MOM5_ACCESS_OM",
        "access-esm1.6": "MOM5_ACCESS_ESM",
        "legacy-access-om2-bgc": "MOM5_ACCESS_OM_BGC"
    }
    __version = "INVALID"

    # NOTE: This functionality will hopefully be implemented in the Spack core
    #       in the future. Till then, this approach can be used in other SPRs
    #       where this functionality is required.
    def setup(self, pkg, spec, prefix):
        if isinstance(pkg.version, GitVersion):
            self.__version = pkg.version.ref_version.string
        elif isinstance(pkg.version, StandardVersion):
            self.__version = pkg.version.string
        else:
            raise ValueError("version=" + pkg.version.string)

        # The rest of the checks are only required if a __builds member
        # variable exists
        if self.__version not in self.__builds.keys():
            raise ValueError(
                f"CMakeBuilder doesn't support version {self.__version}. The version must "
                "be selected from: " + ", ".join(self.__builds.keys())
            )

        print("INFO: version=" + self.__version +
                " type=" + self.__builds[self.__version])

    def cmake_args(self):
        args = [
            self.define("MOM5_TYPE", self.__builds[self.__version]),
            self.define_from_variant("MOM5_DETERMINISTIC", "deterministic"),
        ]
        return args


class MakefileBuilder(makefile.MakefileBuilder):
    phases = ("setup", "edit", "build", "install")

    __builds = {
        "access-om2": "ACCESS-OM",
        "legacy-access-om2-bgc": "ACCESS-OM-BGC",
        "access-esm1.5": "ACCESS-CM"
    }
    __version = "INVALID"
    __platform = "spack"

    # NOTE: This functionality will hopefully be implemented in the Spack core
    #       in the future. Till then, this approach can be used in other SPRs
    #       where this functionality is required.
    def setup(self, pkg, spec, prefix):
        if isinstance(pkg.version, GitVersion):
            self.__version = pkg.version.ref_version.string
        elif isinstance(pkg.version, StandardVersion):
            self.__version = pkg.version.string
        else:
            raise ValueError("version=" + pkg.version.string)

        # The rest of the checks are only required if a __builds member
        # variable exists
        if self.__version not in self.__builds.keys():
            raise ValueError(
                f"MakefileBuilder doesn't support version {self.__version}. The version must "
                "be selected from: " + ", ".join(self.__builds.keys())
            )

        print("INFO: version=" + self.__version +
                " type=" + self.__builds[self.__version])

    def edit(self, pkg, spec, prefix):

        srcdir = pkg.stage.source_path
        makeinc_path = join_path(srcdir, "bin", "mkmf.template.spack")
        config = {}

        # NOTE: The order of the libraries matters during the linking step!
        if self.__version == "access-esm1.5":
            istr = " ".join([
                    join_path((spec["oasis3-mct"].headers).cpp_flags, "psmile.MPI1"),
                    join_path((spec["oasis3-mct"].headers).cpp_flags, "mct")])
            ideps = ["netcdf-fortran"]
            ldeps = ["oasis3-mct", "netcdf-c", "netcdf-fortran"]
            FFLAGS_OPT = "-O3 -debug minimal -xCORE-AVX512 -align array64byte"
            CFLAGS_OPT = "-O2 -debug minimal -no-vec"
        else:
            istr = join_path((spec["oasis3-mct"].headers).cpp_flags, "psmile.MPI1")
            ideps = ["oasis3-mct", "libaccessom2", "netcdf-fortran"]
            # NOTE: datetime-fortran is a dependency of libaccessom2.
            ldeps = ["oasis3-mct", "libaccessom2", "netcdf-c", "netcdf-fortran", "datetime-fortran"]

            # TODO: https://github.com/ACCESS-NRI/ACCESS-OM/issues/12
            FFLAGS_OPT = "-g3 -O2 -xCORE-AVX2 -debug all -check none -traceback"
            CFLAGS_OPT = "-O2 -debug minimal -xCORE-AVX2"
            if self.spec.satisfies("+deterministic"):
                FFLAGS_OPT = "-g0 -O0 -xCORE-AVX2 -debug none -check none"
                CFLAGS_OPT = "-O0 -debug none -xCORE-AVX2"
                print("INFO: +deterministic applied")

        incs = " ".join([istr] + [(spec[d].headers).cpp_flags for d in ideps])
        libs = " ".join([(spec[d].libs).ld_flags for d in ldeps])

        # Copied from bin/mkmf.template.ubuntu
        config["gcc"] = f"""
FC = mpifort
CC = gcc
LD = $(FC)
#########
# flags #
#########
DEBUG =
REPRO =
VERBOSE =
OPENMP =

MAKEFLAGS += --jobs=$(shell grep '^processor' /proc/cpuinfo | wc -l)

FPPFLAGS := 

FFLAGS := -fcray-pointer -fdefault-real-8 -ffree-line-length-none -fno-range-check -Waliasing -Wampersand -Warray-bounds -Wcharacter-truncation -Wconversion -Wline-truncation -Wintrinsics-std -Wsurprising -Wno-tabs -Wunderflow -Wunused-parameter -Wintrinsic-shadow -Wno-align-commons -fallow-argument-mismatch -fallow-invalid-boz
FFLAGS += {incs}
FFLAGS += -DGFORTRAN

#
FFLAGS_OPT = -O2
FFLAGS_REPRO = 
FFLAGS_DEBUG = -O0 -g -W -fbounds-check 
FFLAGS_OPENMP = -fopenmp
FFLAGS_VERBOSE = 

CFLAGS := -D__IFC {incs}
CFLAGS += $(shell nc-config --cflags)
CFLAGS_OPT = -O2
CFLAGS_OPENMP = -fopenmp
CFLAGS_DEBUG = -O0 -g 

# Optional Testing compile flags.  Mutually exclusive from DEBUG, REPRO, and OPT
# *_TEST will match the production if no new option(s) is(are) to be tested.
FFLAGS_TEST = -O2
CFLAGS_TEST = -O2

LDFLAGS :=
LDFLAGS_OPENMP := -fopenmp
LDFLAGS_VERBOSE := 

ifneq ($(REPRO),)
CFLAGS += $(CFLAGS_REPRO)
FFLAGS += $(FFLAGS_REPRO)
endif
ifneq ($(DEBUG),)
CFLAGS += $(CFLAGS_DEBUG)
FFLAGS += $(FFLAGS_DEBUG)
else ifneq ($(TEST),)
CFLAGS += $(CFLAGS_TEST)
FFLAGS += $(FFLAGS_TEST)
else
CFLAGS += $(CFLAGS_OPT)
FFLAGS += $(FFLAGS_OPT)
endif

ifneq ($(OPENMP),)
CFLAGS += $(CFLAGS_OPENMP)
FFLAGS += $(FFLAGS_OPENMP)
LDFLAGS += $(LDFLAGS_OPENMP)
endif

ifneq ($(VERBOSE),)
CFLAGS += $(CFLAGS_VERBOSE)
FFLAGS += $(FFLAGS_VERBOSE)
LDFLAGS += $(LDFLAGS_VERBOSE)
endif

ifeq ($(NETCDF),3)
  # add the use_LARGEFILE cppdef
  ifneq ($(findstring -Duse_netCDF,$(CPPDEFS)),)
    CPPDEFS += -Duse_LARGEFILE
  endif
endif

LIBS := {libs}
LDFLAGS += $(LIBS)
"""

        # Copied from bin/mkmf.template.nci
        if self.__version == "access-esm1.5":
            config["intel"] = f"""
ifeq ($(VTRACE), yes)
    FC = mpifort-vt
    LD = mpifort-vt
else
    FC = mpifort
    LD = mpifort
endif

CC = mpicc

REPRO =
VERBOSE =
OPT = on

MAKEFLAGS += --jobs=4

INCLUDE = {incs}

FPPFLAGS := -fpp -Wp,-w $(INCLUDE)
FFLAGS := -fno-alias -safe-cray-ptr -fpe0 -ftz -assume byterecl -i4 -r8 -traceback -nowarn -check noarg_temp_created -assume buffered_io -convert big_endian
FFLAGS_OPT = {FFLAGS_OPT}
FFLAGS_DEBUG = -g -O0 -debug all -check -check noarg_temp_created -check nopointer -warn -warn noerrors -ftrapuv
FFLAGS_REPRO = -O2 -debug minimal -no-vec -fp-model precise
FFLAGS_VERBOSE = -v -V -what

CFLAGS := -D__IFC $(INCLUDE)
CFLAGS_OPT = {CFLAGS_OPT}
CFLAGS_DEBUG = -O0 -g -ftrapuv -traceback

LDFLAGS :=
LDFLAGS_VERBOSE := -Wl,-V,--verbose,-cref,-M

ifneq ($(REPRO),)
CFLAGS += $(CFLAGS_REPRO)
FFLAGS += $(FFLAGS_REPRO)
endif

ifneq ($(DEBUG),)
CFLAGS += $(CFLAGS_DEBUG)
FFLAGS += $(FFLAGS_DEBUG)
else
CFLAGS += $(CFLAGS_OPT)
FFLAGS += $(FFLAGS_OPT)
endif

ifneq ($(VERBOSE),)
CFLAGS += $(CFLAGS_VERBOSE)
FFLAGS += $(FFLAGS_VERBOSE)
LDFLAGS += $(LDFLAGS_VERBOSE)
endif

LIBS := {libs}

LDFLAGS += $(LIBS)
"""
        else:
            config["intel"] = f"""
ifeq ($(VTRACE), yes)
    FC := mpifort-vt
    LD := mpifort-vt
else
    FC := mpifort
    LD := mpifort
endif

CC := mpicc

VERBOSE :=
OPT := on

MAKEFLAGS += -j

INCLUDE   := {incs}

FPPFLAGS := -fpp -Wp,-w $(INCLUDE)
FFLAGS := -fno-alias -safe-cray-ptr -fpe0 -ftz -assume byterecl -i4 -r8 -nowarn -check noarg_temp_created -assume nobuffered_io -convert big_endian -grecord-gcc-switches -align all
FFLAGS_OPT := {FFLAGS_OPT}
FFLAGS_REPORT := -qopt-report=5 -qopt-report-annotate
FFLAGS_DEBUG := -g3 -O0 -debug all -check -check noarg_temp_created -check nopointer -warn -warn noerrors -ftrapuv -traceback
FFLAGS_REPRO := -fp-model precise -fp-model source -align all
FFLAGS_VERBOSE := -v -V -what

CFLAGS := -D__IFC $(INCLUDE)
CFLAGS_OPT := {CFLAGS_OPT}
CFLAGS_REPORT := -qopt-report=5 -qopt-report-annotate
CFLAGS_DEBUG := -O0 -g -ftrapuv -traceback
CFLAGS_REPRO := -fp-model precise -fp-model source

LDFLAGS :=
LDFLAGS_VERBOSE := -Wl,-V,--verbose,-cref,-M

ifneq ($(REPRO),)
CFLAGS += $(CFLAGS_REPRO)
FFLAGS += $(FFLAGS_REPRO)
endif

ifneq ($(DEBUG),)
CFLAGS += $(CFLAGS_DEBUG)
FFLAGS += $(FFLAGS_DEBUG)
else
CFLAGS += $(CFLAGS_OPT)
FFLAGS += $(FFLAGS_OPT)
endif

ifneq ($(VERBOSE),)
CFLAGS += $(CFLAGS_VERBOSE)
FFLAGS += $(FFLAGS_VERBOSE)
LDFLAGS += $(LDFLAGS_VERBOSE)
endif

ifneq ($(REPORT),)
CFLAGS += $(CFLAGS_REPORT)
FFLAGS += $(FFLAGS_REPORT)
endif

LIBS := {libs}

ifneq ($(OASIS_ROOT),)
LIBS += -L$(OASIS_ROOT)/Linux/lib -lpsmile.MPI1 -lmct -lmpeu -lscrip
endif

ifneq ($(LIBACCESSOM2_ROOT),)
LIBS += -L$(LIBACCESSOM2_ROOT)/build/lib -laccessom2
endif

LDFLAGS += $(LIBS)
"""

        # Add support for the ifx compiler
        # TODO: `.replace() is a temporary workaround for:
        # icx: error: unsupported argument 'source' to option '-ffp-model='
        # The `.replace()` apparently doesn't modify the object.
        config["oneapi"] = config["intel"].replace("CFLAGS_REPRO := -fp-model precise -fp-model source", "CFLAGS_REPRO := -fp-model precise")

        if self.__version == "access-esm1.5":
            config["post"] = """
# you should never need to change any lines below.

# see the MIPSPro F90 manual for more details on some of the file extensions
# discussed here.
# this makefile template recognizes fortran sourcefiles with extensions
# .f, .f90, .F, .F90. Given a sourcefile <file>.<ext>, where <ext> is one of
# the above, this provides a number of default actions:

# make <file>.opt	create an optimization report
# make <file>.o		create an object file
# make <file>.s		create an assembly listing
# make <file>.x		create an executable file, assuming standalone
#			source
# make <file>.i		create a preprocessed file (for .F)
# make <file>.i90	create a preprocessed file (for .F90)

# The macro TMPFILES is provided to slate files like the above for removal.

RM = rm -f
SHELL = /bin/csh -f
TMPFILES = .*.m *.B *.L *.i *.i90 *.l *.s *.mod *.opt

.SUFFIXES: .F .F90 .H .L .T .f .f90 .h .i .i90 .l .o .s .opt .x

.f.L:
	$(FC) $(FFLAGS) -c -listing $*.f
.f.opt:
	$(FC) $(FFLAGS) -c -opt_report_level max -opt_report_phase all -opt_report_file $*.opt $*.f
.f.l:
	$(FC) $(FFLAGS) -c $(LIST) $*.f
.f.T:
	$(FC) $(FFLAGS) -c -cif $*.f
.f.o:
	$(FC) $(FFLAGS) -c $*.f
.f.s:
	$(FC) $(FFLAGS) -S $*.f
.f.x:
	$(FC) $(FFLAGS) -o $*.x $*.f *.o $(LDFLAGS)
.f90.L:
	$(FC) $(FFLAGS) -c -listing $*.f90
.f90.opt:
	$(FC) $(FFLAGS) -c -opt_report_level max -opt_report_phase all -opt_report_file $*.opt $*.f90
.f90.l:
	$(FC) $(FFLAGS) -c $(LIST) $*.f90
.f90.T:
	$(FC) $(FFLAGS) -c -cif $*.f90
.f90.o:
	$(FC) $(FFLAGS) -c $*.f90
.f90.s:
	$(FC) $(FFLAGS) -c -S $*.f90
.f90.x:
	$(FC) $(FFLAGS) -o $*.x $*.f90 *.o $(LDFLAGS)
.F.L:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -listing $*.F
.F.opt:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -opt_report_level max -opt_report_phase all -opt_report_file $*.opt $*.F
.F.l:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c $(LIST) $*.F
.F.T:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -cif $*.F
.F.f:
	$(FC) $(CPPDEFS) $(FPPFLAGS) -EP $*.F > $*.f
.F.i:
	$(FC) $(CPPDEFS) $(FPPFLAGS) -P $*.F
.F.o:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c $*.F
.F.s:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -S $*.F
.F.x:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -o $*.x $*.F *.o $(LDFLAGS)
.F90.L:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -listing $*.F90
.F90.opt:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -opt_report_level max -opt_report_phase all -opt_report_file $*.opt $*.F90
.F90.l:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c $(LIST) $*.F90
.F90.T:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -cif $*.F90
.F90.f90:
	$(FC) $(CPPDEFS) $(FPPFLAGS) -EP $*.F90 > $*.f90
.F90.i90:
	$(FC) $(CPPDEFS) $(FPPFLAGS) -P $*.F90
.F90.o:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c $*.F90
.F90.s:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -S $*.F90
.F90.x:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -o $*.x $*.F90 *.o $(LDFLAGS)
"""
        else:
            # Copied from bin/mkmf.template.t90
            # TODO: Why from `mkmf.template.t90`? Copy bin/mkmf.template.nci.
            config["post"] = """
# you should never need to change any lines below.

# see the CF90 manual for more details on some of the file extensions
# discussed here.
# this makefile template recognizes fortran sourcefiles with extensions
# .f, .f90, .F, .F90. Given a sourcefile <file>.<ext>, where <ext> is one of
# the above, this provides a number of default actions:

# make <file>.T		create a CIF file
# make <file>.lst	create a compiler listing
# make <file>.o		create an object file
# make <file>.s		create an assembly listing
# make <file>.x		create an executable file, assuming standalone
#			source

# make <file>.i		create a preprocessed file (only for .F and .F90
#			extensions)

# make <file>.hpm	produce hpm output from <file>.x
# make <file>.proc	produce procstat output from <file>.x

# The macro TMPFILES is provided to slate files like the above for removal.

RM = rm -f
SHELL = /bin/csh
TMPFILES = .*.m *.T *.TT *.hpm *.i *.lst *.proc *.s

.SUFFIXES: .F .F90 .H .T .f .F90 .h .hpm .i .lst .proc .o .s .x

.f.T:
	$(FC) $(FFLAGS) -c -Ca $*.f
.f.lst:
	$(FC) $(FFLAGS) $(LIST) -c $*.f
.f.o:
	$(FC) $(FFLAGS) -c     $*.f
.f.s:
	$(FC) $(FFLAGS) -eS    $*.f
.f.x:
	$(FC) $(FFLAGS) $(LDFLAGS) -o $*.x $*.f
.f90.T:
	$(FC) $(FFLAGS) -c -Ca $*.f90
.f90.lst:
	$(FC) $(FFLAGS) $(LIST) -c $*.f90
.f90.o:
	$(FC) $(FFLAGS) -c     $*.f90
.f90.s:
	$(FC) $(FFLAGS) -c -eS $*.f90
.f90.x:
	$(FC) $(FFLAGS) $(LDFLAGS) -o $*.x $*.f90
.F.T:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c -Ca $*.F
.F.i:
	$(FC) $(CPPDEFS) $(CPPFLAGS) -eP $*.F
.F.lst:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) $(LIST) -c $*.F
.F.o:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c     $*.F
.F.s:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c -eS $*.F
.F.x:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) $(LDFLAGS) -o $*.x $*.F
.F90.T:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c -Ca $*.F90
.F90.i:
	$(FC) $(CPPDEFS) $(CPPFLAGS) -eP $*.F90
.F90.lst:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) $(LIST) -c $*.F90
.F90.o:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c     $*.F90
.F90.s:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c -eS $*.F90
.F90.x:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) $(LDFLAGS) -o $*.x $*.F90
.x.proc:
	procstat -R $*.proc $*.x
.x.hpm:
	hpm -r -o $*.hpm $*.x
"""

        fullconfig = config[pkg.compiler.name] + config["post"]
        print(fullconfig)
        with open(makeinc_path, "w") as makeinc:
            makeinc.write(fullconfig)

    def build(self, pkg, spec, prefix):

        # cd ${ACCESS_OM_DIR}/src/mom/exp
        # export mom_type=ACCESS-OM
        # ./MOM_compile.csh --type $mom_type --platform spack
        with working_dir(join_path(pkg.stage.source_path, "exp")):
            build = Executable("./MOM_compile.csh")

            if pkg.spec.satisfies("+restart_repro"):
                build.add_default_env("REPRO", "true")
                print("INFO: +restart_repro applied")

            if self.__version != "access-esm1.5":
                # The MOM5 commit d7ba13a3f364ce130b6ad0ba813f01832cada7a2
                # requires the --no_version switch to avoid git hashes being
                # embedded in the binary.
                build.add_default_arg("--no_version")
                if pkg.spec.satisfies("+optimisation_report"):
                    build.add_default_env("REPORT", "true")
                    print("INFO: +optimisation_report applied")

            build(
                "--type",
                self.__builds[self.__version],
                "--platform",
                self.__platform,
                "--no_environ"
            )

    def install(self, pkg, spec, prefix):

        mkdirp(prefix.bin)
        install(
            join_path(
                "exec",
                self.__platform,
                self.__builds[self.__version],
                "fms_" + self.__builds[self.__version] + ".x"
            ),
            prefix.bin
        )
        install(join_path("bin", "mppnccombine." + self.__platform), prefix.bin)

