# Расширение для удобной загрузки видео с множества площадок (YouTube и пр.) для chromium браузеров, основанное на `yt-dlp`.

> [!IMPORTANT]
> Перед установкой убедитесь, что на ПК установлен `Python` версии 3.11 или выше и `ffmpeg`.

## Как использовать:

1. Открыть Windows PowerShell

1. Запустить команду:

	```cmd
	irm https://deno.land/install.ps1 | iex
	```

1. Открыть командную строку

1. Запустить следующие команды:
   ```cmd
   python -m pip install -U "yt-dlp[default]"
   ```
   ```cmd
   python -m pip cache purge
   ```
   ```cmd
   python -m pip install -U https://github.com/NyashniyVladya/ytdl7000/archive/refs/heads/main.zip
   ```

1. По окончании установки появится папка `%userprofile%\\ytdl7000_ext` - установить её как расширение в вашем chromium браузере (инструкция ниже)
1. На странице с нужным видео/каналом/плейлистом нажать на иконку расширения и выбрать нужные опции загрузки

### Как установить расширение в chromium:

1. Открыть в браузере адрес `chrome://extensions` (в Яндекс браузере `browser://extensions`)
1. Включить в правом верхнем углу режим разработчика
1. Выбрать пункт "Загрузить распакованное расширение"
1. Указать папку `%userprofile%\\ytdl7000_ext`

--------------------------

# Extension for easy downloading videos from many video hostings (e.g. YouTube, etc.) for chromium browsers, based on 'yt-dlp'.

> [!IMPORTANT]
> Before installing, make sure that your PC has `Python` 3.11 or higher and `ffmpeg`.

## How to use it:

1. Launch Windows PowerShell

1. Run the following command:

	```cmd
	irm https://deno.land/install.ps1 | iex
	```

1. Launch the command prompt

1. Run the following commands:
   ```cmd
   python -m pip install -U "yt-dlp[default]"
   ```
   ```cmd
   python -m pip cache purge
   ```
   ```cmd
   python -m pip install -U https://github.com/NyashniyVladya/ytdl7000/archive/refs/heads/main.zip
   ```

1. After the installation is complete, the folder `%userprofile%\\ytdl7000_ext` will appear - install it as an extension in your chromium browser (instructions below)
1. On the page with the desired video/channel/playlist, click on the extension icon and select the desired download options

### How to install an extension in chromium:

1. Open the address `chrome://extensions` (in Yandex browser `browser://extensions`)
1. Enable developer mode in the upper-right corner
1. Select "Download Unpacked extension" button
1. Choose `%userprofile%\\ytdl7000_ext` folder
