# DatabaseDictionary

## Author
Cristian Solervicéns C.

## Language: Python

## Description

Create the Data Dictionary for SQL Server Databases in html format.

The output file is called: ***data_dictionary_[DatabaseName].html*** file.

The Data-Dictionay is based on the "Extended Properties", and it works together with SQL-Crypt which allows you to edit the
Extender Properties for Tables, Views, Stored Procedures, and Functions in a simple and straight forward way


## Dependencies

```
It depends on :
   Jinja2
   pymssql
```

## Config.py

It's a very simple file where you put the connection information and a few parameters more.

* db_passwd: if empty the program will ask for the password
* tag: Is the Tag used for comments on Extended properties in SQL Server
* logo = Is a image file for the output logo, it will be embeded into, so choose a small one
* logo_width: expressed in pixels so you can choose the size in which the logo will be displayed.

```
class Config:
    db_server = "127.0.0.1"
    db_origin = "master"
    db_user = "sa"
    db_passwd = "my.pass"
    tag = "MS_Description"
    logo = "FrogFull.png"
    logo_width = "50"
    # logo_width = "100"
```

## Usage

Edit *config.py* to set database connection and you can also change the "tag" for the comments from MS_Description (standard for SQL Server) to another value

You can call main.py --help to see comand line arguments (with description).


Hope it works for you!

Regards

Cristian Solervicéns.
