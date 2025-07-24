# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py
# and https://github.com/coecms/access-esm-build-gadi
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack_repo.builtin.build_systems.generic import Package
from spack.package import *

class Um7(Package):
    """
    UM is a numerical weather prediction and climate modelling software package.
    Um7 is a package for UM vn7.3 for ACCESS ESM 1.5
    """

    homepage = "https://code.metoffice.gov.uk/trac/um"
    git = "https://github.com/ACCESS-NRI/UM7.git"

    # https://code.metoffice.gov.uk/trac/um/wiki/PastReleases
    version("access-esm1.6", branch="dev-access-esm1.6", preferred=True)
    version("access-esm1.5", branch="access-esm1.5")

    maintainers("penguian", "Whyborn")

    depends_on("fcm", type="build")
    depends_on("dummygrib", type=("build", "link"))
    depends_on("gcom4+mpi", type=("build", "link"))
    depends_on("openmpi", type=("build", "run"))
    depends_on("netcdf-fortran@4.5.2:", type=("build", "link"))
    depends_on("oasis3-mct", type=("build", "link"))

    # https://metomi.github.io/fcm/doc/user_guide/build.html
    variant(
        "full",
        default=True,
        description="Full (fresh) build. Disable for incremental build"
    )
    variant("optim", default="high", description="Optimization level",
            values=("high", "debug"), multi=False)

    with when("@access-esm1.6"):
        depends_on("cable library='access-esm1.6'", type=("build", "link"))

    phases = ["edit", "build", "install"]


    def setup_build_environment(self, env):
        """
        Set environment variables to their required values.
        """
        env.prepend_path("PATH", self.spec["fcm"].prefix.bin)
        oasis3_incs = [
                join_path(self.spec["oasis3-mct"].prefix.include, subdir)
                for subdir in ["psmile.MPI1", "mct"]]
        ideps = ["gcom4", "netcdf-fortran"]
        if self.spec.satisfies("@access-esm1.6"):
            ideps.append("cable")
        incs = [self.spec[d].prefix.include for d in ideps] + oasis3_incs
        for ipath in incs:
            env.prepend_path("CPATH", ipath)
        # The gcom4 library does not contain shared objects and
        # therefore must be statically linked.
        env.prepend_path("LIBRARY_PATH", self.spec["gcom4"].prefix.lib)


    # The path to the build directory.
    _bld_path = "ummodel_hg3"

    # The path to the build configuration.
    _bld_cfg_path = join_path(_bld_path, "cfg", "bld-hadgem3-spack.cfg")


    def _exe_name(self, optim_value):
        """
        Return the executable name, depending on optim_value.
        """
        if optim_value == "debug":
            return "um_hg3_dbg.exe"
        else:
            return "um_hg3.exe"


    def _get_linker_args(self, spec, name):
        """
        The reason for the explicit -rpath is:
        https://github.com/ACCESS-NRI/spack-packages/issues/14#issuecomment-1653651447
        """
        return " ".join(
                    [(spec[name].libs).ld_flags,
                    "-Wl,-rpath=" + join_path(spec[name].prefix, "lib")]
                   )


    def edit(self, spec, prefix):
        """
        Create an FCM configuration file based on
        ummodel_hg3/cfg/bld-dbg-hadgem3-C2.cfg and
        ummodel_hg3/cfg/bld-hadgem3-mct.cfg
        """

        ldeps = ["oasis3-mct", "netcdf-fortran", "dummygrib"]
        if self.spec.satisfies("@access-esm1.6"):
            ldeps.append("cable")
        libs = " ".join([self._get_linker_args(spec, d) for d in ldeps] + ["-lgcom"])

        opt_value = spec.variants["optim"].value
        EXE_NAME = self._exe_name(opt_value)
        CPPKEYS = (
            "C_LONG_LONG_INT=c_long_long_int MPP=mpp C_LOW_U=c_low_u "
            "FRL8=frl8 LINUX=linux BUFRD_IO=bufrd_io LITTLE_END=little_end "
            "LINUX_INTEL_COMPILER=linux_intel_compiler "
            "ACCESS=access OASIS3=oasis3 CONTROL=control REPROD=reprod "
            "MPP=mpp ATMOS=atmos GLOBAL=global A04_ALL=a04_all "
            "A01_3A=a01_3a A02_3A=a02_3a A03_8C=a03_8c A04_3D=a04_3d "
            "A05_4A=a05_4a A06_4A=a06_4a A08_7A=a08_7a A09_2A=a09_2a "
            "A10_2A=a10_2a A11_2A=a11_2a A12_2A=a12_2a A13_2A=a13_2a "
            "A14_1B=a14_1b A15_1A=a15_1a A16_1A=a16_1a A17_2B=a17_2b "
            "A18_0A=a18_0a A19_1A=a19_1a A25_0A=a25_0a A26_1A=a26_1a "
            "A30_1A=a30_1a A31_0A=a31_0a A32_1A=a32_1a A33_0A=a33_0a "
            "A34_0A=a34_0a A35_0A=a35_0a A38_0A=a38_0a A70_1B=a70_1b "
            "A71_1A=a71_1a C70_1A=c70_1a C72_0A=c72_0a C80_1A=c80_1a "
            "C82_1A=c82_1a C84_1A=c84_1a C92_2A=c92_2a C94_1A=c94_1a "
            "C95_2A=c95_2a C96_1C=c96_1c C97_3A=c97_3a "
            "CABLE_17TILES=cable_17tiles "
            "CABLE_SOIL_LAYERS=cable_soil_layers "
            "TIMER=timer")
        FFLAGS = "-ftz -what -fno-alias -stack-temps -safe-cray-ptr"
        if opt_value == "debug":
            FO = "-O0"
            FTRACEBACK = "-traceback"
            FDEBUG = "-debug all"
            FG = "-g"
            FARCH = ""
            FOBLANK = "-O0"
        else:
            FO = "-O2"
            FTRACEBACK = ""
            FDEBUG = ""
            FG = ""
            FARCH = "-xCORE-AVX512"
            FOBLANK = ""

        # FCM tries to find all instances of USE and include them as
        # source code, except things explicitly excluded by excl_deps.
        # This means when using CABLE as a library, everything USEd
        # by the coupled infrastructure, which still lives in UM7,
        # must be explicitly included. Leave the default of an empty
        # string for older versions of UM7 which include CABLE as
        # source code.
        CABLE_excl_deps = ""
        if self.spec.satisfies("@access-esm1.6"):
            CABLE_excl_deps = """
excl_dep                                           USE::cable_def_types_mod
excl_dep                                           USE::cbl_masks_mod
excl_dep                                           USE::cable_other_constants_mod
excl_dep                                           USE::cable_math_constants_mod
excl_dep                                           USE::cable_phys_constants_mod
excl_dep                                           USE::cable_soil_params_mod
excl_dep                                           USE::cable_common_module
excl_dep                                           USE::cbl_init_radiation_module
excl_dep                                           USE::grid_constants_mod_cbl
excl_dep                                           USE::cable_surface_types_mod
excl_dep                                           USE::cable_soil_type_mod
excl_dep                                           USE::cable_veg_type_mod
excl_dep                                           USE::cable_pft_params_mod
excl_dep                                           USE::cbl_albedo_mod
excl_dep                                           USE::cbl_soil_snow_main_module
excl_dep                                           USE::cable_soil_snow_type_mod
excl_dep                                           USE::cbl_lai_canopy_height_mod
excl_dep                                           USE::cable_carbon_module
excl_dep                                           USE::snow_aging_mod
excl_dep                                           USE::cable_roughness_module
excl_dep                                           USE::cable_air_module
excl_dep                                           USE::cable_canopy_module
excl_dep                                           USE::cable_canopy_type_mod
excl_dep                                           USE::casadimension
excl_dep                                           USE::casa_inout_module
excl_dep                                           USE::casa_readbiome_module
excl_dep                                           USE::cable_init_wetfac_mod
excl_dep                                           USE::casavariable
excl_dep                                           USE::casaparm
excl_dep                                           USE::phenvariable
excl_dep                                           USE::feedback_mod
excl_dep                                           USE::bgcdriver_mod
excl_dep                                           USE::sumcflux_mod
excl_dep                                           USE::POP_TYPES
excl_dep                                           USE::cable_runtime_opts_mod
excl_dep                                           USE::landuse_mod
            """

        config = f"""
# ------------------------------------------------------------------------------
# File header
# ------------------------------------------------------------------------------

CFG::TYPE                                          bld
CFG::REVISION                                      1.0

USE                                                $HERE/../../umbase_hg3

# ------------------------------------------------------------------------------
# Destination
# ------------------------------------------------------------------------------

DEST                                               $HERE/..

# ------------------------------------------------------------------------------
# Build declarations
# ------------------------------------------------------------------------------

blockdata                                          blkdata.o
excl_dep                                           USE::NetCDF
excl_dep                                           INC::netcdf.inc
excl_dep                                           INC::mpif.h
excl_dep                                           USE::mpl
excl_dep                                           USE::mod_prism
excl_dep                                           USE::mod_prism_proto
excl_dep                                           USE::mod_prism_grids_writing
excl_dep                                           USE::mod_prism_def_partition_proto
excl_dep                                           USE::mod_prism_put_proto
excl_dep                                           USE::mod_prism_get_proto
{CABLE_excl_deps}
excl_dep::script                                   EXE
exe_dep                                            portio2a.o pio_data_conv.o pio_io_timer.o
exe_name::flumeMain                                {EXE_NAME}
pp                                                 1
target                                             {EXE_NAME}
tool::ar                                           ar
tool::cc                                           mpicc
tool::cflags                                       {FO} -g {FTRACEBACK} {FDEBUG} {FARCH} -fp-model precise
tool::cpp                                          cpp
tool::cppflags
tool::cppkeys                                      {CPPKEYS}
tool::fc                                           mpif90
tool::fflags                                       {FO}  -g   -traceback  {FDEBUG} -i8 -r8      -fp-model precise {FFLAGS}
tool::fflags::control::coupling::dump_received     {FO} {FG} {FTRACEBACK} {FDEBUG}         -mp1 -fp-model strict  {FFLAGS}
tool::fflags::control::coupling::dump_sent         {FO} {FG} {FTRACEBACK} {FDEBUG}         -mp1 -fp-model strict  {FFLAGS}
tool::fflags::control::coupling::oasis3_atmos_init {FO} {FG} {FTRACEBACK} {FDEBUG} -i4 -r8 -mp1 -fp-model strict  {FFLAGS}
tool::fflags::control::top_level::atm_step         -O0   -g  {FTRACEBACK} {FDEBUG} -i8 -r8 -mp1 -fp-model strict  {FFLAGS}
tool::fflags::control::top_level::set_atm_pointers -O0   -g   -traceback  {FDEBUG} -i8 -r8      -fp-model strict -ftz -std95
tool::fflags::control::top_level::u_model          -O0   -g  {FTRACEBACK} {FDEBUG} -i8 -r8 -mp1 -fp-model strict  {FFLAGS}
tool::fpp                                          cpp
tool::fppflags                                     -P -traditional
tool::fppkeys                                      {CPPKEYS}

tool::geninterface                                 none
tool::ld                                           mpif90
tool::ldflags                                      {FOBLANK} -g -traceback {FDEBUG} -static-intel {libs}
        """
        with open(self._bld_cfg_path, "w") as bld_cfg_file:
            bld_cfg_file.write(config)


    def build(self, spec, prefix):
        """
        Use FCM to build the executable.
        """
        fcm = which("fcm")
        if spec.satisfies("+full"):
            fcm("build", "-f", "-j", "4", self._bld_cfg_path)
        else:
            fcm("build", "-j", "4", self._bld_cfg_path)


    def install(self, spec, prefix):
        """
        Install the executable into the prefix.bin directory.
        The executable name depends on the "optim" value.
        """
        um_exe = self._exe_name(spec.variants["optim"].value)
        mkdirp(prefix.bin)
        install(
            join_path(self._bld_path, "bin", um_exe),
            join_path(prefix.bin, um_exe))
