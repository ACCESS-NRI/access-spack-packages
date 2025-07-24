# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *

# supported model configurations
KNOWN_CONF = (
    "MOM6",
    "CICE6",
    "WW3",
    "MOM6-WW3",
    "MOM6-CICE6",
    "CICE6-WW3",
    "MOM6-CICE6-WW3",
)

# tag,commit pairs for releases in access3-share git repository
ACCESS3_VERSIONS = {
    "2025.08.000": "f2f35ce5915e82a83899b69560d826deab53b668",
    "2025.03.1": "d28d8b3bb2d490920cabd48a87663de017ca6a18",
    "2025.03.0": "d61a88ac937092f6f8ee1215716e2d6a750161e3"
}


class Access3(CMakePackage):
    """Executable build for ACCESS version 3 climate models. The exectuable is
    defined in Community Mediator for Earth Prediction Systems (CMEPS).
    Currently implemented for ACCESS-OM3, and in the future may support
    ACCESS-CM3 and ACCESS-ESM3. This is a companion package to Access3Share
    which builds the shared libraries."""

    homepage = "https://github.com/ACCESS-NRI/access3-share"
    git = "https://github.com/ACCESS-NRI/access3-share"
    submodules = True
    maintainers("anton-seaice", "harshula", "micaeljtoliveira")
    license("Apache-2.0", checked_by="anton-seaice")

    version("stable", branch="main", preferred=True)
    for tag, commit in ACCESS3_VERSIONS.items():
        version(tag, tag=tag, commit=commit)
        # access3-share uses the same git repository as access3:
        depends_on(f"access3-share@{tag}", when=f"@{tag}")

    variant(
        "configurations",
        values=(*KNOWN_CONF, 'none'),
        default='none',
        multi=True,
        description=(
            "ACCESS-OM3 configurations to build. When a model component "
            "is not included in a configuration, that component is replaced by "
            "a CDEPS data component."
        ),
        sticky=True  # force concretizer to not pick alternative variants
    )

    # force user to supply a build combination
    conflicts(
        "configurations=none",
        msg=f"A configurations variant must be set, can be one or many of {KNOWN_CONF}"
    )

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("access3-share")
    depends_on("esmf@8.7.0:")

    for conf in KNOWN_CONF:
        if "CICE6" in conf:
            depends_on("access-cice@CICE6.6.0-1: +access3", when=f"configurations={conf}")
        if "MOM6" in conf:
            depends_on("access-mom6@2025.02.000: +access3", when=f"configurations={conf}")
        if "WW3" in conf:
            depends_on("access-ww3@2025.03.0: +access3", when=f"configurations={conf}")

    def cmake_args(self):
        # make configurations a cmake argument
        buildConf = ";".join(self.spec.variants["configurations"].value)

        args = [
            self.define("BuildConfigurations", buildConf),
            self.define("ACCESS3_LIB_INSTALL", False),
        ]

        return args
