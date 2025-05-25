# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import os
import sys
import json
import shutil
import pathlib
import winreg
from . import __version__ as _version

EXT_DIR = pathlib.Path.home().resolve(True)

EXECUTABLE = pathlib.Path(sys.executable).parent.joinpath("Scripts").joinpath(
    "ytdl7000.exe"
).resolve(True)

URI_SCHEME = "ytdl7000"


def create_manifest():
    return {
        "manifest_version": 3,  # Constant value
        "name": "ytdl7000",
        "version": _version,
        "description": "Chromium ext for download videos from YouTube",
        "action": {
            "default_popup": "popup.html"
        },
        "permissions": [
            "tabs"
        ],
        "icons": {
            "16": "icons/icon16.png",
            "48": "icons/icon48.png",
            "128": "icons/icon128.png",
            "256": "icons/icon256.png",
        },
        "host_permissions": [
            "*://*.gvt1.com/*",
            "*://*.youtu.be/*",
            "*://*.youtube-nocookie.com/*",
            "*://*.youtube.com/*",
            "*://*.youtubeeducation.com/*",
            "*://*.ytimg.com/*",
            "*://*.googlevideo.com/*",
            "*://*.ggpht.com/*",
        ]
    }


def _set_uri_scheme():

    def _cr_key(key, sub_key):
        return winreg.CreateKeyEx(key, sub_key, access=winreg.KEY_WRITE)

    def _set_val(key, name, value):
        return winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)

    try:
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, URI_SCHEME)
    except OSError:
        pass

    with _cr_key(winreg.HKEY_CLASSES_ROOT, URI_SCHEME) as key:

        _set_val(key, "", "URL:{0} Protocol".format(URI_SCHEME))
        _set_val(key, "URL Protocol", "")

        with _cr_key(key, "shell") as key:
            with _cr_key(key, "open") as key:
                with _cr_key(key, "command") as key:
                    _set_val(
                        key,
                        "",
                        "\"{0}\" \"%1\" --from-browser".format(EXECUTABLE)
                    )


def main():

    ext_folder = EXT_DIR.joinpath("ytdl7000_ext").resolve()
    if ext_folder.exists():
        shutil.rmtree(ext_folder)

    ext_folder.mkdir(parents=True)

    _set_uri_scheme()

    _files = pathlib.Path(__file__).parent.joinpath("_data").joinpath("_ext")
    _files = _files.resolve(True)
    for dp, _, fns in os.walk(_files):
        dp = pathlib.Path(dp).resolve(True)
        for fn in map(dp.joinpath, fns):
            target_fn = ext_folder.joinpath(fn.relative_to(_files))
            target_fn.parent.mkdir(parents=True, exist_ok=True)
            with target_fn.open("wb") as _file_write:
                with fn.open("rb") as _file_read:
                    _file_write.write(_file_read.read())

    with ext_folder.joinpath("manifest.json").open(
        'w',
        encoding="utf_8"
    ) as _file_write:
        json.dump(create_manifest(), _file_write, ensure_ascii=False, indent=4)
