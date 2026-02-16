from spack.package import *


class Gcom(Package):
    """
    GCOM is a wrapper around multiprocessing libraries such as MPI
    """

    homepage = "https://code.metoffice.gov.uk/trac/gcom"
    # svn = "file:///g/data/ki32/mosrs/gcom/main/trunk"
    git = "https://github.com/ACCESS-NRI/gcom"
    maintainers("scottwales", "paulleopardi")

    version("7.8", tag="vn7.8", "65c857cc3201833360ff62b285e49082378dae42")
    version("7.9", tag="vn7.9", "6319ae016dcadc192842a06178f3dbd21a8af64f")
    version("8.0", tag="vn8.0", "5a122e9e2147c9a7486a00b9588356eb65324af9")
    version("8.1", tag="vn8.1", "e061e2787bd643d9a65679f153fb8e3ffd9d3186")
    version("8.2", tag="vn8.2", "fd143bb38e21fe03c7150c0754852c80e15df3d4")
    version("8.3", tag="vn8.3", "b7b890a181d8e31e4e80b731b9f8ad9a6e1a8bed")
    version("8.4", tag="vn8.4", "f4fa92eb4af4f1e4cf9d608b441e3c96f77b6a6d")

    # See 'fcm kp fcm:gcom.xm' for release versions
    # version("7.8", revision=1147)
    # version("7.9", revision=1166)
    # version("8.0", revision=1181)
    # version("8.1", revision=1215)
    # version("8.2", revision=1251)
    # version("8.3", revision=1288)
    # version("8.4", revision=1386)

    variant("mpi", default=True, description="Build with MPI")

    depends_on("fcm", type="build")
    depends_on("mpi", when="+mpi", type=("build", "link", "run"))
    # For the default MPI version for NCI, see (e.g.)
    # https://code.metoffice.gov.uk/trac/gcom/browser/main/trunk/rose-stem/site/nci/suite.rc
    # For cherry picking virtual dependencies, see
    # https://github.com/spack/spack/releases/tag/v0.21.0 Feature 4
    depends_on("openmpi@4.1.3:", when="+mpi^[virtuals=mpi] openmpi", type=("build", "link", "run"))

    def install(self, spec, prefix):
        fcm = which("fcm")

        # Set up variables used by fcm-make/gcom.cfg
        env["ACTION"] = "preprocess build"
        env["GCOM_SOURCE"] = "$HERE/.."
        env["DATE"] = ""
        env["REMOTE_ACTION"] = ""
        env["ROSE_TASK_MIRROR_TARGET"] = "localhost"

        # Decide on the build variant
        if spec.satisfies("%intel"):
            mach_c = "ifort"
        elif spec.satisfies("%gcc"):
            mach_c = "gfortran"
        else:
            raise NotImplentedError("Unknown compiler")
        if "+mpi" in spec:
            mach_m = "mpp"
        else:
            mach_m = "serial"

        env["GCOM_MACHINE"] = f"nci_gadi_{mach_c}_{mach_m}"

        # Do the build with fcm
        fcm("make", "-f", "fcm-make/gcom.cfg")

        # Install the library
        mkdirp(prefix.lib)
        install("build/lib/libgcom.a", prefix.lib + "/libgcom.a")
        install_tree("build/include", prefix.include)
