# APIS Ontologies

Django application to help explore literary works and related (meta) data. Part of the [APIS-app](https://www.oeaw.ac.at/acdh/tools/apis-app) ecosystem.

**Note on repository contents:**

ACDH-CH's `apis-ontologies` repository contains files essential to any APIS Ontologies app, and simultaneously serves as central storage place for files specific to separate APIS Ontologies instances which belong to research projects carried out independently from one another at the Austrian Centre for Digital Humanities and Cultural Heritage.


## Setup

### Django project for development and deployment

[APIS RDF Devops](../apis-rdf-devops) is the larger Django project used to deploy APIS Ontologies apps. It serves as Git *superproject* which APIS Ontologies is one Git *submodule* of.

To ensure correct interlinking of Git superproject and submodules, please follow the installation instructions in the APIS RDF Devops [README](../apis-rdf-devops/README.md). It is *not* advisable to clone the various repositories separately and attempt to connect them manually.

### Create a new APIS Ontologies application

For a new research project, create a new directory at the root of the `apis-ontologies` repository using a sensible/recognisable name (reflective of the research project). Copy all files and folders from an existing application over to the new directory for later adaptation.

#### Configure local settings

To override default settings and store variables and secrets relevant to local development, local settings file are used for individual apps. These are *not meant to be committed* and are set to be ignored by Git via the repository's main `.gitignore` file.

Use `local_settings_template.py` located at `base_project > settings` to create a new file `local_settings.py`. Place this file in your new application's `settings` directory.

Set a `SECRET_KEY` as per the comments in the template. Once you have a database for local development in place, update the database settings so Django can connect to it. For a local MariaDB or MySQL database, for example, you have to fill in values for the `NAME`, `USER` and `PASSWORD` variables:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "",
        "USER": "",
        "PASSWORD": "",
        "HOST": "localhost",  # use "localhost" or the IP address your DB is hosted on
        "PORT": "3306",
    }
}
```
