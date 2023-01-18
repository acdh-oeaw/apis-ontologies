# APIS Ontologies

Django application to help explore literary works and related (meta) data. Part of the [APIS-app](https://www.oeaw.ac.at/acdh/tools/apis-app) ecosystem.

The repository [apis-ontologies](https://github.com/acdh-oeaw/apis-ontologies) serves as central storage place for settings and data belonging to different APIS Ontologies apps as well as files shared between them all. Each of these apps is developed and maintained independently of the others as part of a separate research project carried out at the Austrian Centre for Digital Humanities and Cultural Heritage, [ACDH-CH](https://www.oeaw.ac.at/acdh/).

---

## Setup

### Django project for development and deployment

[apis-rdf-devops](https://github.com/acdh-oeaw/apis-rdf-devops) is the larger Django project used to deploy APIS Ontologies apps. It serves as Git superproject which APIS Ontologies is one Git submodule of.

To ensure correct interlinking of Git superproject and submodules, follow the [setup instructions](https://github.com/acdh-oeaw/apis-rdf-devops#setup) in **apis-rdf-devops**. It is _not_ advisable to clone the various repositories separately and attempt to connect them manually.

### Create a new APIS Ontologies application

For a new research project, create a new directory at the root of the **apis-ontologies** repository. Choose a sensible/recognisable name reflective of the research endeavour. Note: app names must be all-lowercase and may only contain letters, numbers and underscores (e.g. for improved readability for multi-word names).

Next, copy all files and folders from an existing application over to the new directory for later adaptation.

#### Configure local settings

To override default settings and store variables and secrets relevant to local development, a local settings file is used. This file is not meant to be committed – if you name it `local_settings.py`, Git is set to ignore it.

Use `local_settings_template.py` located at `base_project > settings` to create your own `local_settings.py` file and place it in your new application's `settings` directory.

Whenever you run a Django management command, make sure to reference it [as per the instructions](https://github.com/acdh-oeaw/apis-rdf-devops#django-setup) in **apis-rdf-devops**.

##### Required settings

The only strictly required setting for local development is the information about the database connection.

Adapt the `DATABASES` dictionary once you have a database for local development in place. For a local MariaDB or MySQL database, for example, use the following config with values for `NAME`, `USER` and `PASSWORD` provided:

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

Once you migrate the application to a production environment, you should set a `SECRET_KEY` environment variable.

## Sharing of updates to code

While working locally, most changes to your app's code will likely get picked up on-the-fly by the local development server (provided the appropriate Django management commands are run where required).

However, for deployment elsewhere, you need to make sure all changes to the **apis-ontologies** submodule are actually available to and can be picked up by the **apis-rdf-devops** superproject on the remote.

Take care to always:

1. push all relevant commits to the submodule to its remote
2. update the superproject's pointer to the submodule (by committing the changes in the superproject while the submodule is checked out on the correct commit)
