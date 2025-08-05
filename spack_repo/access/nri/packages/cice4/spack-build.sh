#! /bin/csh -f

# Script based on packages/cice5/spack-build.sh
# and https://github.com/ACCESS-NRI/cice4/blob/access-esm1.5/bld/build.sh
# and https://github.com/ACCESS-NRI/cice4/blob/access-esm1.5/compile/comp_access-cm_cice.RJ.nP-mct

set echo on

if ( $#argv < 4 ) then
  echo '*** Please issue the command like ***'
  echo '> ./bld/build.sh <driver> <grid> <blocks> <ntask> [<debug>]'
  echo 'e.g. bld/build.sh access 360x300 12x1 12'
  echo 'driver: which driver to use.'
  echo 'resolution: grid resolution longitude by latitude.'
  echo 'blocks: grid split into the number of blocks longitude by latitude.'
  echo 'ntask: number of tasks.'
  echo 'debug: if this is a unit testing or debug build. Valid options are \'debug\' or \'unit_testing\''
  exit
else
  set driver = $1
  set resolution = $2
  set blocks = $3
  set ntask = $4
  set debug = $5
endif

# Location of this model
setenv SPACKDIR $cwd:h
setenv SRCDIR $SPACKDIR/spack-src
setenv CBLD   $SRCDIR/bld

if ($debug == 'debug') then
    setenv DEBUG yes
endif
if ($debug == 'unit_testing') then
    setenv DEBUG yes
    setenv UNIT_TESTING yes
endif

### Specialty code
setenv USE_ESMF no        # set to yes for ESMF runs
setenv CAM_ICE  no        # set to yes for CAM runs (single column)
setenv SHRDIR   csm_share # location of CCSM shared code
setenv NETCDF   yes       # set to no if netcdf library is unavailable
setenv DITTO    no        # reproducible diagnostics

if ($driver == 'access') then
    setenv ACCESS   yes
    setenv OASIS3_MCT yes
    setenv AusCOM   yes
else
    setenv AusCOM   no
    setenv ACCESS   no
endif

### Location and name of the generated executable
set variant = "${driver}_${resolution}_${blocks}_${ntask}p"
setenv EXE cice_${variant}.exe

### Where this model is compiled
setenv OBJDIR $SRCDIR/build_${variant}
mkdir -p $OBJDIR

setenv NTASK $ntask
set NXGLOB = `echo $resolution | sed s/x.\*//`
set NYGLOB = `echo $resolution | sed s/.\*x//`
set NXBLOCK = `echo $blocks | sed s/x.\*//`
set NYBLOCK = `echo $blocks | sed s/.\*x//`
setenv BLCKX `expr $NXGLOB / $NXBLOCK` # x-dimension of blocks ( not including )
setenv BLCKY `expr $NYGLOB / $NYBLOCK` # y-dimension of blocks (  ghost cells  )

@ a = $NXGLOB * $NYGLOB ; @ b = $BLCKX * $BLCKY * $NTASK
@ m = $a / $b ; setenv MXBLCKS $m ; if ($MXBLCKS == 0) setenv MXBLCKS 1
echo Automatically generated: MXBLCKS = $MXBLCKS

cp -f $CBLD/Makefile.std $CBLD/Makefile

if ($NTASK == 1) then
   setenv COMMDIR serial
else
   setenv COMMDIR mpi
endif
echo COMMDIR: $COMMDIR

if ($driver == 'access') then
  # For "Zero-Layer" ice configuration (ACCESS version)
  set N_ILYR = 1
else
  # For standard multi-layer ice.
  set N_ILYR = 4
endif
setenv DRVDIR $driver

cd $OBJDIR

### List of source code directories (in order of importance).
cat >! Filepath << EOF
$SRCDIR/drivers/$DRVDIR
$SRCDIR/source
$SRCDIR/$COMMDIR
$SRCDIR/$SHRDIR
EOF

cc -o makdep $CBLD/makdep.c || exit 2

make VPFILE=Filepath EXEC=$EXE \
           NXGLOB=$NXGLOB NYGLOB=$NYGLOB \
           N_ILYR=$N_ILYR \
           BLCKX=$BLCKX BLCKY=$BLCKY MXBLCKS=$MXBLCKS \
      -f  $CBLD/Makefile MACFILE=$CBLD/Macros.spack || exit 2

cd ..
pwd
echo NTASK = $NTASK
echo "global N, block_size"
echo "x    $NXGLOB,    $BLCKX"
echo "y    $NYGLOB,    $BLCKY"
echo max_blocks = $MXBLCKS
echo N_ILYR = $N_ILYR
