import argparse
import os

from jinja2 import Environment, FileSystemLoader

import modules.sql as SQL
from config import Config
from modules.helpers import isnone, menu


def main():

    # argumentos
    parser = argparse.ArgumentParser(prog="DataDictionary"
                                     ,description="Imprime el Diccionario de Datos Para SQL Server basado en las Extended Properties MS_Description"
                                     ,epilog="Cristian Solervicéns - 2003"
                                    )
    parser.add_argument("--no_procs", help="No despliega información de Procs. Almacenados", action="store_true")
    parser.add_argument("--no_functions",help="No despliega información de Funciones", action="store_true")
    parser.add_argument("--no_views",help="No despliega información de Vistas", action="store_true")
    parser.add_argument("--no_tables", help="No despliega información de Tablas", action="store_true")
    parser.add_argument("--DEPRECADO"
                        ,help="Incluye Tablas y Vistas con label [DEPRECADO]", action="store_true")
    parser.add_argument("--EN_DESUSO"
                        ,help="Incluye Tablas y Vistas con label [EN_DESUSOO]", action="store_true")
    parser.add_argument("--INTERNA"
                        ,help="Incluye Tablas y Vistas con label [INTERNA]", action="store_true")
    parser.add_argument("--RESPALDO"
                        ,help="Incluye Tablas y Vistas con label [RESPALDO]", action="store_true")
    parser.add_argument("--INCLUDE_ALL"
                        ,help="Incluye Tablas y Vistas con TODOS los label especiales", action="store_true")
    parser.add_argument("--only_with_comments", help="Sólo objetos Base con comentario", action="store_true") 
    args = parser.parse_args()
    # Fin argumentos

    status = ["DEPRECADO", "EN DESUSO", "INTERNA", "RESPALDO"]
    if args.INCLUDE_ALL:
        status = []
    if args.DEPRECADO:
        status.remove("DEPRECADO")
    if args.EN_DESUSO:
        status.remove("EN DESUSO")
    if args.INTERNA:
        status.remove("INTERNA")
    if args.RESPALDO:
        status.remove("RESPALDO")

    hsql.connect()
    if hsql.has_error():
        print("")
        print(f"Error conectándose a la Base de Datos {cfg.db_server}")
        print("")
        input(">> ")
        return

    print("")
    print("Diccionario de Base de Datos")
    print("")
    
    db_name = select_db()
    hsql.use_db(db_name)
    print(db_name)
    if db_name == "":
        return

    print("Obteniendo Tablas")
    if args.no_tables:
        tables = []
    else:
        tables = get_tables(cfg.tag)
    
    print("Obteniendo Vistas")
    if args.no_views:
        views = []
    else:
        views = get_views(cfg.tag)
    
    print("Obteniendo Procedimientos")
    if args.no_procs:
        procs = []
    else:
        procs = get_procs(cfg.tag)
    
    print("Obteniendo Funciones Escalares")
    if args.no_functions:
        scalar_funcs = []
    else:
        scalar_funcs = get_scalar_functions(cfg.tag)
    
    print("Obteniendo Funciones Tabulares")
    if args.no_functions:
        tbl_funcs = []
    else:
        tbl_funcs = get_tbl_functions(cfg.tag)

    # Elimino Todos los Objetos Base sin Comentario
    if args.only_with_comments:
        tables = [k for k in tables if k[2] != '']
        views = [k for k in views if k[2] != '']
        procs = [k for k in procs if k[2] != '']
        scalar_funcs = [k for k in scalar_funcs if k[2] != '']
        tbl_funcs = [k for k in tbl_funcs if k[2] != '']

    print("Obteniendo Detalle de Tablas")
    for table in tables:
        schema = table[0]
        table_name = table[1]
        res = get_table_detail(schema=schema, table=table_name, tag=cfg.tag)
        table.append(res)

    print("Obteniendo Detalle de Vistas")
    for view in views:
        schema = view[0]
        view_name = view[1]
        res = get_view_detail(schema=schema, view=view_name, tag=cfg.tag)
        view.append(res)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template("report.html")
    html = template.render(db_name=db_name
                           ,tables=tables
                           ,views=views
                           ,procs=procs
                           ,scalar_funcs=scalar_funcs
                           ,tbl_funcs=tbl_funcs
                           ,status=status
                           ,args=args
                           )

    html_file = f"data_dictionary_{db_name}.html"
    with open(html_file, "w", encoding="utf-8") as fh:
        fh.write(html)


