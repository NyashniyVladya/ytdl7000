# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import pathlib
import json
import threading
import tkinter
import tkinter.filedialog

PROJECT_DIR = pathlib.Path.home().joinpath(
    "vladya's projects database",
    "ytdl7000"
).resolve()
CONFIG = PROJECT_DIR.joinpath("config.json")
_CONFIG_VERSION = 1

FILE_LOCK = threading.RLock()


def get_config():
    with FILE_LOCK:
        if CONFIG.is_file():
            with CONFIG.open('r', encoding="utf_8") as _file:
                _config = json.load(_file)
            if _config.pop("_version", 0) == _CONFIG_VERSION:
                return _config
        return {}


def save_on_config(new_data_mapping):
    with FILE_LOCK:
        _current = get_config()
        _current.update(new_data_mapping)
        _current["_version"] = _CONFIG_VERSION
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with CONFIG.open('w', encoding="utf_8") as _file:
            json.dump(_current, _file, ensure_ascii=False, indent=4)


def ask_directory():

    with FILE_LOCK:

        options = {}
        _config = get_config()
        if "initialdir" in _config:
            options["initialdir"] = _config["initialdir"]

        root = tkinter.Tk()
        root.withdraw()

        dialog = tkinter.filedialog.Directory(master=root, **options)
        while True:
            result = dialog.show()
            if result:
                break
        result = pathlib.Path(result).resolve()

        save_on_config({"initialdir": str(result)})
        return result
