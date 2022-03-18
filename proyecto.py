

import re as regex
from textwrap import indent
from binarytree import Node as BinaryTreeNode
import json
import graphviz

class Nodo:
    def __init__(self, value, left=None, right=None):
        self.data = value
        self.left = left
        self.right = right

class AF:
    def __init__(self, exp):
        self.actual_node = None
        self.secondary_roots = [] # ramas secundarias
        self.generate_tree(exp, None)

    # Funcion para poder saber el sub arbol para unirlo despues al arbol principal
    def get_secondary_tree(self, secondary_exp):
        i = 0
        while i < len(secondary_exp):
            if secondary_exp[i] == "(":
                contador = 1
                for j in range(i+1, len(secondary_exp)):
                    if secondary_exp[j] == "(":
                        contador += 1
                    elif secondary_exp[j] == ")":
                        contador -= 1

                    counter = 0 #contador si viene otra cosa despues de )
                    if contador == 0 and secondary_exp[j] == ")":
                        if j + 1 < len(secondary_exp):
                            if secondary_exp[j+1] == "*" or secondary_exp[j+1] == "?":
                                counter += 2

                        end_of_exp = j + counter
                        return end_of_exp
            elif regex.match(r"[a-zA-Z0-9*]", secondary_exp[i]):
                end_of_exp = i
                for j in range(i+1, len(secondary_exp)):
                    if not regex.match(r"[a-zA-Z0-9*]", secondary_exp[j]):
                        break
                    end_of_exp = j
                return end_of_exp
            i += 1

    #Funcion que hace el arbol principal
    def generate_tree(self, secondary_exp, secondary_root_node):
        i = 0
        while i < len(secondary_exp):
            if secondary_exp[i] == "(":
                # Si es el inicio entonces se hace contador de parentesis para que al final tiene que dar 0
                if i == 0:
                    contador = 1
                    for j in range(i+1, len(secondary_exp)):
                        if secondary_exp[j] == "(":
                            contador += 1
                        elif secondary_exp[j] == ")":
                            contador -= 1

                        counter = 0
                        if contador == 0:
                            #Se ve si la expresion alfinal tiene algo despues del ultimo parentesis
                            # Quita parentesis de afuera y vuelve a enviarla a la funcion
                            if secondary_exp[j] == ")" and j + 1 < len(secondary_exp):
                                if secondary_exp[j+1] == "*" or secondary_exp[j+1] == "?":
                                    counter += 2

                            end_of_exp = j + counter
                            init = i + 1
                            self.generate_tree(secondary_exp[init:end_of_exp], secondary_root_node)
                            i = j
                            break
                else:
                    # Si el parentesis esta a la mitad se hace un arbol secundario o temporal
                    if secondary_exp[i-1] == ")" or secondary_exp[i-1] == "*" or secondary_exp[i-1] == "?" or regex.match(r"[a-z]", secondary_exp[i-1]):
                        end_sec_exp = self.get_secondary_tree(secondary_exp[i:])
                        end_of_exp = i + 1 + end_sec_exp
                        self.generate_tree(secondary_exp[i:end_of_exp], len(self.secondary_roots))

                        if secondary_root_node is None:
                            secondary_node = self.secondary_roots.pop()
                        else:
                            secondary_node = self.secondary_roots.pop(secondary_root_node + 1)

                        if secondary_node is not None:
                            self.add_child(secondary_root_node, ".", None, secondary_node, "l")

                        i = i + end_of_exp + 1
            elif regex.match(r"[a-zA-Z0-9#]", secondary_exp[i]):
                # Si es la primer letra de la expresion analizandose
                if ((secondary_root_node is None and self.actual_node is None) or i == 0) and i + 1 < len(secondary_exp) and regex.match(r"[a-zA-Z#]", secondary_exp[i+1]):
                    # Si viene un caso de ab(*, +) en donde primero se hace cerradura de kleen
                    if i + 2 < len(secondary_exp) and (secondary_exp[i+2] == "*" or secondary_exp[i+2] == "?"):
                        self.add_child(secondary_root_node, ".", Nodo(secondary_exp[i]), Nodo(secondary_exp[i+2], Nodo(secondary_exp[i+1]), None), "l")
                        i += 2
                    # Si viene letra entonces se agrega el punto representando la concatenacion
                    else:
                        self.add_child(secondary_root_node, ".", Nodo(secondary_exp[i]), Nodo(secondary_exp[i+1]), "l")
                        i += 1
                # Si es cualquier letra que no sea de inicio Se crea concatenacion con el hijo de la izquierda
                elif (secondary_root_node is None and self.actual_node is not None) or i != 0:
                    self.add_child(secondary_root_node, ".", None, Nodo(secondary_exp[i]), "l")
                # Si no es nada de lo anterior es solo una letra
                else:
                    self.add_child(secondary_root_node, secondary_exp[i], None, None, "l")
                # Si viene concatenacion en parentesis seguida de * o +
                if i + 1 < len(secondary_exp):
                    if secondary_exp[i+1] == "*" or secondary_exp[i+1] == "?":
                        self.add_child(secondary_root_node, secondary_exp[i+1], Nodo(secondary_exp[i]), None, "l")
                    elif secondary_exp[i+1] == ")":
                        if i + 2 < len(secondary_exp):
                            if secondary_exp[i+2] == "*" or secondary_exp[i+2] == "?":
                                self.add_child(secondary_root_node, secondary_exp[i+2], Nodo(secondary_exp[i]), None, "l")
            
            # Si es or o concatenacion agrega el hijo a la derecha
            elif secondary_exp[i] == "|" or secondary_exp[i] == ".":
                end_sec_exp = self.get_secondary_tree(secondary_exp[i+1:])
                end_of_exp = i + 1 + end_sec_exp + 1
                self.generate_tree(secondary_exp[i+1:end_of_exp], len(self.secondary_roots))

                if secondary_root_node is None:
                    secondary_node = self.secondary_roots.pop()
                else:
                    secondary_node = self.secondary_roots.pop(secondary_root_node + 1)

                if secondary_node is not None:
                    self.add_child(secondary_root_node, secondary_exp[i], Nodo(secondary_exp[i-1]), secondary_node, "l")

                if end_of_exp < len(secondary_exp) and secondary_exp[end_of_exp] == ")":
                    if end_of_exp + 1 < len(secondary_exp):
                        if secondary_exp[end_of_exp+1] == "*" or secondary_exp[end_of_exp+1] == "?":
                            self.add_child(secondary_root_node, secondary_exp[end_of_exp+1], Nodo(secondary_exp[end_of_exp+1]), None, "l")

                i = i + end_of_exp + 1
            else:
                print()
            i += 1

    # convertir el arbol a binary tree para poder imprimir y usar despues
    def make_sintact_tree(self):
        return make_tree(self.actual_node)

    def add_child(self, secondary_root_node, values, left, right, is_brother):
        # si es el arbol principal
        if secondary_root_node is None:
            if self.actual_node is None:
                self.actual_node = Nodo(values, left, right)
            else:
                if is_brother == "l":
                    self.actual_node = Nodo(values, self.actual_node, right)
        # si es un arbol secundario
        else:
            if secondary_root_node == len(self.secondary_roots):
                self.secondary_roots.append(Nodo(values, left, right))
            elif secondary_root_node < len(self.secondary_roots):
                if self.secondary_roots[secondary_root_node] is None:
                    self.secondary_roots[secondary_root_node] = Nodo(values, left, right)
                else:
                    if is_brother == "l":
                        self.secondary_roots[secondary_root_node] = Nodo(values, self.secondary_roots[secondary_root_node], right)

    #Funcion anulable
    def anulable(self, node, data):
        # Si es or se hace un or entre el anulable de los hijos
        if data[str(node.value)]["value"] == "|":
            data[str(node.value)]["anulable"] = data[str(node.left.value)]["anulable"] or data[str(node.right.value)]["anulable"]
        # Si es cerradura de kleen es verdadero automaticamente
        elif data[str(node.value)]["value"] == "*":
            data[str(node.value)]["anulable"] = True
        # Si es epsilon es verdadero
        elif data[str(node.value)]["value"] == "E":
            data[str(node.value)]["anulable"] == True
        # Si es concatenacion se hace un and entre el anulable de los hijos
        elif data[str(node.value)]["value"] == ".":
            data[str(node.value)]["anulable"] = data[str(node.left.value)]["anulable"] and data[str(node.right.value)]["anulable"]
        # Si es operador nulo es true
        elif data[str(node.value)]["value"] == "?":
            data[str(node.value)]["anulable"] = True
        # Si es solo una letra es falso
        else:
            data[str(node.value)]["anulable"] = False

    # Funcion primera posicion
    def primera_pos(self, node, data):
        # Si es or entonces se una las primeras posiciones de los hijos
        if data[str(node.value)]["value"] == "|":
            data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"], data[str(node.right.value)]["primera_pos"]] for item in sublist]
        # Si es cerradura de kleen entonces son todos las primera posiciones de su hijo
        elif data[str(node.value)]["value"] == "*":
            data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"]] for item in sublist]
        # Si es cadena vacia entonces no es nada
        elif data[str(node.value)]["value"] == "E":
            data[str(node.value)]["primera_pos"] = []
        # Si es concatenacion se evalua si el hijo de la izquierda es anulable
        # Si si lo es entonces se unen los primeras posiciones de los hijos
        # Si no entonces solo es la primera posicion del hijo izquierdo
        elif data[str(node.value)]["value"] == ".":
            if data[str(node.left.value)]["anulable"]:
                data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"], data[str(node.right.value)]["primera_pos"]] for item in sublist]
            else:
                data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"]] for item in sublist]
        # Si es nulo entonces es la union de las primeras posiciones de los hijos
        elif data[str(node.value)]["value"] == "?":
            data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"], data[str(node.right.value)]["primera_pos"]] for item in sublist]
        # Si es letra entonces la primera posicion es la letra
        else:
            data[str(node.value)]["primera_pos"] = [node.value]
    
    def ultima_pos(self, node, data):
        # Si es or entonces es la union de las ulitmas posiciones de los hijos
        if data[str(node.value)]["value"] == "|":
            data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"], data[str(node.right.value)]["ultima_pos"]] for item in sublist]
        # Si es cerradura de kleen entonces es la ultima posicion de su hijo
        elif data[str(node.value)]["value"] == "*":
            data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"]] for item in sublist]
        # Si es cadena vacia entonces no es nada
        elif data[str(node.value)]["value"] == "E":
            data[str(node.value)]["ultima_pos"] = []
        # Si es concatenecion se ve si el hijo de la derecha es anulable
        # Si si entonces es la union de las ultimos posiciones de los hijos
        # Si no entonces solo es la ultima posicion del hijo derecho
        elif data[str(node.value)]["value"] == ".":
            if data[str(node.right.value)]["anulable"]:
                data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"], data[str(node.right.value)]["ultima_pos"]] for item in sublist]
            else:
                data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.right.value)]["ultima_pos"]] for item in sublist]
        # Si es operador nulo entonces es la union de las ultimas posiciones de sus hijos
        elif data[str(node.value)]["value"] == "?":
            data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"], data[str(node.right.value)]["ultima_pos"]] for item in sublist]
        # Si es letra entonces la ultima posicion es el valor de esta
        else:
            data[str(node.value)]["ultima_pos"] = [node.value]

    # Funcion siguiente posicion 
    def siguiente_pos(self, node, data):
        # Si es cerradura de kleen entonces las pimeras posiciones del hijo
        # Se agregan a cada ultima posicion del hijo como siguiente posicion
        if data[str(node.value)]["value"] == "*":
            for up in data[str(node.left.value)]["ultima_pos"]:
                for pp in data[str(node.left.value)]["primera_pos"]:
                    if pp not in data[str(node.left.value)]["siguiente_pos"]:
                        data[str(up)]["siguiente_pos"].append(pp)
        # Si es concatenacion entonces las primeras posiciones del hijo de la derecha
        # Se ponen en cada una de las ultimas posiciones del hijo de la izquierda como siguiente posicion
        elif data[str(node.value)]["value"] == ".":
            for up in data[str(node.left.value)]["ultima_pos"]:
                for pp in data[str(node.right.value)]["primera_pos"]:
                    if pp not in data[str(node.left.value)]["siguiente_pos"]:
                        data[str(up)]["siguiente_pos"].append(pp)

    # Funcion para hacer la tabla de transiciones
    def transiciones(self, trans, tree, data, alfabeto):
        # Contador para estados en 0
        contador = 0
        # Se crea el estado inicial el cual esta compuesto por las primeras posiciones de la raiz
        # Se le agrega como nombre S0
        trans[str(data[str(tree.value)]["primera_pos"])] = {
            "name": "S"+str(contador),
        }
        # Se le agrega los caracteres con los que se puede hacer transicion
        for letra in alfabeto:
            trans[str(data[str(tree.value)]["primera_pos"])][letra] = None
        # Se suma al contador para el siguiente estado
        contador += 1

        # While para completar la tabla de transiciones
        cont = True
        while(cont):
            # Largo inicial de tabla de estos
            initial_size = len(trans)
            keys = list(trans.keys())
            # Se itera sobre las llaves que representa cada estado del AFD
            for key in keys:
                # Se itera entre los caracteres para iteraciones para ir llenando cada estado con sus transiciones
                for letra in alfabeto:
                    # Si no hay una transicion hecha para ese caracter 
                    if trans[key][letra] == None:
                        # Lista de los identificadores que representan al caracter
                        new_state = []
                        # Se para de str a una lista con los identificadores que hay en ese estado
                        current_state = key.replace("[","")
                        current_state = current_state.replace("]","")
                        current_state = current_state.replace(" ","")
                        current_state = current_state.split(",")
                        # Si el identificador representa al caracter para la transicion se agregan las siguientes posiciones de esta al nuevo estado
                        for i in current_state:
                            if data[str(i)]["value"] == letra:
                                new_state.append(data[str(i)]["siguiente_pos"])
                        # se vuelve una sola lista y se ordena el nuevo estado
                        new_state = [item for sublist in new_state for item in sublist]
                        new_state = list(set(new_state))
                        new_state.sort()
                        if len(new_state) > 0:
                            # Si el estado nuevo no tienen ya una representaicone en la tabla
                            # Entonces se agrega a la tabla y se le crea su estado
                            if str(new_state) not in trans:
                                trans[str(new_state)] = {
                                    "name": "S"+str(contador)
                                }
                                for letter in alfabeto:
                                    trans[str(new_state)][letter] = None
                                contador +=1
                            # Se agrega este nuevo nombre del nuevo estado al la transicion del estado que se esta recorriendo acutalmente
                                trans[key][letra] = trans[str(new_state)]["name"]
                            else:
                                trans[key][letra] = trans[str(new_state)]["name"]
            # se vuelve a ver el valor de la tabla si cambio el valor al inicial se sigue en el while
            final_size = len(trans)
            if initial_size == final_size:
                # Si no cambio el valor de la tabal se confirma que todos los valores de transiciones esten llenos y no haya ninguno con vacio
                cont = not all(trans.values())

    # Algoritmo para simular un AFD
    # Para el algoritmo de pasar de exp a AFD
    def simulacion(self, trans, cadena, final_char, alfabeto):
        # Se empieza en estado 0
        current_state = "S0"
        cadena = cadena.replace("E","")
        for char in cadena:
            if char not in alfabeto:
                return False
        # Se recorre la cadena
        if cadena != "":
            for char in cadena:
                llave = ""
                # Se recorre la tabla de transiciones para buscar el estado que tiene esta transicion
                for key, v in trans.items():
                    # Si si hay una transicion con este caracter para el estado actual se guarda el estado
                    if v["name"] == current_state and v[char] != None:
                        llave = key
                    # Si no siginifica que no acepta la cadena
                    elif v["name"] == current_state and v[char] == None:
                        return False
                # Se cambia al nuevo estado
                current_state = trans[llave][char]
        # Ya finalizado de recorrer y con un estado final se comprueba si es de aceptacion
        for key, v in trans.items():
            # Se recorre la tabla y si el # se encuentra en los valores de este estado se acepta
            if v["name"] == current_state:
                chars = key.replace("[","")
                chars = chars.replace("]","")
                chars = chars.replace(" ","")
                chars = chars.split(",")
                if final_char in chars:
                    return True
                else:
                    return False

    # Algoritmo thompson para pasar de exp a AFN                 
    def thompson(self, tree, data, alfabeto, trans):
        #Primero se generan los estados finales e iniciales de cada nodo
        contador = 1 
        for nodo in tree.postorder:
            # Si es or se agregan dos nuevos estados
            if data[str(nodo.value)]["value"] == "|":
                data[str(nodo.value)]["initial_state"] = "S"+str(contador)
                contador += 1
                data[str(nodo.value)]["final_state"] = "S"+str(contador)
                contador += 1
            # Si es concatenacion entonces el estado inicial del hijo derecho es el final del izquierdo
            # El estado inicial de la concatenacion es el estado inicial de hijo izquierdo
            # El estado final de la concatenacion es el estado final del hijo derecho
            elif data[str(nodo.value)]["value"] == ".":
                data[str(nodo.right.value)]["initial_state"] = data[str(nodo.left.value)]["final_state"] 
                data[str(nodo.value)]["initial_state"] = data[str(nodo.left.value)]["initial_state"]
                data[str(nodo.value)]["final_state"] = data[str(nodo.right.value)]["final_state"]
            # Si es cerradura de kleen se agregan dos nuevos estados
            elif data[str(nodo.value)]["value"] == "*":
                data[str(nodo.value)]["initial_state"] = "S"+str(contador)
                contador += 1
                data[str(nodo.value)]["final_state"] = "S"+str(contador)
                contador += 1
            # Si es otra cosa se agregan dos nuevos estados
            else:
                data[str(nodo.value)]["initial_state"] = "S"+str(contador)
                contador += 1
                data[str(nodo.value)]["final_state"] = "S"+str(contador)
                contador += 1
        
        #Estado inicial es siempre cero 
        s0 = {
            "initial_state": "S0",
            "final_state": "S1"
        }
        #Dibujar AFN y llenar tabla de transiciones del AFN
        dot = graphviz.Digraph(comment="AFN", format="png")
        dot.attr(rankdir="LR")

        # Se le agrega al diccionario todos los posibles caracteres para transiciones
        for i in range(contador):
            trans["S"+str(i)]={}
            for letra in alfabeto:
                trans["S"+str(i)][letra] = []

        # Se recoore el arbol en postorder para poder dibujar y hacer la tabla
        for nodo in tree.postorder:
            # Si es or entonces su estado inicial se conecta con el de los hijos
            # El final de los hijos se conecta con el del or
            if data[str(nodo.value)]["value"] == "|":
                #Condicion para cambiar el estado final de S0 si hay or
                if data[str(nodo.left.value)]["initial_state"] == s0["final_state"]:
                    s0["final_state"] = data[str(nodo.value)]["initial_state"]

                dot.node(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["initial_state"], shape='circle')
                dot.node(data[str(nodo.left.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"], shape='circle')
                dot.node(data[str(nodo.right.value)]["initial_state"], data[str(nodo.right.value)]["initial_state"], shape='circle')
                dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"], label="E")
                trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.left.value)]["initial_state"])

                dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.right.value)]["initial_state"], label="E")
                trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.right.value)]["initial_state"])

                if data[str(nodo.value)]["final_state"] == "S"+str(contador-1):
                    dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"], shape='doublecircle')
                else:
                    dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"], shape='circle')
                dot.node(data[str(nodo.left.value)]["final_state"], data[str(nodo.left.value)]["final_state"], shape='circle')
                dot.node(data[str(nodo.right.value)]["final_state"], data[str(nodo.right.value)]["final_state"], shape='circle')
                dot.edge(data[str(nodo.left.value)]["final_state"], data[str(nodo.value)]["final_state"], label="E")
                trans[data[str(nodo.left.value)]["final_state"]]["E"].append(data[str(nodo.value)]["final_state"])

                dot.edge(data[str(nodo.right.value)]["final_state"], data[str(nodo.value)]["final_state"], label="E")
                trans[data[str(nodo.right.value)]["final_state"]]["E"].append(data[str(nodo.value)]["final_state"])

            # Si es cerradura de kleen se conecta su estado inicial con el del hijo
            # El estado final del hijo con el de kleen
            elif data[str(nodo.value)]["value"] == "*":
                # Condicion para cambiar el estado final de 0 si viene kleen
                if data[str(nodo.left.value)]["initial_state"] == s0["final_state"]:
                    s0["final_state"] = data[str(nodo.value)]["initial_state"]
                dot.node(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["initial_state"], shape='circle')
                dot.node(data[str(nodo.left.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"], shape='circle')
                dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"], label="E")
                trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.left.value)]["initial_state"])

                if data[str(nodo.value)]["final_state"] == "S"+str(contador-1):
                    dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"], shape='doublecircle')
                else:
                    dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"], shape='circle')
                dot.node(data[str(nodo.left.value)]["final_state"], data[str(nodo.left.value)]["final_state"], shape='circle')
                dot.edge(data[str(nodo.left.value)]["final_state"], data[str(nodo.value)]["final_state"], label="E")
                trans[data[str(nodo.left.value)]["final_state"]]["E"].append(data[str(nodo.value)]["final_state"])

                dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["final_state"], label="E")
                trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.value)]["final_state"])

                dot.edge(data[str(nodo.left.value)]["final_state"], data[str(nodo.left.value)]["initial_state"], label="E")
                trans[data[str(nodo.left.value)]["final_state"]]["E"].append(data[str(nodo.left.value)]["initial_state"])
            # Si es concatenacion no hago nada ya que sus hijos lo hacen
            elif data[str(nodo.value)]["value"] == ".":
                print()
            # si es otra cosa se hace transicion entre su estado final a inicial
            else:
                dot.node(str(data[str(nodo.value)]["initial_state"]),data[str(nodo.value)]["initial_state"], shape='circle')
                if str(data[str(nodo.value)]["final_state"]) == "S"+str(contador-1):
                    dot.node(str(data[str(nodo.value)]["final_state"]), data[str(nodo.value)]["final_state"], shape='doublecircle')
                else:
                    dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"], shape='circle')
                dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["final_state"], label=data[str(nodo.value)]["value"])
                trans[data[str(nodo.value)]["initial_state"]][data[str(nodo.value)]["value"]].append(data[str(nodo.value)]["final_state"])

        # Luego hago las transiciones de so a su estado final
        dot.node(s0["initial_state"], s0["initial_state"], shape='circle')
        dot.edge(s0["initial_state"], s0["final_state"], label="E")
        trans[s0["initial_state"]]["E"].append(s0["final_state"])

        dot.render(directory='automatas', filename='Thompson-AFN')
        # regreso el contador porque me sirve para saber cuantos estados se crearon al final
        return contador

    #Cerradura de epsilon devuelve los estados a los que puedo ir con E
    def cerraduraEpsilon(self, state, trans, states = []):
        if state not in states:
            states.append(state)
        if (len(trans[state]["E"]) > 0):
            for current_state in trans[state]["E"]:
                if current_state not in states:
                    states.append(current_state)
                self.cerraduraEpsilon(current_state, trans, states)
        return states

    #Mover devuelve los estados a los que puedo ir de un conjunto de estados con un caracter
    def mover(self, states, caracter, trans):
        moved_states = []
        for state in states:
            for k, v in trans.items():
                if k == state:
                    if len(v[caracter]) > 0:
                        for current_state in v[caracter]:
                            if current_state not in moved_states:
                                moved_states.append(current_state)
        return moved_states

    # Cerradurade epsilon S  es para estos devuelve los conjuntos con los que se puede ir con E de un conjunto de estados
    def cerraduraEpsilonS(self, all_states, trans):
        final_states = []
        for current_state in all_states:
            new_states = []
            new_states = self.cerraduraEpsilon(current_state, trans, [])
            final_states.append(new_states)

        final_states = [item for sublist in final_states for item in sublist]
        final_states = list(set(final_states))
        final_states.sort()
        return final_states     

    #Funcion para simular AFN
    def simulacionAFN(self, cadena, trans, final_state, alfabeto):

        for char in cadena:
            if char not in alfabeto:
                return False
        #Cerradura del primer estado
        states = self.cerraduraEpsilon("S0", trans, [])
        contador = 1
        #End of file caracter
        cadena += "#"
        c = cadena[0]
        #mientras no sea el final 
        while c != "#":
            #Cerradura de epsilon de conjuntos para mover con el caracter evaluandose
            states = self.cerraduraEpsilonS(self.mover(states, c, trans), trans)
            # Se cambia de caracter
            c = cadena[contador]
            contador += 1
        #Si el estado final se encuentra en los estados que se tienen al final pertenece
        if final_state in states:
            return True
        else:
            return False

    #Algoritmo de subconjuntos
    def subconjuntos(self, trans, data, alfabeto):
        #Se le quita E del los posibles transiciones porque AFD no tienen E
        contador = 0
        alfabeto.remove("E")
        # Cerradura de epsilon del primer estado
        cerradura = self.cerraduraEpsilon("S0", trans, [])
        cerradura.sort()
        #Se crea su entrada en la tabla de transiciones
        data[str(cerradura)] = {
            "name": str(contador),
        }
        for letra in alfabeto:
            data[str(cerradura)][letra] = None
        contador += 1
        cont = True
        #While mientras la tabla no este llena
        while(cont):
            initial_size = len(data)
            keys = list(data.keys())
            #Se recorre la tabla
            for key in keys:
                #Se recorre los caracteres para transiciones
                for letra in alfabeto:
                    if data[key][letra] == None:
                        new_state = []
                        current_state = key.replace('[','')
                        current_state = current_state.replace(']','')
                        current_state = current_state.replace(' ','')
                        current_state = current_state.split(',')
                        state = []
                        for i in current_state:
                            i = i.replace("'",'')
                            state.append(i)
                        new_state = self.cerraduraEpsilonS(self.mover(state, letra, trans), trans)
                        # Si existe una transiciones
                        if len(new_state) > 0:
                            #Si no estan en la tabla se agrega como una nueva entrada 
                            if str(new_state) not in data:
                                data[str(new_state)] = {
                                    "name": str(contador)
                                }
                                for letter in alfabeto:
                                    data[str(new_state)][letter] = None
                                contador +=1
                                # se le asigna el valor de esta nueva entrada como el estado de la que se estaba evaluando
                                data[key][letra] = data[str(new_state)]["name"]
                            else:
                                data[key][letra] = data[str(new_state)]["name"]
            # si se agrego una entrada se continua
            final_size = len(data)
            if initial_size == final_size:
                #Si ya esta todo lleno se sale
                cont = not all(data.values())
        return data

    #Simulacion AFD
    def simulacionAFD(self, trans, cadena, final_char, alfabeto):
        #Se recorre y si hay una transicion para el estado actual se actualiza 
        current_state = "0"
        cadena = cadena.replace("E","")
        for char in cadena:
            if char not in alfabeto:
                return False
        if cadena != "":
            for char in cadena:
                llave = ""
                for key, v in trans.items():
                    if v["name"] == current_state and v[char] != None:
                        llave = key
                    elif v["name"] == current_state and v[char] == None:
                        return False
                current_state = trans[llave][char]
        #Se ve que caracteres estan en el estados final si se encuentra el # pertenece
        for key, v in trans.items():
            if v["name"] == current_state:
                states = key.replace("[","")
                states = states.replace("]","")
                states = states.replace(" ","")
                states = states.split(",")
                st = []
                for i in states:
                    i = i.replace("'",'')
                    st.append(i)
                if final_char in st:
                    return True
                else:
                    return False

