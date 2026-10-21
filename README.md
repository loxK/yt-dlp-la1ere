# yt-dlp-la1ere

A [yt-dlp](https://github.com/yt-dlp/yt-dlp) plugin for [la1ere.franceinfo.fr](https://la1ere.franceinfo.fr), the France Télévisions overseas network (Nouvelle-Calédonie, Polynésie, Guadeloupe, Martinique, Guyane, La Réunion, Mayotte, Wallis-et-Futuna, Saint-Pierre-et-Miquelon).

Stock yt-dlp answers `Unsupported URL` on these pages. With the plugin you get:

| Page | Example | Result |
|------|---------|--------|
| Programme episode | `/nouvellecaledonie/programme-video/<programme>/diffusion/<id>-<slug>.html` | the episode video |
| Article | `/nouvellecaledonie/<slug>-<id>.html` | the article's videos, as a playlist when there are several |
| Audio podcast series | `/nouvellecaledonie/programme-audio/<slug>-<id>/` | every episode of the series, as MP3 |

Videos go through yt-dlp's regular France TV extractor, so formats, subtitles and geo-restrictions behave as they do on france.tv. Articles that only carry photos return `Unable to extract video id`, which is expected.

The same code is proposed upstream in [yt-dlp#16646](https://github.com/yt-dlp/yt-dlp/pull/16646) (videos) and [yt-dlp#16645](https://github.com/yt-dlp/yt-dlp/pull/16645) (audio). Once a yt-dlp release ships them, this plugin is no longer needed and can be removed.

## Requirements

- yt-dlp 2026.03.17 or later, any flavour: standalone binary, Homebrew, winget, pip, pipx or uv
- `git` is optional, it only makes updating easier

## Installation

yt-dlp loads plugins from a `plugins` folder in its configuration directory. Each plugin lives in its own subfolder, so the steps below put this repository in `plugins/yt-dlp-la1ere/`.

| System | Plugins folder |
|--------|----------------|
| Linux | `~/.config/yt-dlp/plugins/` |
| macOS | `~/.config/yt-dlp/plugins/` |
| Windows | `%APPDATA%\yt-dlp\plugins\` |

If `XDG_CONFIG_HOME` is set on Linux or macOS, use `$XDG_CONFIG_HOME/yt-dlp/plugins/` instead.

### Linux and macOS

With git:

```sh
mkdir -p ~/.config/yt-dlp/plugins
git clone https://github.com/loxK/yt-dlp-la1ere.git ~/.config/yt-dlp/plugins/yt-dlp-la1ere
```

Update with:

```sh
git -C ~/.config/yt-dlp/plugins/yt-dlp-la1ere pull
```

Without git:

```sh
mkdir -p ~/.config/yt-dlp/plugins/yt-dlp-la1ere
curl -L https://github.com/loxK/yt-dlp-la1ere/archive/refs/heads/main.tar.gz \
  | tar -xz --strip-components=1 -C ~/.config/yt-dlp/plugins/yt-dlp-la1ere
```

Run the same commands again to update.

These commands work in bash and zsh, the default shell on macOS. They apply whatever way yt-dlp was installed, Homebrew included.

### Windows

In PowerShell, with git:

```powershell
git clone https://github.com/loxK/yt-dlp-la1ere.git "$env:APPDATA\yt-dlp\plugins\yt-dlp-la1ere"
```

Update with:

```powershell
git -C "$env:APPDATA\yt-dlp\plugins\yt-dlp-la1ere" pull
```

Without git:

```powershell
$plugins = "$env:APPDATA\yt-dlp\plugins"
$zip = "$env:TEMP\yt-dlp-la1ere.zip"
New-Item -ItemType Directory -Force $plugins | Out-Null
Invoke-WebRequest https://github.com/loxK/yt-dlp-la1ere/archive/refs/heads/main.zip -OutFile $zip
Expand-Archive $zip -DestinationPath $plugins -Force
Remove-Item $zip
```

This extracts to `%APPDATA%\yt-dlp\plugins\yt-dlp-la1ere-main\`, which yt-dlp loads just the same. Run the same commands again to update.

For a portable `yt-dlp.exe` kept on a USB stick or in a single folder, put the plugin next to the executable instead, in `yt-dlp-plugins\yt-dlp-la1ere\` (note the dash: `yt-dlp-plugins`, not `plugins`).

### As a Python package

This only applies when yt-dlp itself is installed as a Python package. The standalone binaries (`yt-dlp`, `yt-dlp.exe`, `yt-dlp_macos`) do not see Python packages: use one of the folder methods above for them.

```sh
# yt-dlp installed with uv
uv tool install yt-dlp --with git+https://github.com/loxK/yt-dlp-la1ere.git

# yt-dlp installed with pipx
pipx inject yt-dlp git+https://github.com/loxK/yt-dlp-la1ere.git

# yt-dlp installed with pip
python3 -m pip install -U https://github.com/loxK/yt-dlp-la1ere/archive/refs/heads/main.zip
```

## Checking that the plugin is loaded

```sh
yt-dlp -v --simulate "https://la1ere.franceinfo.fr/nouvellecaledonie/programme-audio/le-journal-de-06h30-nouvelle-caledonie-14634/"
```

The debug header should list the plugin:

```
[debug] Extractor Plugins: FranceTVInfoIE, FranceTVInfoLa1ereAudioIE
[debug] Plugin directories: .../yt-dlp/plugins/yt-dlp-la1ere/yt_dlp_plugins
```

If it does not show up, check the folder layout. yt-dlp expects `plugins/<any name>/yt_dlp_plugins/extractor/la1ere.py`. A common mistake is one folder level too many or too few, for instance `plugins/yt_dlp_plugins/...`.

## Usage

```sh
# An episode
yt-dlp "https://la1ere.franceinfo.fr/nouvellecaledonie/programme-video/la1ere_nouvelle-caledonie_journal-de-19h30-de-nouvelle-caledonie/diffusion/8412318-edition-du-mardi-05-mai-2026.html"

# Every video of an article
yt-dlp "https://la1ere.franceinfo.fr/nouvellecaledonie/l-hopital-de-poindimie-commence-a-rouvrir-quatorze-lits-pour-les-patients-de-la-cote-est-1698130.html"

# The latest 5 episodes of a podcast series
yt-dlp -I 1:5 "https://la1ere.franceinfo.fr/nouvellecaledonie/programme-audio/le-journal-de-06h30-nouvelle-caledonie-14634/"
```

Podcast series are listed newest first and fetched page by page, so `-I 1:5` only downloads the first page of the episode list.

## Uninstall

Delete the plugin folder (`yt-dlp-la1ere` or `yt-dlp-la1ere-main`) from the plugins folder, or for a Python install:

```sh
# uv: reinstall yt-dlp without the extra package
uv tool uninstall yt-dlp && uv tool install yt-dlp

# pipx
pipx uninject yt-dlp yt-dlp-la1ere

# pip
python3 -m pip uninstall yt-dlp-la1ere
```

## License

Released into the public domain under the [Unlicense](LICENSE), like yt-dlp.

---
Built with 🥥 and ☕ by [Gecka](https://gecka.nc) — Kanaky-New Caledonia 🇳🇨
