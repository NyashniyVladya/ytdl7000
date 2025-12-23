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
import json
import shlex
import argparse
import pathlib
import threading
import shutil
import yt_dlp
import http.server
import urllib.parse
from . import utils

__author__ = "Vladya"
__version__ = "1.17.0"


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


class _Handler(http.server.BaseHTTPRequestHandler):

    LAST_VALUE = None

    def _send_answer(self, status_code, message):

        if 400 <= status_code < 600:
            answer = {"error": message}
        else:
            answer = {"message": message}

        self.send_response(status_code)
        self.send_header("Access-Control-Allow-Origin", '*')
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(answer).encode("utf_8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", '*')
        self.send_header("Access-Control-Allow-Methods", 'POST')
        self.send_header("Access-Control-Allow-Headers", '*')
        self.end_headers()

    def do_POST(self):

        if "application/json" not in self.headers["Content-Type"].lower():
            self._send_answer(415, "Incorrect content-type")
            return

        try:
            data = self.rfile.read(int(self.headers["Content-Length"]))
            data = json.loads(data)
        except Exception:
            self._send_answer(400, "Error while decoding JSON")
        else:
            if isinstance(data, dict):
                self._send_answer(200, "Success")
                _Handler.LAST_VALUE = data
                threading.Thread(target=self.server.shutdown).start()
            else:
                self._send_answer(400, "Incorrect JSON format")


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
        cookies_txt=None
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

    if cookies_txt:
        params["cookiefile"] = io.StringIO(cookies_txt)

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
        parser.add_argument("--skip-errors", action="store_true")
        parser.add_argument("--audio-only", action="store_true")
        parser.add_argument("--no-sponsorblock", action="store_true")
        parser.add_argument("--cookies-txt", default=None)

        parser.add_argument("--data-port", default=None)

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

        params = dict(
            savedir=namespace.savedir,
            best_height=namespace.best_height,
            skip_errors=namespace.skip_errors,
            load_full_playlist=namespace.load_full_playlist,
            use_playlist_extra_folder=namespace.playlist_extra_folder,
            use_playlist_numeration=namespace.use_playlist_numeration,
            invert_playlist_numeration=namespace.invert_playlist_numeration,
            playlist_items=namespace.playlist_items,
            audio_only=namespace.audio_only,
            use_sponsorblock=(not namespace.no_sponsorblock),
            restart_attempts=namespace.restart_attempts,
            cookies_txt=namespace.cookies_txt
        )

        data_port = namespace.data_port
        if data_port:
            LOGGER.info("Port was passed. Wait data request")
            data_port = int(data_port)
            with http.server.HTTPServer(("", data_port), _Handler) as _server:
                _server.serve_forever()
            for k, v in _Handler.LAST_VALUE.items():
                params[k.replace('-', '_')] = v
            LOGGER.info("Success")
            _Handler.LAST_VALUE = None

        restart_attempts = params.pop("restart_attempts")

        if params["savedir"] == ":autoChoice:":
            params["savedir"] = utils.ask_directory()

        if params["savedir"] is not None:
            params["savedir"] = pathlib.Path(params["savedir"]).resolve()

        _counter = 0
        while True:

            LOGGER.info("Attempt %d", (_counter + 1))

            try:
                download(*namespace.urls, **params)
            except Exception as ex:
                if _counter >= restart_attempts:
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
