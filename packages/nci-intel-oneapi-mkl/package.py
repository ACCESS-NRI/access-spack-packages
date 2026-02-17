# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 Angus Gibson
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.pkg.builtin.intel_oneapi_mkl import IntelOneapiMkl

class NciIntelOneapiMkl(IntelOneapiMkl):
    @property
    def component_prefix(self):
        # we don't need to join the version into the prefix
        # on Gadi, because the paths have been rearranged
        return self.prefix.join(self.component_dir)
