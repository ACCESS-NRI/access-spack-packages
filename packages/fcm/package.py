from spack.package import *


class Fcm(Package):
    """
    FCM is a build system for Fortran programs
    """

    homepage = "https://github.com/metomi/fcm"

    maintainers("scottwales", "penguian")

    version(
        "2021.05.0",
        sha256="b4178b488470aa391f29b46d19bd6395ace42ea06cb9678cabbd4604b46f56cd",
    )

    variant("site", default="none", description="Site to use for keyword configuration",
        values=("none", "nci-gadi"), multi=False)

    def url_for_version(self, version):
        return "https://github.com/metomi/fcm/archive/refs/tags/{0}.tar.gz".format(version)

    def install(self, spec, prefix):
        install_tree(".", prefix)
        site = spec.variants["site"].value
        if site != "none":
            mkdirp(prefix.etc)
            install(
                join_path(self.package_dir, "etc", site, "keyword.cfg"),
                join_path(prefix.etc, "fcm"))
