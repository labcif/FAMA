# Unnamed Project (...)

## Getting Started

Android extraction and analysis framework with an integrated Autopsy Plugin. Dump easily user data from a device and generate powerful reports for Autopsy or external applications.

## Functionalities

* Extract user application data from an Android device with ADB (root and ADB required)
* Dump user data from an android image or mounted path.
* Easily build modules for a specific Android application.
* Generate clean and readable JSON reports.
* Integrated complete Autopsy compatibility.
* (...)

## Prerequisites

* [Python](https://www.python.org/downloads/) (2.7+)
* [Autopsy](https://www.sleuthkit.org/autopsy/) (optional)

## How to use

The script can be used directly in terminal or as Autopsy module.

### Running from Terminal

```bash
usage: start.py [-h] [-d DUMP [DUMP ...]] [-p PATH] [-o OUTPUT] [-a] app

Forensics Artefacts Analyzer

positional arguments:
  app                                            Application to be analyzed <tiktok>

optional arguments:
  -h, --help                                     show this help message and exit
  -d DUMP [DUMP ...], --dump DUMP [DUMP ...]     Analyze specific(s) dump(s) <20200307_215555 ...>
  -p PATH, --path PATH                           Dump app data in path (mount or folder structure)
  -o OUTPUT, --output OUTPUT                     Report output path folder
  -a, --adb                                      Dump app data directly from device with ADB
```

### Running from Autopsy

1. Download repository contents ([zip](https://github.com/labcif/TikTok/archive/master.zip)).
2. Open Autopsy -> Tools -> Python Plugins
3. Unzip previously downloaded zip in `python_modules` folder.
4. Restart Autopsy, create a case and select the module.
5. (...)

## Authors

* **José Francisco** - [GitHub](https://github.com/98jfran)
* **Ruben Nogueira** - [GitHub](https://github.com/rubnogueira)


## Mentors
* **Miguel Frade** - [GitHub](https://github.com/mfrade)
* **Patrício Domingues** - (...)

Project developed as final project for Computer Engineering course in Escola Superior de Tecnologia e Gestão de Leiria.

## Environments Tested
* Windows (main)
* Linux
* Mac OS

## License

Project License (...)

* [ADB](https://developer.android.com/studio/releases/platform-tools) - license (...)
* [Base64](http://rtner.de/software/base64.html) - license (...)
* [Undark](https://github.com/witwall/undark) - license (...)

## Notes

* Project under development
* Made with ❤ in Leiria, Portugal