# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright 2023 Angus Gibson
# Copyright 2025 Justin Kin Jun Hew - Wrappers, Examples, Versioning, AD-enabled flavour
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.autotools import AutotoolsPackage
from spack.package import *
import zipfile
import os
import time

ZIPFILE_MIN_DATE = (1980, 1, 1, 0, 0, 0)

class Issm(AutotoolsPackage):
    """Ice-sheet and Sea-Level System Model.

    This recipe supports two distinct build flavours:

    * **Classic** (default) - links against PETSc for linear algebra.
    * **Automatic Differentiation** (+ad) - uses CoDiPack + MediPack and
      **excludes PETSc** (ISSM's AD implementation is not PETSc-compatible).
    """

    homepage = "https://issm.jpl.nasa.gov/"
    git = "https://github.com/ACCESS-NRI/ISSM.git"

    maintainers("justinh2002", "lawrenceabird")

    # --------------------------------------------------------------------
    # Versions
    # --------------------------------------------------------------------
    version("upstream", branch="main", git="https://github.com/ISSMteam/ISSM.git")
    version("main", branch="main")
    version("access-release", branch="access-release")
    version("access-development", branch="access-development")

    version("2026.04.16", tag="2026.04.16", preferred=True)

    # --------------------------------------------------------------------
    # Variants
    # --------------------------------------------------------------------
    variant(
        "wrappers",
        default=False,
        description="Enable building ISSM Python/C wrappers",
    )

    variant(
        "examples",
        default=False,
        description="Install the examples tree under <prefix>/examples",
    )

    variant(
        "ad",
        default=False,
        description="Build with CoDiPack automatic differentiation (drops PETSc)",
    )

    variant(
        "openmp",
        default=True,
        description="Propagate OpenMP flags so threaded deps link cleanly",
    )

    variant(
        "production",
        default=True,
        description="Build ISSM in production mode with optimized PETSc and release flags",
    )

    variant(
        "py-tools",
        default=False,
        description="Install ISSM python files under <prefix>/python-tools",
    )

    # --------------------------------------------------------------------
    # Dependencies
    # --------------------------------------------------------------------
    # Build-time tools
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("fortran", type="build")
    depends_on("autoconf", type="build")
    depends_on("automake", type="build")
    depends_on("libtool", type="build")
    depends_on("m4", type="build")

    # Core build + runtime deps
    depends_on("mpi")

    # Conditional dependencies
    # --------------------------------------------------------------------
    # When building "default" ISSM, use Petsc (with metis [incl. parmetis], mumps, and scalapack variants)
    with when("~ad"):
        depends_on("petsc~examples+metis+mumps+scalapack", when="~production")
        depends_on("petsc~debug~examples+metis+mumps+scalapack", when="+production")

    # When building with AD support, do not use Petsc; instead use CoDiPack + MeDiPack.
    with when("+ad"):
        depends_on("codipack")
        depends_on("medipack")

    # When building with Python wrappers, need access-triangle, Python, and NumPy
    with when("+wrappers"):
        depends_on("access-triangle")
        depends_on("python", type=("build", "run"))
        depends_on("py-numpy", type=("build", "run"))

    # Unconditional dependencies
    # --------------------------------------------------------------------
    depends_on("metis")
    depends_on("parmetis")
    depends_on("access-mumps~openmp", when="~openmp")
    depends_on("access-mumps+openmp", when="+openmp")
    depends_on("scalapack")
    depends_on("m1qn3")

    # --------------------------------------------------------------------
    # Conflicts
    # --------------------------------------------------------------------

    # GCC 14 breaks on several C++17 constructs used in ISSM
    conflicts("%gcc@14:", msg="ISSM cannot be built with GCC versions above 13")

    # +wrappers requires +py-tools to access the wrappers
    conflicts("+wrappers", when="~py-tools", msg="The +wrappers variant requires +py-tools")

    # +py-tools requires +wrappers for full Python functionality
    conflicts("+py-tools", when="~wrappers", msg="The +py-tools variant requires +wrappers for full functionality")

    # --------------------------------------------------------------------
    # Helper functions
    # --------------------------------------------------------------------
    def url_for_version(self, version):
        """Tarball URL for Spack-generated versions."""
        if version == Version("upstream"):
            return "https://github.com/ISSMteam/ISSM/archive/refs/heads/main.tar.gz"
        return f"https://github.com/ACCESS-NRI/ISSM/archive/refs/heads/{version}.tar.gz"

    # --------------------------------------------------------------------
    # Build environment - inject AD and/or OpenMP compiler flags when needed
    # --------------------------------------------------------------------
    def setup_build_environment(self, env):
        # OpenMP support
        if "+openmp" in self.spec:
            for var in ("CFLAGS", "CXXFLAGS", "FFLAGS", "LDFLAGS"):
                env.append_flags(var, self.compiler.openmp_flag)

        # Production build: optimized release flags
        if "+production" in self.spec:
            for var in ("CFLAGS", "CXXFLAGS", "FFLAGS"):
                env.append_flags(var, "-O2 -DNDEBUG")
            if self.spec.satisfies("%intel") or self.spec.satisfies("%oneapi"):
                for var in ("CFLAGS", "CXXFLAGS", "FFLAGS"):
                    env.append_flags(var, "-fp-model precise")

        # Automatic Differentiation extras
        if "+ad" in self.spec:
            # CoDiPack's performance tips: force inlining & keep full symbols
            env.append_flags(
                "CXXFLAGS",
                f"-g -O3 -fPIC {self.compiler.cxx11_flag} -DCODI_ForcedInlines",  # https://issm.ess.uci.edu/trac/issm/wiki/totten#InstallingISSMwithCoDiPackAD
            )

    # --------------------------------------------------------------------
    # Autoreconf hook
    # --------------------------------------------------------------------
    def autoreconf(self, spec, prefix):
        autoreconf("--install", "--verbose", "--force")

    # --------------------------------------------------------------------
    # Configure phase - construct ./configure arguments
    # --------------------------------------------------------------------
    def configure_args(self):
        args = [
            "--enable-shared",
            "--without-kriging",
            "--without-Love",
        ]

        if "+production" in self.spec:
            args += [
                "--disable-debugging",
                "--enable-development",
            ]
        else:
            args += [
                "--enable-debugging",
                "--enable-development",
            ]

        # Linear-algebra backend
        if "+ad" in self.spec:
            # AD build: *exclude* PETSc and point at CoDiPack/MediPack
            args += [
                f"--with-codipack-dir={self.spec['codipack'].prefix}",
                f"--with-medipack-dir={self.spec['medipack'].prefix}",
            ]
        else:
            # Classic build with PETSc
            args += [
                f"--with-petsc-dir={self.spec['petsc'].prefix}",
            ]
        args.append(f"--with-parmetis-dir={self.spec['parmetis'].prefix}")
        args.append(f"--with-metis-dir={self.spec['metis'].prefix}")
        args.append(f"--with-mumps-dir={self.spec['access-mumps'].prefix}")

        # Optimiser
        args.append(f"--with-m1qn3-dir={self.spec['m1qn3'].prefix.lib}")
        args.append(f"--with-scalapack-dir={self.spec['scalapack'].prefix}")

        # MPI compilers & headers
        mpi = self.spec["mpi"]
        args += [
            f"--with-mpi-include={mpi.prefix.include}",
            f"CC={mpi.mpicc}",
            f"CXX={mpi.mpicxx}",
            f"FC={mpi.mpifc}",
            f"F77={mpi.mpif77}",
        ]

        # Optional wrappers
        if "+wrappers" in self.spec:
            args.append("--with-wrappers=yes")
            args.append(f"--with-triangle-dir={self.spec['access-triangle'].prefix}")

            py_ver = self.spec["python"].version.up_to(2)
            py_pref = self.spec["python"].prefix
            np_pref = self.spec["py-numpy"].prefix
            np_inc = join_path(np_pref, "lib", f"python{py_ver}", "site-packages", "numpy")

            args += [
                f"--with-python-version={py_ver}",
                f"--with-python-dir={py_pref}",
                f"--with-python-numpy-dir={np_inc}",
            ]
        else:
            args.append("--with-wrappers=no")

        return args

    # --------------------------------------------------------------------
    # Install phase - delegate to standard make install & copy examples
    # --------------------------------------------------------------------
    def install(self, spec, prefix):
        make("install", parallel=False)

        # Optionally install examples directory
        if "+examples" in self.spec:
            examples_src = join_path(self.stage.source_path, "examples")
            examples_dst = join_path(prefix, "examples")
            install_tree(examples_src, examples_dst)

        # Optionally install Python (.py) files as a zip archive
        if "+py-tools" in self.spec:
            py_src = join_path(self.stage.source_path, "src", "m")
            py_dst = join_path(prefix, "python-tools.zip")

            # Recursively copy all .py files from src/m to python-tools.zip
            # Exclude contrib directory which contains working files
            exclude_dirs = {'contrib'}

            # Empty list to hold paths of .py files
            py_files = []

            # Walk through the directory tree
            for root, dirs, files in os.walk(py_src):

                # Split root into path parts (to allow direct exclusion of exclude_dirs)
                parts = os.path.normpath(root).split(os.sep)

                # Skip excluded directories
                if any(excl in parts for excl in exclude_dirs):
                    continue

                # Iterate over files in the current directory and collect .py files
                for file in files:
                    if file.endswith('.py'):
                        py_files.append(join_path(root, file))

            # Create the ZIP archive
            with zipfile.ZipFile(py_dst, "w", zipfile.ZIP_DEFLATED) as zf:
                for src_path in py_files:
                    # Use only the filename inside the archive
                    arcname = src_path.split("/")[-1]

                    zinfo = self._clamped_mtime(src_path, arcname, zf)

                    with open(src_path, "rb") as f:
                        zf.writestr(zinfo, f.read())

    def _clamped_mtime(self, file_path: str, archive_name: str, zip_file: zipfile.ZipFile) -> zipfile.ZipInfo:
        # Since some sources during building are erroneously using unix epoch mtime (which errors out in
        # python 3.6s implementation of zipfile when the mtime is before 1980),
        # we clamp it to a supported date (1/1/1980).
        stats = os.stat(file_path)
        mtime = stats.st_mtime
        mode = stats.st_mode

        # This converts the unix-style seconds since epoch to a zipfile-understandable struct of (year, month, day, hour, min, sec)
        mtime_date = time.localtime(mtime)[:6]
        clamped_mtime_date = max(mtime_date, ZIPFILE_MIN_DATE)

        zinfo = zipfile.ZipInfo(archive_name, clamped_mtime_date)

        # Since we're setting the zipinfo manually, we need to set some other aspects...
        zinfo.compress_type = zip_file.compression
        # mode is both file type and perms. We only want the perms (the low 16 bits).
        # zipfile expects unix perms to be set in the upper 16 bits, so we shift them up by 16.
        zinfo.external_attr = (mode & 0xFFFF) << 16

        return zinfo

    # --------------------------------------------------------------------
    # Run environment - set ISSM_DIR and PYTHONPATH
    # --------------------------------------------------------------------
    def setup_run_environment(self, env):
        """Set ISSM_DIR to the install root."""

        # Get the prefix path (install root)
        issm_dir = self.prefix

        # Set environment variable
        env.set('ISSM_DIR', issm_dir)

        # Add ISSM python files (and shared libraries) to PYTHONPATH if +py-tools
        if "+py-tools" in self.spec:
            env.prepend_path("PYTHONPATH", join_path(self.prefix, "python-tools.zip"))
            env.prepend_path("PYTHONPATH", join_path(self.prefix, "lib"))
