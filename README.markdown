# About
Django project for Android

# Installation
## Scripting Layer for Android
* Install [SL4A](http://code.google.com/p/android-scripting/) on Android

## Django
* Get [Django](https://www.djangoproject.com/) here: [tarball](https://www.djangoproject.com/download/1.4/tarball/)
* Copy _django_ directory from the tarball into the **/mnt/sdcard/com.googlecode.pythonforandroid/extras/python/** directory on Android

## Jadro
* Get Jadro

    git clone git://github.com/b3b/jadro.git

* Create the **/mnt/sdcard/sl4a/scripts/jadro/** directory on Android
* Copy all the Jadro files into the **/mnt/sdcard/sl4a/scripts/jadro/** directory on Android

## Root
* Root the Android to have access to Android SQLite databases

# Usage
_run.py_ (from the Jadro directory) is a Django manage.py wrapper. To run manage.py command, launch _run.py_ and follow the dialogs

* Create default database with _syncdb_ command
* Start Web server with _runserver_ command
* Open http://127.0.0.1:8000/ from Android browser

## Additional manage.py commands
* find_databases
Find and output a paths to SQLite databases

* inspectdb --database_path=DATABASE\_PATH
Introspects _DATABASE\_PATH_ SQLite database

* startapp --database_path=DATABASE_PATH
Create app for _DATABASE\_PATH_ SQLite database
