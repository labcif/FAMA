# How to build an application module

## Getting Started

Open the file `/modules/packages.json` and add a reference to the application. The first element `theapplication` is the name of the module, and the second element is the package id of the Android application.

```JSON
{
    ...
    "theapplication": "com.the.application",
    ...
}
```

## Create the report module

Inside the `/modules/report` folder, create one `.py` file with the previous app name. Based on the _Getting Started_ example, the filename to be created is _theapplication.py_.

```Python
from modules.report import ModuleParent

class ModuleReport(ModuleParent):
    def __init__(self, internal_path, external_path, report_path, app_name, app_id):
        ModuleParent.__init__(self, internal_path, external_path, report_path, app_name, app_id)
        print("[TheApplication] Module started")
    
    def generate_report(self):
        self.report["category_example"] = self.get_category_example()

        print("[TheApplication] Generate Report")

        Utils.save_report(os.path.join(self.report_path, "Report.json"), self.report)
        return self.report

    def get_category_example(self):
        listing = {}
        listing["name"] = "John Doe"
        listing["address"] = "Leiria"
        return listing
```

The python file should contain this structure and implement `generate_report(self)` method. Object `self.report` contains the base data for the report structure. Gathered information should be appended to this variable.

`get_category_example(self)` is an example of how can data be processed in this model.

The `__init__.py` file contains the parent structure of the module. `self.shared_preferences` and `self_databases` contains information about the databases and shared preferences of the application. More shared information can be found on this file.

There are many utilities in this framework which can help you with this process, such `Database` for database queries and `Utils` for package helpers.

## Create the autopsy module (optional)

Inside the `/modules/autopsy` folder, create one `.py` file with the same name of the report file.

```Python
(...)
```
