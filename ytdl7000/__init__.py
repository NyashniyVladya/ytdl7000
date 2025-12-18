# -*- coding: utf-8 -*-
"""
@author: Vladya
"""

import re
import sys
import time
import logging
import os
import io
import shlex
import argparse
import pathlib
import shutil
import urllib.parse
import yt_dlp
from . import utils

__author__ = "Vladya"
__version__ = "1.15.20"


def _get_logger():
    result = logging.getLogger(__name__)
    _formatter = logging.Formatter("[%(name)s] [%(levelname)s] %(message)s")
    _handler = logging.StreamHandler()
    _handler.setFormatter(_formatter)

    result.addHandler(_handler)
    result.setLevel(logging.DEBUG)
    return result


LOGGER = _get_logger()
del _get_logger


def _get_pp_options(use_sponsorblock, audio_only=False):

    params = (
        "--sponsorblock-mark", "all",
        "--concat-playlist", "multi_video"
    )

    if audio_only:
        params += (
            "-x", "--audio-format", "mp3"
        )
    else:
        params += (
            "--merge-output-format", "mp4",
            "--remux-video", "mp4"
        )

    if use_sponsorblock:
        params += (
            "--sponsorblock-remove", "all,-filler,-music_offtopic"
        )

    _, opts, _ = yt_dlp.parseOpts(params)
    yt_dlp.set_compat_opts(opts)
    yt_dlp.validate_options(opts)
    return tuple(yt_dlp.get_postprocessors(opts))


