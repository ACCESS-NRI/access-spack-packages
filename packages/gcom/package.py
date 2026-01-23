from spack.package import *


class Gcom(Package):
    """
    GCOM is a wrapper around multiprocessing libraries such as MPI
    """

    homepage = "https://code.metoffice.gov.uk/trac/gcom"

    maintainers("scottwales", "paulleopardi")

    version("7.8", revision=1443, svn= "file:///g/data/ki32/mosrs/gcom/main/branches/dev/martindix/vn7.8_nci_intel_oneapi")
    version("7.9", revision=1444, svn= "file:///g/data/ki32/mosrs/gcom/main/branches/dev/martindix/vn7.9_nci_intel_oneapi")
    version("8.0", revision=1445, svn= "file:///g/data/ki32/mosrs/gcom/main/branches/dev/martindix/vn8.0_nci_intel_oneapi")
    version("8.1", revision=1446, svn= "file:///g/data/ki32/mosrs/gcom/main/branches/dev/martindix/vn8.1.nci_intel_oneapi")
    version("8.2", revision=1447, svn= "file:///g/data/ki32/mosrs/gcom/main/branches/dev/martindix/vn8.2_nci_intel_oneapi")
    version("8.3", revision=1448, svn= "file:///g/data/ki32/mosrs/gcom/main/branches/dev/martindix/vn8.3_nci_intel_oneapi")
    version("8.4", revision=1436, svn= "file:///g/data/ki32/mosrs/gcom/main/branches/dev/martindix/vn8.4_nci_intel_oneapi")

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
        elif spec.satisfies("%oneapi"):
           mach_c = "ifx"
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
