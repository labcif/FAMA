# LabCIF - Android Forensics

## Getting Started

Android extraction and analysis framework with integrated Autopsy Plugin. Dump easily user data from a device and generate powerful reports for Autopsy or external applications.

## Functionalities

* Extract user application data from an Android device with ADB (root and ADB required).
* Dump user data from an android image or mounted path.
* Easily build modules for a specific Android application.
* Generate clean and readable JSON reports.
* Complete integrated Autopsy compatibility (ingest, report, communication and timeline support).
* Export HTML report based on the current case.

### Report Screenshots

![Report Index](https://i.imgur.com/T3v3uH4.png)

![Report Sample](https://i.imgur.com/uWpTKaF.png)

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
  app                                            Application or package to be analyzed <tiktok> or <com.zhiliaoapp.musically>

optional arguments:
  -h, --help                                     show this help message and exit
  -d DUMP [DUMP ...], --dump DUMP [DUMP ...]     Analyze specific(s) dump(s) <20200307_215555 ...>
  -p PATH, --path PATH                           Dump app data in path (mount or folder structure)
  -o OUTPUT, --output OUTPUT                     Report output path folder
  -a, --adb                                      Dump app data directly from device with ADB
  -H, --html                                     Generate HTML report
```

### Running from Autopsy

1. Download repository contents ([zip](../../archive/master.zip)).
2. Open Autopsy -> Tools -> Python Plugins
3. Unzip previously downloaded zip in `python_modules` folder.
4. Restart Autopsy, create a case and select the module.
5. Select your module options in the Ingest Module window selector.
6. Click "Generate Report" to generate an HTML report of the case.

## Build an application module

Do you need a forensics module for a specific Android application? Follow the instructions [here](modules/README.md) and build a module by yourself.

## Authors

* **José Francisco** - [GitHub](https://github.com/98jfran)
* **Ruben Nogueira** - [GitHub](https://github.com/rubnogueira)

## Mentors

* **Miguel Frade** - [GitHub](https://github.com/mfrade)
* **Patrício Domingues** - [GitHub](https://github.com/PatricioDomingues)

Project developed as final project for Computer Engineering course in Escola Superior de Tecnologia e Gestão de Leiria.

## Environments Tested

* Windows (primary)
* Linux
* Mac OS

## License

This project is licensed under the terms of the GNU GPL v3 License.

* [ADB](https://developer.android.com/studio/releases/platform-tools) - Android Software Development Kit License Agreement
* [Base64](http://rtner.de/software/base64.html) - GNU GPL v2 License
* [Undark](https://github.com/witwall/undark) - BSD License 2.0
* [SQLite-Deleted-Records-Parser](https://github.com/mdegrazia/SQLite-Deleted-Records-Parser) - GNU GPL v3 License
* [Bootstrap](https://getbootstrap.com/) - MIT License
* [jQuery](https://jquery.com/) - MIT License
* [feather](https://github.com/feathericons/feather) - MIT License
* [pdfmake](https://github.com/bpampuch/pdfmake) - MIT License

## Notes

* Project under development
* Made with ❤ in Leiria, Portugal
