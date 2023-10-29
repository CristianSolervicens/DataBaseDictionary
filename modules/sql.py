import codecs
import os

import chardet
import pymssql

if __name__ == '__main__':
    print('')
    print('No es ejecutable')
    print("Módulo de funciones para simplificar el acceso a SQL Server")
    print('')


class HSql:
    """
    Clase para simplificar el acceso a la Base de Datos SQL Server
    Cada llamada es una Conexión a la BD
    """

    def __init__(self, server: str, user: str, pwd: str, dbname: str, db_port=1433):
        """Constructor"""
        self.server = server
        self.user = user
        self.pwd = pwd
        self.dbname = dbname
        self.db_port = db_port
        self.conn = None
        self.error = None


    def has_error(self):
        """Retorna True si la ultima sentencia genero un Error"""
        return True if self.error is not None else False


    def clear_error(self):
        """Limpia el Estado de Error"""
        self.error = None


    def print_error(self):
        """Imprime el Ultimo Error SQL que se ha producido."""

        if self.error is not None:
            print()
            print(
                f'Error SQL : {self.error["Database"]}\nServer    : {self.server}\nMensaje   : {self.error["Mensaje"]}')
            print()


    def connect(self) -> bool:
        """Se conecta al SQL definido"""
        if self.conn is not None:
            return True

        try:
            self.conn = pymssql.connect(self.server, self.user, self.pwd, self.dbname)
            self.conn.autocommit(True)
        except pymssql.StandardError as err:
            self.error = {"Database": self.dbname,
                          "Mensaje": str(err)}
            return False
        return True

    def disconnect(self):
        try:
            self.conn.close()
            self.conn = None
        except:
            pass


    def get_object(self, objeto: int, database='') -> str:
        """
        Obtiene el texto de definicion de un objeto de la Base de Datos
        (Procedure, Function, View, Trigger)
        """
        if self.error is not None:
            print('SQL En estado de Error')
            return ''

        if self.conn is None:
            self.connect()

        if self.has_error():
            return 'Error'

        _database = self.dbname
        if database != '' and _database != database:
            self.use_db(database)

        salida = ""
        query = f"SELECT OBJECT_DEFINITION(OBJECT_ID(N'{objeto}'))"
        # print("getObject " + query)
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(query)
                for row in cursor:
                    salida += row[0] if row[0] else ''
            except pymssql.StandardError as err:
                self.error = {"Database": self.dbname, "Mensaje": str(err)}
                return 'Error'

        salida = salida.replace('\r', '')
        return salida.strip().replace('\n\n', '\n')


    def exec_dictionary(self, comando: str, database=''):
        """
        Ejecuta un comando SQL y retorna la salida como diccionario
        """
        if self.error is not None:
            print('SQL En estado de Error')
            return dict()

        if self.conn is None:
            self.connect()

        _database = self.dbname
        if database != '' and _database != database:
            self.use_db(database)

        # print(f'Conexión: {self.server} {self.user} {self.pwd}')
        cursor = self.conn.cursor(as_dict=True)

        try:
            cursor.execute(comando)
        except pymssql.StandardError as err:
            self.error = {"Database": self.dbname, "Mensaje": str(err)}
            return []
        except Exception as ex:
            self.error = {"Database": self.dbname, "Mensaje": str(ex)}
            return []

        rows = []
        for row in cursor:
            nrow = {k.lower(): v.decode("utf-8") if isinstance(v, bytes) else v for k, v in row.items()}
            rows.append(nrow)

        return rows


    def exec_dictionary_multiple_rs(self, comando: str, database=''):
        """Ejecuta SQL que Retorna múltiples Result Sets"""

        if self.error is not None:
            print('SQL En estado de Error')
            return dict()

        if self.conn is None:
            self.connect()

        _database = self.dbname
        if database != '' and _database != database:
            self.use_db(database)

        # print(f'Conexión: {self.server} {self.user} {self.pwd}')
        cursor = self.conn.cursor(as_dict=True)

        try:
            cursor.execute(comando)
        except pymssql.StandardError as err:
            self.error = {"Database": self.dbname, "Mensaje": str(err)}
            return []

        resultSets = 0
        multipleRs = []
        while True:
            rows = []
            for row in cursor:
                nrow = {k.lower(): v.decode("utf-8") if isinstance(v, bytes) else v for k, v in row.items()}
                rows.append(nrow)
            print(f'Rows {rows}')
            multipleRs.append(rows)
            if not cursor.nextset():
                resultSets += 1
                break

        return resultSets, multipleRs


    def use_db(self, dbname: str) -> bool:
        """Se ubica en la BD especificada"""

        if self.error is not None:
            print('SQL En estado de Error')
            return False

        if self.conn is None:
            self.connect()

        comando = "USE " + dbname

        with self.conn.cursor() as cursor:
            try:
                cursor.execute(comando)
            except pymssql.StandardError as err:
                self.error = {"Database": self.dbname, "Mensaje": str(err)}
                return False

        return True


    def exec_no_result(self, comando, database='') -> bool:
        """
        Ejecuta un comando SQL que no trae resultados
        Retorna: None
        """

        if self.error is not None:
            print('SQL En estado de Error')
            return False

        if self.conn is None:
            self.connect()

        _database = self.dbname
        if database != '' and _database != database:
            self.use_db(database)

        with self.conn.cursor() as cursor:
            try:
                cursor.execute(comando)
            except pymssql.StandardError as err:
                self.error = {"Database": self.dbname, "Mensaje": str(err)}
                return False

        return True


    def get_db_names(self, ) -> list:
        """
        Retorna una lista con los nombres de todas las BD's del Sistema
        """
        databases = []
        comando = "SELECT name FROM sys.databases"
        if self.error is not None:
            print('SQL En estado de Error')
            return []

        if self.conn is None:
            self.connect()

        try:
            res = self.exec_dictionary(comando)
            databases = [k['name'] for k in res]

        except pymssql.StandardError as err:
            self.error = {"Database": self.dbname, "Mensaje": str(err)}
            return []

        return databases

    def get_date(self, ) -> str:
        """
        Retorna la Fecha desde SQL Server
        """

        if self.error is not None:
            print('SQL En estado de Error')
            return ''

        if self.conn is None:
            self.connect()

        if self.conn is None:
            self.error = f'No es posible conectarse al servidor {self.dbname}'
            return ''

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT getdate() as fecha")
            res = cursor.fetchone()
            return res[0]
        except pymssql.StandardError as err:
            self.error = {"Database": self.dbname, "Mensaje": str(err)}
            return ''


def read_sql_file(fileName: str) -> list:
    """
    Lee un archivo de texto retornando las secciones de este que están separadas
    por una línea que contiene la palabra "GO"
    """
    if not os.path.isfile(fileName):
        return []

    rawdata = open(fileName, 'rb').read()
    result = chardet.detect(rawdata)
    charenc = result['encoding']
    del rawdata

    result = []
    with codecs.open(fileName, 'r', charenc) as f:
        comando = ""
        for line in f:
            if line.strip().upper() == "GO":
                result.append(comando)
                comando = ""
            else:
                comando += line

        if not comando == "":
            result.append(comando)

    return result


def parse_command(comando: str):
    """Parsea un script SQL en sus sentencias separadas por 'GO'"""
    result = []

    comando = comando.casefold().replace("\ngo\n", "\ngo\n")
    # comando = comando.replace("\nGo\n", "\ngo\n")
    # comando = comando.replace("\ngO\n", "\ngo\n")
    result = comando.split("\ngo\n")

    return result

# FIN DEL ARCHIVO
