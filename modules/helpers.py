import os


def isnone(value, value2):
    """Si la primera expresion distinta a None, retorna su valor,
       si es None, retorna el valor de la segunda expreson
    """
    if value is None:
        return value2
    return value


def write_rs_to_csv(dict_var, file_name:str, append:bool):
    """Escribe el contenido de una lista de Diccionarios a un archivo CSV"""

    if len(dict_var) == 0:
        return
    
    mode = 'w' if not append else 'a'
    
    if os.path.exists(file_name):
        if os.stat(file_name).st_size > 0:
            mode = 'a'
            append =True
        else:
            append = False
            mode = 'w'
    else:
        append = False
        mode = 'w'
    
    with open(file_name, mode, newline='') as f:
        w = csv.DictWriter(f, dict_var[0].keys(), delimiter=';')
        if not append:
            w.writeheader()
        
        for row in dict_var:
            w.writerow(row)


def write_list_to_file( lista, archivo):
    with open( archivo, 'w') as f:
        for item in lista:
            f.write(f'{item}\n')


def menu(titulo: str, lista):
    """ Despliega un menú con los elementos de la lista entregada como parámetro.
            Se agrega el elemento "Salir" como último de la lista.
        Retorna:
            Indice de la lista que corresponde al elemento seleccionado
            -1 = Salir
    """
    clear()
    if titulo != '':
        print(f'\n{titulo}')
    else:
        print('\n Menú\n======')

    x: int = 0
    for elem in lista:
        print(f"\t{x+1:2} - {elem}")
        x += 1
    print(f"\t{x+1:2} - Salir")

    print("")
    opcion_menu: int = 0
    while True:
        try:
            opcion_menu = int(input("Ingresa el número de tu Opción >> "))

            if int(opcion_menu) >= 0 and int(opcion_menu) <= len(lista) + 1:
                break

        except ValueError:
            print("Ingrese sólo números")

    if int(opcion_menu) == len(lista)+1:
        print("See you...\n")
        return -1
    else:
        return int(opcion_menu)-1


def menu2(titulo, prompt_salida, lista):
    """ Despliega un menú con los elementos de la lista entregada como parámetro.
            Se agrega el elemento "Salir" como último de la lista.
        Retorna:
            Indice de la lista que corresponde al elemento seleccionado
            -1 = Salir
    """

    clear()
    if titulo != '':
        print(f'\n{titulo}')
    else:
        print('\n Menú\n======')

    x: int = 0
    for elem in lista:
        print(f"\t{x+1:2} - {elem}")
        x += 1
    print(f"\t{x+1:2} - {prompt_salida}")
    
    print("")
    opcion_menu: int = 0
    while True:
        try:
            opcion_menu = int(input("Ingresa el número de la Opción >> "))

            if int(opcion_menu) >= 0 and int(opcion_menu) <= len(lista) + 1:
                break

        except ValueError:
            print("Ingrese sólo números")

    if int(opcion_menu) == len(lista)+1:
        print("See you...\n")
        return -1
    else:
        return int(opcion_menu)-1


def clear():
    """
    Limpiar pantalla de la consola
    """
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")