# ===================================================================
# Funciones de Búsqueda en BD
# ===================================================================


def get_tables(tag: str):
    """[[schema, table], [schema, table...]]"""
    
    comando = f"""
    SELECT [schema] = OBJECT_SCHEMA_NAME(so.object_id)
          ,so.name
          ,comment = (SELECT Value
                      FROM ::fn_listextendedproperty ('{tag}', 'Schema', OBJECT_SCHEMA_NAME(so.object_id), 'TABLE', so.name, Null, Null)
                     ) 
    FROM sys.tables  so
    ORDER BY OBJECT_SCHEMA_NAME(so.object_id), so.name
    """
    res = hsql.exec_dictionary(comando)
    if hsql.has_error():
        print("Error 'get_tables'")
        hsql.print_error()
        hsql.clear_error()
        print("")
        return []
    return [[k["schema"], k["name"], isnone(k["comment"], '')] for k in res]
    

def get_views(tag: str):
    """[[schema, view], [schema, view]...]"""
    comando = f"""
    SELECT [schema] = OBJECT_SCHEMA_NAME(so.object_id)
          ,so.name
          ,comment = (SELECT Value
                      FROM ::fn_listextendedproperty ('{tag}', 'Schema', OBJECT_SCHEMA_NAME(so.object_id), 'VIEW', so.name, Null, Null)
                     )
    FROM sys.views so
    ORDER BY OBJECT_SCHEMA_NAME(so.object_id), so.name
    """
    res = hsql.exec_dictionary(comando)
    if hsql.has_error():
        print("Error 'get_views'")
        hsql.print_error()
        hsql.clear_error()
        print("")
        return []
    return [[k["schema"], k["name"], isnone(k["comment"], '')] for k in res]


def get_procs(tag: str):
    """[[schema, proc], [schema, proc]...]"""
    comando = f"""
    SELECT [schema] = OBJECT_SCHEMA_NAME(so.object_id)
          ,so.name
          ,comment = (SELECT Value
                      FROM ::fn_listextendedproperty ('{tag}', 'Schema', OBJECT_SCHEMA_NAME(so.object_id), 'PROCEDURE', so.name, Null, Null)
                     )
    FROM sys.procedures so
    ORDER BY OBJECT_SCHEMA_NAME(so.object_id), so.name
    """
    res = hsql.exec_dictionary(comando)
    if hsql.has_error():
        print("Error 'get_procs'")
        hsql.print_error()
        hsql.clear_error()
        print("")
        return []
    return [[k["schema"], k["name"], isnone(k["comment"], '')] for k in res]


def get_scalar_functions(tag: str):
    """[[schema, func, [schema, func]...]"""
    comando = f"""
    SELECT [schema] = OBJECT_SCHEMA_NAME(so.object_id)
          ,so.name
          ,comment = (SELECT Value
                      FROM ::fn_listextendedproperty ('{tag}', 'Schema', OBJECT_SCHEMA_NAME(so.object_id), 'FUNCTION', so.name, Null, Null)
                     )
    FROM sys.objects  so
    WHERE so.type = 'FN'
    ORDER BY OBJECT_SCHEMA_NAME(so.object_id), so.name
    """
    res = hsql.exec_dictionary(comando)
    if hsql.has_error():
        print("Error 'get_scalar_functions'")
        hsql.print_error()
        hsql.clear_error()
        print("")
        return []
    return [[k["schema"], k["name"], isnone(k["comment"], '')] for k in res]


def get_tbl_functions(tag: str):
    """[[schema, func, [schema, func]...]"""
    comando = f"""
    SELECT [schema] = OBJECT_SCHEMA_NAME(so.object_id)
          ,so.name
          ,comment = (SELECT Value
                      FROM ::fn_listextendedproperty ('{tag}', 'Schema', OBJECT_SCHEMA_NAME(so.object_id), 'FUNCTION', so.name, Null, Null)
                     )
    FROM sys.objects so
    WHERE so.type = 'TF'
    ORDER BY OBJECT_SCHEMA_NAME(so.object_id), so.name
    """
    res = hsql.exec_dictionary(comando)
    if hsql.has_error():
        print("Error 'get_tbl_functions'")
        hsql.print_error()
        hsql.clear_error()
        print("")
        return []
    return [[k["schema"], k["name"], isnone(k["comment"], '')] for k in res]