# Pasa el arbol a un binary tree para poder usarlo mas facil
def make_tree(node, root=None):
        if root is None:
            root = BinaryTreeNode(ord(node.data))

        if node.left is not None and node.left.data is not None:
            root.left = BinaryTreeNode(ord(node.left.data))
            make_tree(node.left, root.left)

        if node.right is not None and node.right.data is not None:
            root.right = BinaryTreeNode(ord(node.right.data))
            make_tree(node.right, root.right)

        return root

#Quita el caracter de +
def remove_cerr_pos(r):
    for c in range(0, len(r), 1):
        if r[c] == "+":
            subr = r[:c]
            postr = r[c+1:]
            contador = 0
            subs = ""
            i = len(subr) - 1
            while(i >= 0):
                if r[i] == ")":
                    contador += 1
                    if contador == 1:
                        i -= 1
                    else:
                        subs = r[i] +subs
                        i-=1

                elif r[i] =="(":
                    contador -= 1
                    if contador == 0 :
                        i=-1
                    else:
                        subs = r[i] + subs
                        i-=1
                else:
                    if contador != 0:
                        subs = r[i] +subs
                        i-=1
                    else:
                        subs = r[i]
                        i=-1
            if len(subs) == 1:
                return subr+"*"+subs+postr
            else:
                return subr+"*("+subs+")"+postr

