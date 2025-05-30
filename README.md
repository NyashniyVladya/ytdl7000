# Расширение для удобной загрузки видео с YouTube для chromium браузеров, основанное на `yt-dlp`.

> [!IMPORTANT]
> Перед установкой убедитесь, что на ПК установлен `Python` версии 3.9 или выше и `ffmpeg`.

## Как использовать:

1. Открыть командную строку
2. Запустить следующие команды:
   ```cmd
   python -m pip install -U yt-dlp[default]
   python -m pip cache purge
   python -m pip install -U https://github.com/NyashniyVladya/ytdl7000/archive/refs/heads/main.zip
   ```
3. По окончании установки появится папка `%userprofile%\\ytdl7000_ext` - установить её как расширение в вашем chromium браузере (инструкция ниже)
4. На странице с нужным видео/каналом/плейлистом нажать на иконку расширения и выбрать нужные опции загрузки

### Как установить расширение в chromium:

1. Открыть в браузере адрес `chrome://extensions` (в Яндекс браузере `browser://extensions`)
2. Включить в правом верхнем углу режим разработчика
3. Выбрать пункт "Загрузить распакованное расширение"
4. Указать папку `%userprofile%\\ytdl7000_ext`

--------------------------

# Extension for easy downloading videos from YouTube for chromium browsers, based on 'yt-dlp'.

> [!IMPORTANT]
> Before installing, make sure that your PC has `Python` 3.9 or higher and `ffmpeg`.

## How to use it:

1. Open the command prompt
2. Run the following commands:
   ```cmd
   python -m pip install -U yt-dlp[default]
   python -m pip cache purge
   python -m pip install -U https://github.com/NyashniyVladya/ytdl7000/archive/refs/heads/main.zip
   ```
3. After the installation is complete, the folder `%userprofile%\\ytdl7000_ext` will appear - install it as an extension in your chromium browser (instructions below)
4. On the page with the desired video/channel/playlist, click on the extension icon and select the desired download options

### How to install an extension in chromium:

1. Open the address `chrome://extensions` (in Yandex browser `browser://extensions`)
2. Enable developer mode in the upper-right corner
3. Select "Download Unpacked extension" button
4. Choose `%userprofile%\\ytdl7000_ext` folder
