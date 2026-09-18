# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *
from spack_repo.access.nri.packages.access3.package import ACCESS3_VERSIONS

class Access3Share(CMakePackage):
    """Shared coupler/mediator libraries used by the ACCESS version 3 climate
    models. This package includes the Community Mediator for Earth Prediction
    Systems (CMEPS) and Community Data models for Earth Prediction Systems
    (CDEPS) as used in ACCESS-OM3 (and the future ACCESS-CM3 and ACCESS-ESM3 etc
    ). See Access3 package to produce executable programs."""

    homepage = "https://github.com/ACCESS-NRI/access3-share"
    git = "https://github.com/ACCESS-NRI/access3-share"
    submodules = True
    maintainers("anton-seaice", "harshula", "micaeljtoliveira")
    license("Apache-2.0", checked_by="anton-seaice")

    version("stable", branch="main", preferred=True)
    # access3-share uses the same git repository as access3
    for tag, commit in ACCESS3_VERSIONS.items():
        version(tag, tag=tag, commit=commit)

    variant("openmp", default=False, sticky=True, description="Enable OpenMP")

    depends_on("c", type="build")
    depends_on("fortran", type="build")

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")
    depends_on("esmf@8.7.0:")
    depends_on("esmf fflags='-fp-model precise'", when="%intel")  # for consistency with access-om3-nuopc builds, e.g. https://github.com/ACCESS-NRI/spack-packages/blob/e2bdb46e56af8ac14183e7ed25da9235486c973a/packages/access-om3-nuopc/package.py#L58
    depends_on("fortranxml@4.1.2:")

    depends_on("parallelio@2.5.3:")
    depends_on(("parallelio "
                "fflags='-qno-opt-dynamic-align -convert big_endian -assume byterecl -ftz -traceback -assume realloc_lhs -fp-model precise' "
                "cflags='-qno-opt-dynamic-align -fp-model precise -std=gnu99'"),
                when="%intel")  # consistency with access-om3-nuopc builds, e.g. https://github.com/ACCESS-NRI/spack-packages/blob/e2bdb46e56af8ac14183e7ed25da9235486c973a/packages/access-om3-nuopc/package.py#L65

    # Mediator restart I/O containing two changes - i) Drops the per-FieldBundle
    # pio_syncfile (a collective H5Fflush of a still-growing multi-GB file, ~14 '
    # times per restart), and ii) optionally stops writing duplicate
    # <pre>_lon / <pre>_lat copies into the restart file. Default is set to "true" -
    # which preserves the old behaviour of writing out the duplicate coordinates.
    # Setting  write_restart_coords = .false. (under MED_attributes:: in nuopc.runconfig)
    # will stop writing the duplicate coordinates, but naturally, the restart file
    # contents will be different.
    # Applies to the bundled CMEPS submodule only. Verified against the CMEPS
    # commits pinned by @2025.08.000 through @2026.03.002; @2025.03.x pin a CMEPS
    # whose med_phases_restart_mod.F90 predates the context hunk 1 needs.
    patch("cmeps-mediator-restart-io.patch", working_dir="CMEPS/CMEPS", when="@2025.08.000:")
    patch("cmeps-mediator-restart-io.patch", working_dir="CMEPS/CMEPS", when="@stable")

    # DIAGNOSTIC ONLY -- ESMF trace regions inside the mediator restart write, so
    # ESMF_Profile.summary breaks med_phases_restart_write (288-336 s, 34-39% of an
    # ACCESS-OM3 8 km 1-day run) into file open, variable definition, per-FieldBundle
    # decomposition build, the pio_write_darray loop, coordinate writes, freedecomp
    # and the final pio_closefile. Purely additive: nothing but
    # ESMF_TraceRegionEnter/Exit calls and comments, so it cannot change results.
    # Remove once the numbers have said whether the pauses between bursts of file
    # growth are pio_initdecomp, the per-bundle ESMF_LogWrite, or a deferred flush.
    # MUST be listed AFTER cmeps-mediator-restart-io.patch: it applies on top of it.
    patch("cmeps-restart-timers.patch", working_dir="CMEPS/CMEPS", when="@2025.08.000:")
    patch("cmeps-restart-timers.patch", working_dir="CMEPS/CMEPS", when="@stable")

    # Cache PIO decompositions instead of calling pio_initdecomp once per
    # FieldBundle. Measured with the trace regions above: pio_initdecomp was 274.4 s
    # of a 326.6 s mediator restart write on ACCESS-OM3 8 km (84%, 22.9 s per bundle)
    # while the pio_write_darray loop beside it was 0.76 s. The 12 bundles share one
    # ESMFmesh, so they collapse to one decomposition. Expected ~-266 s, taking the
    # restart write to roughly 61 s.
    # MUST be listed AFTER cmeps-restart-timers.patch. Narrower version range than
    # the patches above: @2026.03.000 and earlier pin a CMEPS whose module-level
    # "use pio" block differs.
    patch("cmeps-iodesc-cache.patch", working_dir="CMEPS/CMEPS", when="@2026.03.001:")
    patch("cmeps-iodesc-cache.patch", working_dir="CMEPS/CMEPS", when="@stable")


    # DIAGNOSTIC ONLY -- ESMF trace regions inside the CDEPS data-model stream
    # initialisation, so ESMF_Profile.summary breaks datm_strdata_init (114.8 s of a
    # 866.7 s ACCESS-OM3 8 km 1-day run) into model-mesh read, xml parse, model
    # domain, and per-stream mesh create / field bundle / regrid store. Purely
    # additive: nothing but ESMF_TraceRegionEnter/Exit calls and comments, so it
    # cannot change results. Remove once the per-stream Counts have answered
    # whether caching the stream meshes and route handles is worth writing.
    # Verified against the CDEPS commits pinned by @2026.03.000 through
    # @2026.03.002; @2025.08.000 and earlier pin a CDEPS where 2 of 7 hunks miss.
    patch("cdeps-strdata-timers.patch", working_dir="CDEPS/CDEPS", when="@2026.03.000:")
    patch("cdeps-strdata-timers.patch", working_dir="CDEPS/CDEPS", when="@stable")

    # Reuse identical stream route handles instead of calling ESMF_FieldRegridStore
    # once per stream. That call generates interpolation weights and measured 94.9%
    # of datm_strdata_init (112.5 s of 118.6 s, 12.5 s x 9 streams) on ACCESS-OM3
    # 8 km, where all 9 DATM streams share one source mesh, one model mesh and two
    # mapalgo values -- so two handles are needed and nine were built. Expected
    # saving ~89 s, about 10% of a 1-day benchmark.
    # MUST be listed AFTER cdeps-strdata-timers.patch: it applies on top of it, and
    # the trace regions are how the change is verified (strdata_regridstore Count
    # falls from the stream count to the number of distinct handles).
    patch("cdeps-routehandle-cache.patch", working_dir="CDEPS/CDEPS", when="@2026.03.000:")
    patch("cdeps-routehandle-cache.patch", working_dir="CDEPS/CDEPS", when="@stable")


    def cmake_args(self):
        args = [
            self.define("ACCESS3_LIB_INSTALL", True),
            self.define_from_variant("OPENMP", "openmp"),
        ]

        return args