def remove_nulo(r):
    for c in range(0, len(r), 1):
        if r[c] == "?":
            subr = r[:c]
            postr = r[c+1:]
            contador = 0
            subs = ""
            i = len(subr) -1
            while (i>=0):
                if r[i] == ")":
                    contador += 1
                    if contador == 1:
                        i -= 1
                    else:
                        subs = r[i] +subs
                        subr = subr[:-1]
                        i-=1

                elif r[i] =="(":
                    contador -= 1
                    if contador == 0 :
                        i=-1
                    else:
                        subs = r[i] + subs
                        subr = subr[:-1]
                        i-=1
                else:
                    if contador != 0:
                        subs = r[i] +subs
                        subr  = subr[:-1]
                        i-=1
                    else:
                        subs = r[i]
                        subr = subr[:-1]
                        i=-1
            if len(subs) == 1:
                subr = subr[:-2]
                return subr+"("+subs+"|E)"+postr
            else:
                subr = subr[:-2]
                return subr+"("+subs+"|E)"+postr



if __name__ == "__main__":

    re = input('Ingrese la expresion regular: ')
    cadena = input('Ingrese la cadena a probar: ')

    # if "?" in re:
    #     re = remove_nulo(re)
    while( "+" in re):
        re = remove_cerr_pos(re)
    while( "?" in re):
        re = remove_nulo(re)
    # re ="a|b"
    print(re)
    af = AF(re)

    

    tree = af.make_sintact_tree()


    algoritmo = input("""
        Menu:
        1. Thompson y subconjuntos
        2. Exp a AFD

        Elija un numero: 
    """)

    if algoritmo == "1":
        af = AF(re)
        tree = af.make_sintact_tree()
        #diccionario para estados iniciales y finales de cada nodo
        data = {}
        #Tabla de transiciones de afn
        trans={}
        #Tabla de transiciones de afd
        datos = {}
        #Simbolos que son operadores
        letras='*|?+E'
        #Lista de las hojas del arbol
        alfabeto=[]
        arbolito = tree
        contador = 1
        #Se inicializa el diccionario para estados iniciales y finales con la cantidad de nodos que hay
        for j in tree.postorder:
            data[str(contador)] = {
                "value": chr(j.value),
                "initial_state": None,
                "final_state": None,
            }
            j.value = contador
            contador +=1
        # Se llena la lista con los caracteres de las hojas del arbol
        for hoja in arbolito.leaves:
            for letra in letras:
                if letra != data[str(hoja.value)]["value"]:
                    if data[str(hoja.value)]["value"] not in alfabeto:
                        alfabeto.append(data[str(hoja.value)]["value"])
        alfabeto.sort()
        #Se le agrega E cadena vacia
        if "E" not in alfabeto:
            alfabeto.append("E")
        print(arbolito)

        #Se hace thompson
        final_state = af.thompson(arbolito, data, alfabeto, trans)

        #Se simula el AFN
        resultadoAFN = af.simulacionAFN(cadena, trans, "S"+str(final_state-1), alfabeto)

        #Se hace subconjuntos
        af.subconjuntos(trans, datos, alfabeto)
        
        #Se dibuja el AFD
        afd = graphviz.Digraph(comment="AFD", format='png')
        afd.attr(rankdir="LR")

        #Se crean los nodos
        for key in datos.keys():
            states = key.replace("[","")
            states = states.replace("]","")
            states = states.replace(" ","")
            states = states.split(",")
            st = []
            for i in states:
                i = i.replace("'",'')
                st.append(i)
            if ("S"+str(final_state-1)) in st:
                afd.node(datos[key]["name"], datos[key]["name"], shape='doublecircle')
            else:
                afd.node(datos[key]["name"], datos[key]["name"])
                
        # Se hacen las transiciones
        for key, v in datos.items():
            for c in alfabeto:
                if v["name"] != None and v[c] != None:
                    states = key.replace("[","")
                    states = states.replace("]","")
                    states = states.replace(" ","")
                    states = states.split(",")
                    if ("S"+str(final_state-1)) in states:
                        afd.node(v["name"], v["name"],  shape='doublecircle')
                    else:
                        afd.node(v["name"], v["name"])
                    afd.node(v[c], v[c])
                    afd.edge(v["name"], v[c], c)

        #Se dibuja
        afd.render(directory='automatas', filename='Subconjuntos-AFD')

        #Se simula el AFD
        resultadoAFD = af.simulacionAFD(datos, cadena, "S"+str(final_state-1), alfabeto)

        #Resultados de salida
        if resultadoAFN:
            print('La cadena si pertenece en el AFN')
        else:
            print('La cadena no pertenece en el AFN')

        if resultadoAFD:
            print('La cadena si pertenece en el AFD')
        else:
            print('La cadena no pertenece en el AFD')

    # Si es de forma directa
    elif algoritmo == "2":
        re = "("+re+")#" # Se agrega #

        #Se hace el arbol
        af = AF(re)
        tree = af.make_sintact_tree()

        print(tree)
        #Diccionario con la data para cada nodo anulable, primera pos...
        data = {}
        #Tabla de transiciones
        transiciones= {}
        #operadores
        letras='*|?+'
        #Caracteres en hojas de arbol
        alfabeto=[]
        arbol = tree
        contador = 1
        #Se llena el diccionario de datos con la cantidad de nodos
        for i in arbol.postorder:
            data[str(contador)] = {
                "value": chr(i.value),
                "node_value": i.value,
                "anulable": None,
                "primera_pos": None,
                "ultima_pos": None,
                "siguiente_pos": [],
                "is_leaf": False,
            }
            i.value = contador
            contador +=1
        #Se obtienen los caracteres de las hojas
        for hoja in arbol.leaves:
            for letra in letras:
                if letra != data[str(hoja.value)]["value"]:
                    if data[str(hoja.value)]["value"] not in alfabeto:
                        alfabeto.append(data[str(hoja.value)]["value"])
        alfabeto.sort()
        print(arbol)
        for j in arbol.leaves:
            data[str(j.value)]["is_leaf"] = True

        # Se hacen las fuciones anulable, primera pos, ultimo pos y siguiente pos para llenar la data
        for node in arbol.postorder:
            af.anulable(node, data)
            af.primera_pos(node, data)
            af.ultima_pos(node, data)
            af.siguiente_pos(node, data)
        
        #Se llena la tabla de transiciones
        af.transiciones(transiciones, arbol, data, alfabeto)
        # Se simula el afd
        resultado = af.simulacion(transiciones, cadena, str(arbol.right.value), alfabeto)

        #Resultado
        if resultado:
            print("La cadena pertenece")
        else:
            print("La cadena no pertenece")

        #Se dibuja el afd
        dot = graphviz.Digraph(comment="AFD", format='png')
        dot.attr(rankdir="LR")

        #Se hacen los nodos
        for key in transiciones.keys():
            states = key.replace("[","")
            states = states.replace("]","")
            states = states.replace(" ","")
            states = states.split(",")
            if str(arbol.right.value) in states:
                dot.node(transiciones[key]["name"], transiciones[key]["name"], shape='doublecircle')
            else:
                dot.node(transiciones[key]["name"], transiciones[key]["name"], shape='circle')
                
        #Se hacen las transiciones
        for key, v in transiciones.items():
            for c in alfabeto:
                if v["name"] != None and v[c] != None:
                    dot.edge(v["name"], v[c], c)

        dot.render(directory='automatas', filename='Directo-AFD')
