#! /bin/csh -f

set echo on

if ( $#argv < 4 ) then
  echo '*** Please issue the command like ***'
  echo '> ./bld/build.sh <driver> <grid> <blocks> <ntask> [<debug>]'
  echo 'e.g. bld/build.sh auscom 1440x1080 48x40 480'
  echo 'driver: which driver to use.'
  echo 'grid: grid resolution longitude by latitude.'
  echo 'blocks: grid split into the number of blocks longitude by latitude.'
  echo 'ntask: number of tasks.'
  echo 'debug: if this is a unit testing or debug build. Valid options are \'debug\' or \'unit_testing\''
  exit
else
  set driver = $1
  set grid = $2
  set blocks = $3
  set ntask = $4
  set debug = $5
endif

# Location of this model
setenv SRCDIR $cwd
setenv CBLD   $SRCDIR/bld

if ($debug == 'debug') then
    setenv DEBUG 1
else
    setenv DEBUG 0
endif
if ($debug == 'unit_testing') then
    setenv DEBUG 1
    setenv UNIT_TESTING yes
endif

### Specialty code
setenv CAM_ICE    no        # set to yes for CAM runs (single column)
setenv SHRDIR     csm_share # location of CCSM shared code
setenv DITTO      no        # reproducible diagnostics
setenv THRD       no        # set to yes for OpenMP threading
if ( $THRD == 'yes') setenv OMP_NUM_THREADS 2 # positive integer 
setenv BARRIERS   yes       # set -Dgather_scatter_barrier, prevents hangs on raijin
setenv NSNWLYR    1         # number of vertical layers in the snow
setenv NICECAT    5         # number of ice thickness categories
setenv OASIS3_MCT yes	      # oasis3-mct version
setenv AusCOM     yes

if ($driver == 'access-esm1.6') then
  setenv DRVDIR   'access'
  setenv ACCESS   yes
  setenv IO_TYPE  netcdf
  setenv CHAN     MPI1	  # MPI1 or MPI2 (always MPI1!)
  setenv NICELYR  1       # 1 for ktherm=0, zero-layer thermodynamics
  setenv TRBGCS   0
  # This branch does not include version.F90.template and does not need version_mod.F90
# else if ($driver == 'access-cm2') then
#     setenv DRVDIR   'access'
#     setenv ACCESS   yes
#     setenv IO_TYPE  netcdf
#     setenv CHAN     MPI1	  # MPI1 or MPI2 (always MPI1!)
#     setenv NICELYR  4       #4 for standard multi-layer ice (ktherm=1)
#     setenv TRBGCS   2
      # This branch does not include version.F90.template and does not need version_mod.F90
else #driver = auscom
  setenv DRVDIR   $driver
  setenv ACCESS   no
  setenv IO_TYPE  pio
  setenv NICELYR  4         # number of vertical layers in the ice
  setenv TRBGCS   2         # number of skeletal layer bgc tracers 
                            # TRBGCS=0 or 2<=TRBGCS<=9)
  ### The version of an executable can be found with the following
  ### command: strings <executable> | grep 'CICE_VERSION='
  set version='202301'
  sed -e "s/{CICE_VERSION}/$version/g" $SRCDIR/drivers/$driver/version.F90.template > $SRCDIR/drivers/$driver/version_mod.F90
endif


### Where this model is compiled
setenv OBJDIR $SRCDIR/build_${driver}_${grid}_${blocks}_${ntask}p
if !(-d $OBJDIR) mkdir -p $OBJDIR

setenv NTASK $ntask
setenv RES $grid
set NXGLOB = `echo $RES | sed s/x.\*//`
set NYGLOB = `echo $RES | sed s/.\*x//`
set NXBLOCK = `echo $blocks | sed s/x.\*//`
set NYBLOCK = `echo $blocks | sed s/.\*x//`
setenv BLCKX `expr $NXGLOB / $NXBLOCK` # x-dimension of blocks ( not including )
setenv BLCKY `expr $NYGLOB / $NYBLOCK` # y-dimension of blocks (  ghost cells  )

@ a = $NXGLOB * $NYGLOB ; @ b = $BLCKX * $BLCKY * $NTASK
@ m = $a / $b ; setenv MXBLCKS $m ; if ($MXBLCKS == 0) setenv MXBLCKS 1
echo Autimatically generated: MXBLCKS = $MXBLCKS

###########################################
# ars599: 24032014
#	copy from /short/p66/ars599/CICE.v5.0/accice.v504_csiro
#	solo_ice_comp
###########################################
### Tracers               # match ice_in tracer_nml to conserve memory
setenv TRAGE   1          # set to 1 for ice age tracer
setenv TRFY    1          # set to 1 for first-year ice area tracer
setenv TRLVL   1          # set to 1 for level and deformed ice tracers
setenv TRPND   1          # set to 1 for melt pond tracers
setenv NTRAERO 0          # number of aerosol tracers 
                          # (up to max_aero in ice_domain_size.F90) 
                          # CESM uses 3 aerosol tracers
setenv TRBRI   1          # set to 1 for brine height tracer
setenv NBGCLYR 0          # number of zbgc layers

### File unit numbers
setenv NUMIN 11           # minimum file unit number
setenv NUMAX 99           # maximum file unit number

if ($IO_TYPE == 'netcdf') then
  setenv IODIR io_netcdf
else if ($IO_TYPE == 'pio') then
  setenv IODIR io_pio
else
  setenv IODIR io_binary
endif

cp -f $CBLD/Makefile.std $CBLD/Makefile

if ($NTASK == 1) then
   setenv COMMDIR serial
else
   setenv COMMDIR mpi
endif
echo COMMDIR: $COMMDIR

cd $OBJDIR

### List of source code directories (in order of importance).
cat >! Filepath << EOF
$SRCDIR/drivers/$DRVDIR
$SRCDIR/source
$SRCDIR/$COMMDIR
$SRCDIR/$IODIR
$SRCDIR/$SHRDIR
EOF

cc -o makdep $CBLD/makdep.c || exit 2

make VPFILE=Filepath EXEC=cice_${driver}_${grid}_${blocks}_${ntask}p.exe \
           NXGLOB=$NXGLOB NYGLOB=$NYGLOB \
           BLCKX=$BLCKX BLCKY=$BLCKY MXBLCKS=$MXBLCKS \
           -f  $CBLD/Makefile MACFILE=$CBLD/Macros.spack || exit 2

cd ..
pwd
echo NTASK = $NTASK
echo "global N, block_size"
echo "x    $NXGLOB,    $BLCKX"
echo "y    $NYGLOB,    $BLCKY"
echo max_blocks = $MXBLCKS
echo $TRAGE   = TRAGE,   iage tracer
echo $TRFY    = TRFY,    first-year ice tracer
echo $TRLVL   = TRLVL,   level-ice tracers
echo $TRPND   = TRPND,   melt pond tracers
echo $NTRAERO = NTRAERO, number of aerosol tracers
echo $TRBRI   = TRBRI,   brine height tracer
echo $NBGCLYR = NBGCLYR, number of bio grid layers
echo $TRBGCS  = TRBGCS,  number of BGC tracers
