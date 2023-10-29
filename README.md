# DatabaseDictionary

## Author
Cristian Solervicéns C.

## Language: Python

## Description
```
Prints the Data Dictionary for SQL Server
It's based on the "Extended Properties", it works together with SQL-Crypt which allows you to edit the
Extender Properties for Tables, Views, Stored Procedures, and Functions in an easy and straight way
```

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
