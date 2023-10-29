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

## Usage

Edit *config.py* to set database connection and you can also change the "tag" for the comments from MS_Description (standard for SQL Server) to another value

You can call main.py --help to see comand line arguments (with description).


Hope it works for you!

Regards

Cristian Solervicéns.
