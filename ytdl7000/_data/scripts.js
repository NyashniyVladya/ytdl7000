
function _tabHandler([tab]) {

    let _uri = `ytdl7000:\"${tab.url}\"`;

    let element = document.getElementById("maxQuality");
    _uri += ` --best-height \"${element.value}\"`;

    element = document.getElementById("chooseSavedir");
    if (element.checked) {
        _uri += " --savedir \":autoChoice:\"";
    };

    element = document.getElementById("loadFullPlaylist");
    if (element.checked) {
        _uri += " --load-full-playlist";
    };

    element = document.getElementById("skipErrors");
    if (element.checked) {
        _uri += " --skip-errors";
    };

    element = document.getElementById("audioOnly");
    if (element.checked) {
        _uri += " --audio-only";
    };

    element = document.getElementById("useSponsorBlock");
    if (!(element.checked)) {
        _uri += " --no-sponsorblock";
    };

    window.open(_uri);
};

function _setForm() {
    const button = document.getElementById("startDownload");
    button.addEventListener(
        "click",
        () => chrome.tabs.query({active: true}, _tabHandler)
    );
};
_setForm();
