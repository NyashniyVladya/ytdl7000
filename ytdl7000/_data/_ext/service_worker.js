
async function sleep(ms) {
    return new Promise(((resolve) => setTimeout(resolve, ms)));
};

function randInt(minValue, maxValue) {
    return Math.round((minValue + (Math.random() * (maxValue - minValue))));
};

async function _main(url, requestData) {

    console.debug(`Download from URL: ${url}`);
    console.debug(`Request data: ${JSON.stringify(requestData)}`);

    const port = randInt(1024, 65535);
    console.debug(`Data port: ${port}`);

    const _uri = `ytdl7000:\"${url}\" --data-port \"${port}\"`;
    const localURL = new URL(`http://localhost:${port}`);

    console.debug("Open URI scheme");
    const startWindow = await chrome.windows.create(
        {url: _uri, focused: false, state: "minimized"}
    );

    let _attempt = 0;
    while (true) {
        _attempt += 1;
        if (_attempt > 15) {
            break;
        };
        try {
            console.debug(`Send data (attempt ${_attempt})`);
            const resp = await fetch(
                localURL,
                {
                    method: "POST",
                    headers: {"Content-Type": "application/json;charset=utf-8"},
                    body: JSON.stringify(requestData)
                }
            );
            if (resp.ok) {
                console.debug("Success");
                break;
            };
        } catch (ex) {
            console.error(ex);
        };
        await sleep((_attempt * 1000));
    };
    console.debug("Close window");
    try {
        await chrome.windows.remove(startWindow.id);
    } catch (ex) {
        // If user close window.
        console.error(ex);
    };
    console.debug("Done");
};


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.command == "startDownload") {
        console.debug("Start main script");
        _main(message.url, message.requestData);
        console.debug("End listener");
    };
});
