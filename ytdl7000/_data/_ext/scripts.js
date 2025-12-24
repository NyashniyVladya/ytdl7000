
import * as translations from "./translations.js";

let _CONFIG = {
    lang: null,
    version: 6,
    checkBoxes: {
        chooseSavedir: false,
        loadFullPlaylist: false,
        savePlaylistInExtraFolder: true,
        usePlaylistNumeration: true,
        invertPlaylistNumeration: false,
        skipErrors: false,
        audioOnly: false,
        useSponsorBlock: true,
        passCookies: false
    },
    fields: {
        maxQuality: "1080",
        restartAttempts: "5",
        playlistItems: ""
    }
};
let _config = window.localStorage.getItem("config");
if (_config) {
    _config = JSON.parse(_config);
    if (("version" in _config) && (_config.version >= _CONFIG.version)) {
        _CONFIG = _config;
    };
};


function setLang() {

    let lang = _CONFIG.lang;
    if (lang === null) {
        const localeObject = new Intl.Locale(navigator.language);
        lang = localeObject.language;
        if (!(lang in translations)) {
            lang = "en";
        };
        _CONFIG.lang = lang;
        window.localStorage.setItem("config", JSON.stringify(_CONFIG));
    };

    let element;
    for (let key in translations[lang]) {
        element = document.getElementById(key);
        if (element) {
            element.innerHTML = translations[lang][key];
        };
    };
};

async function startDownload() {

    const [tab] = await chrome.tabs.query({active: true});

    let requestData = {};

    let element = document.getElementById("maxQuality");
    if (element.value) {
        requestData["best-height"] = Number(element.value);
    };

    element = document.getElementById("chooseSavedir");
    if (element.checked) {
        requestData["savedir"] = ":autoChoice:";
    };

    element = document.getElementById("loadFullPlaylist");
    if (element.checked) {
        requestData["load-full-playlist"] = true;
    };

    element = document.getElementById("savePlaylistInExtraFolder");
    if (element.checked) {
        requestData["use-playlist-extra-folder"] = true;
    };

    element = document.getElementById("usePlaylistNumeration");
    if (element.checked) {
        requestData["use-playlist-numeration"] = true;
    };

    element = document.getElementById("invertPlaylistNumeration");
    if (element.checked) {
        requestData["invert-playlist-numeration"] = true;
    };

    element = document.getElementById("playlistItems");
    if (element.value) {
        requestData["playlist-items"] = element.value;
    };

    element = document.getElementById("skipErrors");
    if (element.checked) {
        requestData["skip-error"] = true;
    };

    element = document.getElementById("audioOnly");
    if (element.checked) {
        requestData["audio-only"] = true;
    };

    element = document.getElementById("useSponsorBlock");
    if (element.checked) {
        requestData["use-sponsorblock"] = true;
    };

    element = document.getElementById("restartAttempts");
    if (element.value) {
        requestData["restart-attempts"] = Number(element.value);
    };

    element = document.getElementById("passCookies");
    if (element.checked) {

        let cookies = await chrome.cookies.getAll({url: tab.url});

        if (cookies.length >= 1) {

            let cookiesNetscape = "# Netscape HTTP Cookie File\n";
            for (const cookie of cookies) {

                cookiesNetscape += cookie.domain;
                cookiesNetscape += "\t";

                cookiesNetscape += (cookie.domain.startsWith(".")) ? "TRUE" : "FALSE";
                cookiesNetscape += "\t";

                cookiesNetscape += cookie.path;
                cookiesNetscape += "\t";

                cookiesNetscape += (cookie.httpOnly) ? "TRUE" : "FALSE";
                cookiesNetscape += "\t";

                cookiesNetscape += (cookie.expirationDate) ? String(Math.round(cookie.expirationDate)) : "";
                cookiesNetscape += "\t";

                cookiesNetscape += cookie.name;
                cookiesNetscape += "\t";

                cookiesNetscape += cookie.value;

                cookiesNetscape += "\n";

            };

            requestData["cookies-txt"] = cookiesNetscape;

        };
    };

    await chrome.runtime.sendMessage({
        command: "startDownload",
        url: tab.url,
        requestData: requestData
    });
};

function init() {

    let element;

    for (let key in _CONFIG.checkBoxes) {
        element = document.getElementById(key);
        if (element) {
            element.checked = _CONFIG.checkBoxes[key];
            element.addEventListener(
                "click",
                function() {
                    const _element = document.getElementById(key);
                    _CONFIG.checkBoxes[_element.id] = _element.checked;
                    window.localStorage.setItem("config", JSON.stringify(_CONFIG));
                }
            );
        };
    };


    for (let key in _CONFIG.fields) {
        element = document.getElementById(key);
        if (element) {
            element.value = _CONFIG.fields[key];
            element.addEventListener(
                "input",
                function() {
                    const _element = document.getElementById(key);
                    _CONFIG.fields[_element.id] = _element.value;
                    window.localStorage.setItem("config", JSON.stringify(_CONFIG));
                }
            );
        };
    };


    element = document.getElementById("langCode");
    let option;
    for (let key in translations) {

        option = document.createElement("option");
        option.value = key;
        option.innerHTML = key;
        if (key == _CONFIG.lang) {
            option.selected = true;
        };
        element.appendChild(option);
    };

    element.addEventListener(
        "change",
        function() {
            const _element = document.getElementById("langCode");
            _CONFIG.lang = _element.value;
            window.localStorage.setItem("config", JSON.stringify(_CONFIG));
            setLang();
        }
    );


    element = document.getElementById("startDownload");
    element.addEventListener("click", startDownload);

};

setLang();
init();
