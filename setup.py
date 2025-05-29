# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import setuptools
import setuptools.command.install


class _MyInstaller(setuptools.command.install.install):

    def run(self):

        super(_MyInstaller, self).run()

        import ytdl7000.chromium_ext_creator

        ytdl7000.chromium_ext_creator.main()


setuptools.setup(
    cmdclass={
        "install": _MyInstaller
    }
)