def download(
        *urls,
        savedir=None,
        best_height=1080,
        skip_errors=False,
        load_full_playlist=True,
        use_playlist_extra_folder=True,
        use_playlist_numeration=True,
        playlist_items=None,
        invert_playlist_numeration=False,
        audio_only=False,
        use_sponsorblock=True,
        cookies=None
):

    best_height = int(best_height)
    assert (best_height >= 144)

    if savedir is None:
        _desktop = pathlib.Path.home().joinpath("Desktop").resolve(True)
        savedir = _desktop.joinpath("Videos").resolve()

    assert savedir, "No `savedir` was found"

    savedir = pathlib.Path(savedir).resolve()
    assert (not savedir.is_file()), "`savedir` must be directory"
    savedir.mkdir(parents=True, exist_ok=True)

    tempdir = savedir.joinpath("_temp{0}".format(int((time.time() * 1e5))))
    assert (not tempdir.is_file()), "`tempdir` must be directory"
    shutil.rmtree(tempdir, ignore_errors=True)
    tempdir.mkdir(parents=True, exist_ok=True)

    if audio_only:
        _format_param = "ba[acodec^=mp3]/ba/b/b*"
    else:
        _format_param = """
            bv[height<={0}]+ba/b[height<={0}]/bv+ba/b/b*
        """.strip().format(best_height)

    info = None
    _pattern = re.compile("^(?P<num>\\d+)(?=\\.\\s)")

    def _f(fn):

        if not load_full_playlist:
            return

        if not use_playlist_numeration:
            return

        if not invert_playlist_numeration:
            return

        assert info
        if "playlist_count" not in info:
            return

        _playlist_count = info["playlist_count"]
        size = str(len(str(_playlist_count)))

        fn = pathlib.Path(fn).resolve()

        _mtch = _pattern.search(fn.name)
        if not _mtch:
            return

        current_id = int(_mtch.group("num")) - 1
        new_id = (_playlist_count - current_id)
        new_id = "{0:>0{1}}".format(new_id, size)

        new_fn = fn.parent.joinpath(
            _pattern.sub(new_id, fn.name)
        )
        os.rename(fn, new_fn)

    params = {
        "min_views": None,
        "max_views": None,
        "age_limit": 21,
        "windowsfilenames": True,
        "paths": {
            "home": str(savedir),
            "temp": str(tempdir)
        },
        "format": _format_param,
        "final_ext": ("mp3" if audio_only else "mp4"),
        "overwrites": False,
        "postprocessors": _get_pp_options(
            use_sponsorblock=use_sponsorblock,
            audio_only=audio_only
        ),
        "postprocessor_args": {
            "merger+ffmpeg_i1": ["-stream_loop", "-1"],
            "merger+ffmpeg_o1": ["-shortest", "-shortest_buf_duration", "0"]
        },
        "post_hooks": (_f, )
    }

    if isinstance(playlist_items, str):
        playlist_items = playlist_items.strip()

    if playlist_items:
        params["playlist_items"] = playlist_items

    if skip_errors:
        params["ignoreerrors"] = True

    if load_full_playlist:
        if use_playlist_extra_folder or use_playlist_numeration:
            pattern = ""
            if use_playlist_extra_folder:
                pattern += "%(playlist)s/"
            if use_playlist_numeration:
                pattern += "%(playlist_index)s. "
            pattern += "%(title)s.%(ext)s"
            params["outtmpl"] = {"default": pattern}
    else:
        params["noplaylist"] = True

    if cookies:
        params["cookiefile"] = cookies

    try:

        for url in urls:

            with yt_dlp.YoutubeDL(params=params) as _downloader:
                info = _downloader.extract_info(
                    url,
                    download=False,
                    process=False
                )
                _downloader.download((url, ))

    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def main():

    try:

        parser = argparse.ArgumentParser("ytdl7000")
        parser.add_argument("urls", nargs='+')
        parser.add_argument("--savedir", default=None)
        parser.add_argument("--best-height", default=1080, type=int)
        parser.add_argument("--restart-attempts", default=5, type=int)
        parser.add_argument("--load-full-playlist", action="store_true")
        parser.add_argument("--playlist-extra-folder", action="store_true")
        parser.add_argument("--use-playlist-numeration", action="store_true")
        parser.add_argument("--invert-playlist-numeration", action="store_true")
        parser.add_argument("--playlist-items", default=None)
        parser.add_argument("--cookies-file", default=None)
        parser.add_argument("--skip-errors", action="store_true")
        parser.add_argument("--audio-only", action="store_true")
        parser.add_argument("--no-sponsorblock", action="store_true")
        parser.add_argument("--wait-cookie-timeout", default=15., type=float)
        parser.add_argument("--from-browser", action="store_true")

        namespace = parser.parse_args()
        LOGGER.info("Starting")

        _from_browser = namespace.from_browser
        if _from_browser:
            _protocol = "ytdl7000:"
            single_arg = sys.argv[1]
            if single_arg.startswith(_protocol):
                single_arg = single_arg[len(_protocol):]
            single_arg = urllib.parse.unquote(single_arg)
            namespace = parser.parse_args(shlex.split(single_arg))

        _savedir = namespace.savedir
        if _savedir == ":autoChoice:":
            _savedir = utils.ask_directory()

        if _savedir is not None:
            _savedir = pathlib.Path(_savedir).resolve()

        cookies = None
        _cookies = namespace.cookies_file
        if _cookies:

            _cookies = pathlib.Path(_cookies).resolve()
            if _from_browser:
                _wait_start_time = None
                while True:
                    # Waiting for the file to be available,
                    # in case an error occurred when downloading the file
                    # by the browser.
                    if _cookies.is_file():
                        break
                    _now = time.time()
                    if _wait_start_time is None:
                        _wait_start_time = _now
                    _wait_time = _now - _wait_start_time
                    if _wait_time > namespace.wait_cookie_timeout:
                        break
                    time.sleep(.1)

            if not _cookies.is_file():
                raise RuntimeError("No cookie file was found")

            with _cookies.open('r', encoding="utf_8") as _fo:
                cookies = io.StringIO(_fo.read())

            if _from_browser:
                _cookies.unlink(missing_ok=True)

        _counter = 0
        while True:

            LOGGER.info("Attempt %d", (_counter + 1))

            try:
                download(
                    *namespace.urls,
                    savedir=_savedir,
                    best_height=namespace.best_height,
                    skip_errors=namespace.skip_errors,
                    load_full_playlist=namespace.load_full_playlist,
                    use_playlist_extra_folder=namespace.playlist_extra_folder,
                    use_playlist_numeration=namespace.use_playlist_numeration,
                    invert_playlist_numeration=namespace.invert_playlist_numeration,
                    playlist_items=namespace.playlist_items,
                    audio_only=namespace.audio_only,
                    use_sponsorblock=(not namespace.no_sponsorblock),
                    cookies=cookies
                )
            except Exception as ex:
                if _counter >= namespace.restart_attempts:
                    raise
                LOGGER.exception(ex)
            else:
                LOGGER.info("Success")
                break

            LOGGER.info("Wait for the next attempt")
            time.sleep((1.5 ** float(_counter)))
            _counter += 1

    except Exception as ex:
        LOGGER.exception(ex)

    finally:
        os.system("pause")


def get_available_services():
    return ", ".join(
        sorted(
            frozenset(
                map(lambda a: a.ie_key(), yt_dlp.extractor.list_extractors())
            )
        )
    )


if __name__ == "__main__":
    main()
