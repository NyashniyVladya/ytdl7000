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
    name="ytdl7000",
    version="1.8.5",
    author="Vladya",
    python_requires=">=3.9",
    description="Download video from YouTube based on `yt-dlp`",
    install_requires=(
        "yt-dlp[default]",
    ),
    packages=setuptools.find_packages(),
    package_data={
        "ytdl7000": ["_data/**"]
    },
    entry_points={
        "console_scripts": (
            "ytdl7000=ytdl7000:main",
            "create_ytdl7000_ext=ytdl7000.chromium_ext_creator:main"
        )
    },
    cmdclass={
        "install": _MyInstaller
    }
)
