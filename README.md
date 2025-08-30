# Scriptorium

<img src="data/icons/hicolor/scalable/apps/io.github.cgueret.Scriptorium.svg" width="128" height="128" />
<p>Design and write manuscripts</p>

Scriptorium is a text editor coupled with a planning tool and a publishing tool.

The objective is to provide writers with a simple and complete environment to plan, write and publish e-books.

Main features:

  * **Plan** the list of scenes and story elements of the manuscript
  * **Write** the content of the scenes with a text focused editor
  * **Publish** your manuscript as an epub after previewing it

In addition, some general features are:

  * Dark mode
  * Versioning of scenes managed via Git
  * Back-end using plain text YAML and HTML files


## Installation

<a href='https://flathub.org/apps/io.github.cgueret.Scriptorium'><img width='240' alt='Get it on Flathub' src='https://flathub.org/api/badge?locale=en'/></a>


## Screenshots

![screenshot](https://raw.githubusercontent.com/cgueret/Scriptorium/739941bc737e790eee305f0c25424d4caddc742b/data/screenshots/write.png)

More screenshots are available in `data/screenshots`


## Build and run

To build and run the app once you cloned the repo do:

```
flatpak run org.flatpak.Builder --force-clean --sandbox --user --install \
    --install-deps-from=flathub --ccache \
    --mirror-screenshots-url=https://dl.flathub.org/media/ \
    --repo=repo builddir io.github.cgueret.Scriptorium.json
```

and then

```
flatpak run io.github.cgueret.Scriptorium
```

You may have to run this first if it's the first time you build:

```
flatpak install -y flathub org.flatpak.Builder
flatpak remote-add --if-not-exists --user flathub \
    https://dl.flathub.org/repo/flathub.flatpakrepo
```

## Credit

The quill on the icon comes from <a href="https://www.svgrepo.com/svg/229764/quill">SVG Repo</a>

This project contains a lot of codes inspired by many other open source projects, thanks everyone!

