# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

from setuptools import setup, find_packages

setup(
    name="ytdl7000",
    version="1.7.11",
    author="Vladya",
    python_requires=">=3.9",
    description="Download video from YouTube based on `yt-dlp`",
    install_requires=(
        "yt-dlp[default]",
    ),
    packages=find_packages(),
    package_data={
        "ytdl7000": ["_data/**"]
    },
    entry_points={
        "console_scripts": (
            "ytdl7000=ytdl7000:main",
            "create_ytdl7000_ext=ytdl7000.chromium_ext_creator:main"
        )
    }
)
