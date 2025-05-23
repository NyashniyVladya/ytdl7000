# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import sys
import json
import shutil
import pathlib
import winreg
from . import __version__ as _version

DESKTOP = pathlib.Path.home().joinpath("Desktop").resolve(True)

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
        ]
    }


def _set_registry():

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

    ext_folder = DESKTOP.joinpath("ytdl7000_ext").resolve()
    shutil.rmtree(ext_folder, ignore_errors=True)
    ext_folder.mkdir(parents=True)

    _set_registry()

    for fn in ("popup.html", "scripts.js"):
        full_fn = pathlib.Path(__file__).parent.joinpath("_data").joinpath(
            fn
        ).resolve(True)
        with ext_folder.joinpath(fn).open("wb") as _file_write:
            with full_fn.open("rb") as _file_read:
                _file_write.write(_file_read.read())

    with ext_folder.joinpath("manifest.json").open(
        'w',
        encoding="utf_8"
    ) as _file_write:
        json.dump(create_manifest(), _file_write, ensure_ascii=False, indent=4)
