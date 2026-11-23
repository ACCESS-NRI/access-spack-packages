# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
 
from spack_repo.builtin.build_systems.autotools import AutotoolsPackage
 
from spack.package import *
 
 
class Ems(AutotoolsPackage):
    """CSIRO Environmental Modelling Suite (EMS): the SHOC (structured) and
    COMPAS (unstructured) hydrodynamic models, with sediment transport,
    biogeochemistry, waves and tracer-statistics libraries."""
 
    homepage = "https://research.csiro.au/cem/software/ems/"
    git = "https://github.com/csiro-coasts/EMS.git"

    # Custom CSIRO license. Free and open to use with conditions, see LICENSE.md 
    # in the source tree for details.
    license("LicenseRef-CSIRO-EMS", checked_by="aidan")

    maintainers("aidan", "helenmacdonald", "frizwi")
 
    version("master", branch="master")
    version("1.5.3", tag="v1.5.3", commit="a0f8eb016cebb64470c01407d1362d5ecba61343")
 
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("netcdf-c")
 
    # The configure script lives in conf/ but must be run from the source root.
    configure_directory = "conf"
 
    @property
    def build_directory(self):
        return self.stage.source_path
 
    # The top-level makefile builds sub-directories sequentially.
    parallel = False
 
    def setup_build_environment(self, env):
        env.set("NETCDF_ROOT", self.spec["netcdf-c"].prefix)
 
    def install(self, spec, prefix):
        # Upstream "make install" is broken, so install the executables directly.
        mkdirp(prefix.bin)
        mkdirp(prefix.lib)
        install("model/hd/shoc", prefix.bin)
        install("model/hd-us/compas", prefix.bin)
        # COMPAS links against the bundled JIGSAW shared library.
        install("ext/jigsaw/lib/libjigsaw64r.so", prefix.lib)