def get_table_detail(schema: str, table: str, tag: str):
    """[{}...]"""
    comando = f"""
    select 
     --[Schema] = schema_name(tab.schema_id),
     --[Table] = tab.name, 
     [Column] = col.name, 
     --t.name as data_type,    
     [Tipo] =  t.name + 
         case when t.is_user_defined = 0 then 
                   isnull('(' + 
                   case when t.name in ('binary', 'char', 'nchar', 
                             'varchar', 'nvarchar', 'varbinary') then
                             case col.max_length 
                                  when -1 then 'MAX' 
                                  else 
                                       case when t.name in ('nchar', 
                                                 'nvarchar') then
                                                 cast(col.max_length/2 
                                                 as varchar(4)) 
                                            else cast(col.max_length 
                                                 as varchar(4)) 
                                       end
                             end
                        when t.name in ('datetime2', 'datetimeoffset', 
                             'time') then 
                             cast(col.scale as varchar(4))
                        when t.name in ('decimal', 'numeric') then
                              cast(col.precision as varchar(4)) + ', ' +
                              cast(col.scale as varchar(4))
                   end + ')', '')        
              else ':' + 
                   (select c_t.name + 
                           isnull('(' + 
                           case when c_t.name in ('binary', 'char', 
                                     'nchar', 'varchar', 'nvarchar', 
                                     'varbinary') then 
                                      case c.max_length 
                                           when -1 then 'MAX' 
                                           else   
                                                case when t.name in 
                                                          ('nchar', 
                                                          'nvarchar') then 
                                                          cast(c.max_length/2
                                                          as varchar(4))
                                                     else cast(c.max_length
                                                          as varchar(4))
                                                end
                                      end
                                when c_t.name in ('datetime2', 
                                     'datetimeoffset', 'time') then 
                                     cast(c.scale as varchar(4))
                                when c_t.name in ('decimal', 'numeric') then
                                     cast(c.precision as varchar(4)) + ', ' 
                                     + cast(c.scale as varchar(4))
                           end + ')', '') 
                      from sys.columns as c
                           inner join sys.types as c_t 
                               on c.system_type_id = c_t.user_type_id
                     where c.object_id = col.object_id
                       and c.column_id = col.column_id
                       and c.user_type_id = col.user_type_id
                   )
          end,
      [Nullable] = case 
                    when col.is_nullable = 0 then 'N' 
                    else 'Y'
                 end,
      [Default] = case 
                   when def.definition is not null then def.definition 
                   else '' 
                end,
      [PK] = case 
              when pk.column_id is not null then 'PK' 
              else '' 
           end, 
      [FK] = case 
              when fk.parent_column_id is not null then 'FK' 
              else ''
           end, 
      UniqueKey = case 
                     when uk.column_id is not null then 'UK' 
                     else ''
                  end,
      [Check] = case 
                 when ch.check_const is not null then ch.check_const 
                 else ''
              end,
      [Computed] = ISNULL(cc.definition, ''),
      [Comments] = ISNULL(ep.value, '')
 from sys.tables as tab
      left join sys.columns as col
          on tab.object_id = col.object_id
      left join sys.types as t
          on col.user_type_id = t.user_type_id
      left join sys.default_constraints as def
          on def.object_id = col.default_object_id
      left join (
                select index_columns.object_id, 
                       index_columns.column_id
                  from sys.index_columns
                       inner join sys.indexes 
                           on index_columns.object_id = indexes.object_id
                          and index_columns.index_id = indexes.index_id
                 where indexes.is_primary_key = 1
                ) as pk 
          on col.object_id = pk.object_id 
         and col.column_id = pk.column_id
      left join (
                select fc.parent_column_id, 
                       fc.parent_object_id
                  from sys.foreign_keys as f 
                       inner join sys.foreign_key_columns as fc 
                           on f.object_id = fc.constraint_object_id
                 group by fc.parent_column_id, fc.parent_object_id
                ) as fk
          on fk.parent_object_id = col.object_id 
         and fk.parent_column_id = col.column_id    
      left join (
                select c.parent_column_id, 
                       c.parent_object_id, 
                       'Check' check_const
                  from sys.check_constraints as c
                 group by c.parent_column_id,
                       c.parent_object_id
                ) as ch
          on col.column_id = ch.parent_column_id
         and col.object_id = ch.parent_object_id
      left join (
                select index_columns.object_id, 
                       index_columns.column_id
                  from sys.index_columns
                       inner join sys.indexes 
                           on indexes.index_id = index_columns.index_id
                          and indexes.object_id = index_columns.object_id
                  where indexes.is_unique_constraint = 1
                  group by index_columns.object_id, 
                        index_columns.column_id
                ) as uk
          on col.column_id = uk.column_id 
         and col.object_id = uk.object_id
      left join sys.extended_properties as ep 
          on tab.object_id = ep.major_id
         and col.column_id = ep.minor_id
         and ep.name = '{tag}'
         and ep.class_desc = 'OBJECT_OR_COLUMN'
      left join sys.computed_columns as cc
          on tab.object_id = cc.object_id
         and col.column_id = cc.column_id
where tab.schema_id = SCHEMA_ID('{schema}')
  And tab.name = '{table}'
order by --[Schema],
         --[Table], 
         [Column];
    """
    res = hsql.exec_dictionary(comando)
    if hsql.has_error():
        print(f"Error en get_table_detail schema:{schema}, table:{table}")
        hsql.print_error()
        hsql.clear_error()
        print("")
        return {}
    return res
    


