# ACCESS-NRI Spack packages

This is a Spack package repository maintained by ACCESS-NRI for packages that are not available in the upstream Spack package repository. Where possible Spack package recipes (SPRs) written by ACCESS-NRI will be contributed to the upstream Spack packages repository.

The namespace of the ACCESS Spack package repository is `access.nri`.

## How to utilise this package repository

By default you have a single package repository (`builtin`) when you clone spack
```bash
$ spack repo list
[+] builtin    v2.2    $SPACK_ROOT/../package_repos/fncqgg4/repos/spack_repo/builtin
```
(note `$SPACK_ROOT` is substituted in all paths to make these instructions installation independent)

And the following package is not available:
```
$ spack list libaccessom2
==> 0 packages
```

To use the SPRs in this repository, **first** check if your Spack instance already includes this repository (`spack repo list`). If not, then add it manually:
```
spack repo add https://github.com/ACCESS-NRI/access-spack-packages $ACCESS_SPACK_PACKAGE_PATH
```
and then confirm it has been added correctly:
```
$ spack repo list
[+] builtin       v2.2    $SPACK_ROOT/../package_repos/fncqgg4/repos/spack_repo/builtin
[+] access.nri    v2.0    $ACCESS_SPACK_PACKAGE_PATH/spack_repo/access/nri
```
Now, the `libaccessom2` package should be available to install
```
$ spack list libaccessom2
libaccessom2
==> 1 packages
```

## More information

* The Spack package repository that was used with pre-v1.0 Spack is available in the [api-v1 branch](https://github.com/ACCESS-NRI/access-spack-packages/tree/api-v1)

* For more information see the extensive [spack documentation](https://spack.readthedocs.io/en/latest/repositories.html) on how to utilise repository files.
