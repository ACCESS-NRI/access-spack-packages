# ACCESS-NRI Spack packages

This is a Spack package repository maintained by ACCESS-NRI containing Spack package recipes that are not available in the upstream `spack-packages` repository. Where possible ACCESS-NRI developed Spack package recipes will be contributed to the upstream `spack-packages` repository. In some cases it is not possible to do this, for example where it isn't appropriate to distribute a package that only supports ACCESS-NRI build use-cases.

The namespace of the package repository is access.nri

## How to utilise this package repository

By default, Spack will automatically clone a single package repository (`builtin`)
```bash
$ spack repo list
[+] builtin       v2.2    $SPACK_ROOT/package_repos/fncqgg4/repos/spack_repo/builtin
```
(note `$SPACK_ROOT` is substituted in all paths to make the description installation independent)

And the package is not available:
```
$ spack list oasis3-mct
==> 0 packages
```

To build and install the packages in this repository, first clone the repo to a path of your choosing (represented here as `$PACKAGE_PATH`)
```
git clone https://github.com/ACCESS-NRI/access-spack-packages.git $PACKAGE_PATH/access-spack-packages
```
and then add the location of the repository to your Spack instance
```
spack repo add $PACKAGE_PATH/access-spack-packages
```
and then confirm it is has been added correctly:
```
$ spack repo list
[+] access.nri    v2.0    $PACKAGE_PATH/access-spack-packages/spack_repo/access/nri
[+] builtin       v2.2    $SPACK_ROOT/package_repos/fncqgg4/repos/spack_repo/builtin
```
Now the `oasis3-mct` package should be available to install
```
$ spack list oasis3-mct
oasis3-mct
==> 1 packages
```

## More information

For more information see the extensive [spack documentation](https://spack.readthedocs.io/en/latest/repositories.html) on how to utilise repository files.