def get_view_detail(schema: str, view: str, tag: str):
    """[{}...]"""
    comando = f"""
    select 
       [Columna] = col.name,
       [Tipo] = t.name + 
                case when t.is_user_defined = 0 then 
                            isnull('(' + 
                            case when t.name in ('binary', 'char', 'nchar',
                                    'varchar', 'nvarchar', 'varbinary') then
                                    case col.max_length 
                                        when -1 then 'MAX' 
                                        else 
                                                case 
                                                    when t.name in ('nchar', 
                                                        'nvarchar') then
                                                        cast(col.max_length/2 
                                                        as varchar(4))
                                                    else cast(col.max_length 
                                                        as varchar(4))
                                                end
                                    end
                                when t.name in ('datetime2', 
                                    'datetimeoffset', 'time') then 
                                    cast(col.scale as varchar(4))
                                when t.name in ('decimal', 'numeric') then 
                                    cast(col.precision as varchar(4)) + ', ' +
                                    cast(col.scale as varchar(4))
                            end + ')', '')        
                    else ':' +
                            (select c_t.name + 
                                    isnull('(' + 
                                    case when c_t.name in ('binary', 'char',
                                            'nchar', 'varchar', 'nvarchar',
                                            'varbinary') then
                                            case c.max_length
                                                when -1 then 'MAX'
                                                else case when t.name in
                                                                ('nchar',
                                                                'nvarchar')
                                                            then cast(c.max_length/2
                                                                as varchar(4))
                                                            else cast(c.max_length
                                                                as varchar(4))
                                                        end
                                            end
                                        when c_t.name in ('datetime2', 
                                            'datetimeoffset', 'time') then
                                            cast(c.scale as varchar(4))
                                        when c_t.name in ('decimal', 'numeric') then
                                            cast(c.precision as varchar(4)) +
                                            ', ' + cast(c.scale as varchar(4))
                                    end + ')', '')
                            from sys.columns as c
                                    inner join sys.types as c_t 
                                        on c.system_type_id = c_t.user_type_id
                            where c.object_id = col.object_id
                                and c.column_id = col.column_id
                                and c.user_type_id = col.user_type_id
                            ) 
                end,
        [Nullable] = case 
                        when col.is_nullable = 0 then 'N'
                        else 'Y'
                     end,
        [Comment] = ISNULL(ep.value, '')
    from sys.views as v
        join sys.columns as col
            on v.object_id = col.object_id
        left join sys.types as t
            on col.user_type_id = t.user_type_id
        left join sys.extended_properties as ep 
            on v.object_id = ep.major_id
            and col.column_id = ep.minor_id
            and ep.name = '{tag}'        
            and ep.class_desc = 'OBJECT_OR_COLUMN'
    where v.schema_id = SCHEMA_ID('{schema}')
      And v.name = '{view}'
    order by col.name; 
    """
    res = hsql.exec_dictionary(comando)
    if hsql.has_error():
        print(f"Error en get_view_detail schema:{schema}, table:{view}")
        hsql.print_error()
        hsql.clear_error()
        print("")
        return {}
    return res


def select_db() -> str:
    databases = hsql.get_db_names()

    system_databases = ["master", "model", "tempdb", "msdb"]
    databases = [k for k in databases if k not in system_databases]
    opcion = menu("Seleccione la BD", databases)
    if opcion == -1:
        input(">>")
        return ""
    else:
        return databases[opcion]


if __name__ == "__main__":
    cfg = Config()
    hsql = SQL.HSql(cfg.db_server, cfg.db_user, cfg.db_passwd, cfg.db_origin)
    main()