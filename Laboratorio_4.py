from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QTextEdit, QFileDialog, \
    QLineEdit, QMessageBox, QInputDialog, QTextBrowser
import sys
import json
import os
import math

class Persona:
    def __init__(self, nombre, dpi, date_birth, address, empresas = "", cartas_comprimidas = "", cartas_descomprimidas = ""):
        self.nombre = nombre
        self.dpi = dpi
        self.date_birth = date_birth
        self.address = address
        self.empresas = empresas
        self.cartas_comprimidas = cartas_comprimidas
        self.cartas_descomprimidas = cartas_descomprimidas

class Nodo:
    def __init__(self, esHoja=False):
        self.claves = []
        self.hijos = []
        self.hoja = esHoja

class ArbolB:
    def __init__(self, grado):
        self.grado = grado
        self.raiz = Nodo(True)

    def insertar(self, persona):
        raiz = self.raiz
        if len(raiz.claves) == (2 * self.grado) - 1:
            temp = Nodo()
            temp.hijos.append(raiz)
            self.raiz = temp
            self.dividir(temp, 0)
        self.insertar_no_lleno(self.raiz, persona)

    def insertar_no_lleno(self, nodo, persona):
        i = len(nodo.claves) - 1
        if nodo.hoja:
            while i >= 0 and persona.dpi < nodo.claves[i].dpi:
                i -= 1
            i += 1
            nodo.claves.insert(i, persona)
        else:
            while i >= 0 and persona.dpi < nodo.claves[i].dpi:
                i -= 1
            i += 1
            if len(nodo.hijos) > i and len(nodo.hijos[i].claves) == (2 * self.grado) - 1:
                self.dividir(nodo, i)
                if persona.dpi > nodo.claves[i].dpi:
                    i += 1
            if i < len(nodo.hijos):
                self.insertar_no_lleno(nodo.hijos[i], persona)
            else:
                self.insertar_no_lleno(nodo.hijos[-1], persona)

    def dividir(self, nodo, i):
        t = self.grado
        y = nodo.hijos[i]
        z = Nodo(y.hoja)
        nodo.hijos.insert(i + 1, z)
        nodo.claves.insert(i, y.claves[t - 1])
        z.claves = y.claves[t: (2 * t) - 1]
        y.claves = y.claves[0: t - 1]
        if not y.hoja:
            z.hijos = y.hijos[t: 2 * t]
            y.hijos = y.hijos[0: t]

    def mostrar(self, nodo=None, l=0):
        if nodo is None:
            nodo = self.raiz

        resultado = []
        resultado.append(f"Level {l} {len(nodo.claves)}:")

        for i in nodo.claves:
            resultado.append(f"DPI: {i.dpi}")
            resultado.append(f"Nombre: {i.nombre}")
            resultado.append(f"Fecha de Nacimiento: {i.date_birth}")
            resultado.append(f"Dirección: {i.address}")
            resultado.append(f"Empresas: {', '.join(i.empresas)}")  # Mostrar las empresas como una lista separada por comas
            resultado.append(f"Cartas comprimidas: {i.cartas_comprimidas}")
            resultado.append(f"Cartas descomprimidas: {i.cartas_descomprimidas}\n")

        l += 1
        if len(nodo.hijos) > 0:
            for i in nodo.hijos:
                child_result = self.mostrar(i, l)
                resultado.extend(child_result)

        return resultado


    def buscar(self, dpi, nodo=None):
        if nodo is None:
            nodo = self.raiz

        i = 0
        while i < len(nodo.claves) and dpi > nodo.claves[i].dpi:
            i += 1
        if i < len(nodo.claves) and dpi == nodo.claves[i].dpi:
            return nodo.claves[i]
        elif nodo.hoja:
            return None
        else:
            return self.buscar(dpi, nodo.hijos[i])

    def actualizar(self, dpi, nuevos_datos):
        persona_antigua = self.buscar(dpi, self.raiz)
        if persona_antigua:
            if 'nombre' in nuevos_datos and nuevos_datos['nombre'] != "":
                nombre_nuevo = nuevos_datos['nombre']
            else:
                nombre_nuevo = persona_antigua.nombre

            if 'date_birth' in nuevos_datos and nuevos_datos['date_birth'] != "":
                date_birth_nueva = nuevos_datos['date_birth']
            else:
                date_birth_nueva = persona_antigua.date_birth

            if 'address' in nuevos_datos and nuevos_datos['address'] != "":
                address_nueva = nuevos_datos['address']
            else:
                address_nueva = persona_antigua.address

            persona_nueva = Persona(nombre_nuevo, dpi, date_birth_nueva, address_nueva)

            return self._actualizar_en_arbol(self.raiz, dpi, persona_nueva)
        else:
            return False

    def _actualizar_en_arbol(self, nodo, dpi, persona_nueva):
        if nodo is None:
            return False

        indice = 0
        while indice < len(nodo.claves) and dpi > nodo.claves[indice].dpi:
            indice += 1

        if indice < len(nodo.claves) and dpi == nodo.claves[indice].dpi:
            nodo.claves[indice] = persona_nueva
            return True
        elif nodo.hoja:
            return False
        else:
            return self._actualizar_en_arbol(nodo.hijos[indice], dpi, persona_nueva)

    def eliminar(self, dpi):
        if self.raiz is not None:
            resultado, nodo = self._eliminar_en_arbol(self.raiz, dpi)
            if resultado and len(nodo.claves) == 0:
                self.raiz = nodo.hijos[0] if nodo.hijos else None
            return resultado
        else:
            return False

    def _eliminar_en_arbol(self, nodo, dpi):
        if nodo is None:
            return False, None

        indice = 0
        while indice < len(nodo.claves) and dpi > nodo.claves[indice].dpi:
            indice += 1

        if indice < len(nodo.claves) and dpi == nodo.claves[indice].dpi:
            if nodo.hoja:
                nodo.claves.pop(indice)
            else:
                dpi_antecesor = self._obtener_dpi_antecesor(nodo, indice)
                nodo.claves[indice] = dpi_antecesor
                return self._eliminar_en_arbol(nodo.hijos[indice], dpi_antecesor.dpi)

        elif nodo.hoja:
            return False, None

        else:
            resultado, nodo_hijo = self._eliminar_en_arbol(nodo.hijos[indice], dpi)
            if resultado:
                if len(nodo_hijo.claves) < self.grado // 2:
                    if indice < len(nodo.claves):
                        self._mover_clave_derecha(nodo, indice)
                    else:
                        self._mover_clave_izquierda(nodo, indice)
                return self._eliminar_en_arbol(nodo.hijos[indice], dpi)

        return False, nodo


class LZW:
    def __init__(self):
        self.init = {}
    
    def CFD(self, mensaje):
        for i in range(len(mensaje)):
            current = mensaje[i]
            if current not in self.init:
                self.init[current] = len(self.init)
    
class LZW:
    def __init__(self):
        self.init = {}
    
    def CFD(self, mensaje):
        for i in range(len(mensaje)):
            current = mensaje[i]
            if current not in self.init:
                self.init[current] = len(self.init)
    
    def COMPRESS(self, mensaje):
        self.CFD(mensaje)
        w = None
        k = ""
        wk = ""
        salida = ""
        for i in range(len(mensaje)):
            k = mensaje[i]
            if w is None:
                wk = k
            else:
                wk = w + k
            if wk in self.init:
                w = wk
            else:
                salida += str(self.init[w]) + ","
                self.init[wk] = len(self.init)
                w = k
        salida += str(self.init[w]) + ","
        return salida

    def DECOMPRESS(self, compress):
        original = ""
        partes = compress.split(',')[:-1]
        for parte in partes:
            parte = int(parte)
            for key, value in self.init.items():
                if value == parte:
                    original += key
                    break
        return original

def cifrarMensaje(key, message):
    cipherText = [''] * key
    for col in range(key):
        pointer = col
        while pointer < len(message):
            cipherText[col] += message[pointer]
            pointer += key
    return ''.join(cipherText)

def descifrarMensaje(key, message):
    numCols = math.ceil(len(message) / key)
    numRows = key
    numShadedBoxes = (numCols * numRows) - len(message)
    plainText = [""] * numCols
    col = 0; row = 0;

    for symbol in message:
        plainText[col] += symbol
        col += 1

        if (col == numCols) or (col == numCols - 1) and (row >= numRows - numShadedBoxes):
            col = 0
            row += 1

    return "".join(plainText)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Administrar Personas")
        self.setGeometry(100, 100, 360, 580)

        self.boton_cargar = QPushButton("Cargar", self)
        self.boton_cargar.setGeometry(100, 20, 160, 40)
        self.boton_cargar.clicked.connect(self.cargar)

        self.boton_mostrar_datos = QPushButton("Mostrar Datos", self)
        self.boton_mostrar_datos.setGeometry(100, 70, 160, 40)
        self.boton_mostrar_datos.clicked.connect(self.mostrar_datos)

        self.input_buscar = QLineEdit(self)
        self.input_buscar.setGeometry(80, 120, 200, 40)

        self.boton_buscar = QPushButton("Buscar", self)
        self.boton_buscar.setGeometry(100, 170, 160, 40)
        self.boton_buscar.clicked.connect(self.buscar)

        self.boton_actualizar = QPushButton("Actualizar", self)
        self.boton_actualizar.setGeometry(100, 220, 160, 40)
        self.boton_actualizar.clicked.connect(self.actualizar)

        self.boton_eliminar = QPushButton("Eliminar", self)
        self.boton_eliminar.setGeometry(100, 270, 160, 40)
        self.boton_eliminar.clicked.connect(self.eliminar)

        self.boton_comprimir = QPushButton("Comprimir DPI", self)
        self.boton_comprimir.setGeometry(100, 320, 160, 40)
        self.boton_comprimir.clicked.connect(self.comprimir_dpi)

        self.boton_descomprimir = QPushButton("Descomprimir DPI", self)
        self.boton_descomprimir.setGeometry(100, 370, 160, 40)
        self.boton_descomprimir.clicked.connect(self.descomprimir_dpi)

        self.boton_comprimir = QPushButton("Cifrar y comprimir cartas", self)
        self.boton_comprimir.setGeometry(100, 420, 160, 40)
        self.boton_comprimir.clicked.connect(self.cc_cartas)

        self.boton_comprimir = QPushButton("Compresión Cartas", self)
        self.boton_comprimir.setGeometry(100, 470, 160, 40)
        self.boton_comprimir.clicked.connect(self.compresion_cartas)

        self.input_key = QLineEdit(self)
        self.input_key.setGeometry(70, 520, 50, 40)

        self.boton_cifrar = QPushButton("Cifrado Cartas", self)
        self.boton_cifrar.setGeometry(130, 520, 160, 40)
        self.boton_cifrar.clicked.connect(self.cifrado_cartas)

        self.arbol = ArbolB(2)

    def cargar(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo CSV", "", "CSV Files (*.csv)")
        if archivo:
            try:
                archivo_absoluto = os.path.abspath(archivo)
                with open(archivo_absoluto, 'r') as file:
                    for line in file:
                        parts = line.strip().split(';')
                        if len(parts) == 2:
                            accion = parts[0]
                            datos_json = parts[1]

                            if accion == 'INSERT':
                                try:
                                    datos = json.loads(datos_json)
                                    persona = Persona(
                                        datos['name'],
                                        datos['dpi'],
                                        datos['datebirth'],
                                        datos['address']
                                    )
                                    if 'companies' in datos:
                                        persona.empresas = datos['companies']  # Asignar empresas a la persona
                                    self.arbol.insertar(persona)
                                except json.JSONDecodeError as e:
                                    QMessageBox.warning(self, "Advertencia", f"No se pudo cargar la línea debido a un error de JSON: {str(e)}")
                            elif accion == 'DELETE':
                                dpi_a_eliminar = datos_json
                                self.arbol.eliminar(dpi_a_eliminar)
                            elif accion == 'PATCH':
                                try:
                                    datos = json.loads(datos_json)
                                    dpi_a_actualizar = datos['dpi']
                                    if self.arbol.buscar(dpi_a_actualizar, self.arbol.raiz):
                                        self.arbol.actualizar(dpi_a_actualizar, datos)
                                except json.JSONDecodeError as e:
                                    QMessageBox.warning(self, "Advertencia", f"No se pudo cargar la línea debido a un error de JSON: {str(e)}")
                    QMessageBox.information(self, "Éxito", "Datos cargados exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar el archivo: {str(e)}")


    def mostrar_datos(self):
        datos = self.arbol.mostrar()
        if datos:
            dialogo_mostrar = MostrarDatosDialog("\n".join(datos))
            dialogo_mostrar.exec_()

    def buscar(self):
        dpi_a_buscar = self.input_buscar.text()
        if dpi_a_buscar:
            persona = self.arbol.buscar(dpi_a_buscar, self.arbol.raiz)
            if persona:
                datos = f"DPI: {persona.dpi}\n" \
                        f"Nombre: {persona.nombre}\n" \
                        f"Fecha de Nacimiento: {persona.date_birth}\n" \
                        f"Dirección: {persona.address}\n" \
                        f"Empresas: {persona.empresas}\n" \
                        f"Cartas comprimidas: {persona.cartas_comprimidas}\n" \
                        f"Cartas descomprimidas: {persona.cartas_descomprimidas}"
                dialog = MostrarBusquedaDialog(datos)
                dialog.exec_()
            else:
                QMessageBox.warning(self, "Resultado de búsqueda", "No se encontró ninguna persona con el DPI especificado.")
        else:
            QMessageBox.warning(self, "Error", "Ingrese un DPI válido para buscar.")


    def actualizar(self):
        dpi_a_actualizar, ok = QInputDialog.getText(self, "Actualizar Persona", "Ingrese el DPI de la persona a actualizar:")
        if ok:
            persona = self.arbol.buscar(dpi_a_actualizar, self.arbol.raiz)
            if persona:
                dialogo_actualizar = ActualizarPersonaDialog(persona)
                if dialogo_actualizar.exec_() == QDialog.Accepted:
                    nuevos_datos = dialogo_actualizar.obtener_datos_actualizados()
                    if nuevos_datos:
                        if self.arbol.actualizar(dpi_a_actualizar, nuevos_datos):
                            QMessageBox.information(self, "Éxito", "Persona actualizada exitosamente.")
                        else:
                            QMessageBox.warning(self, "Error", "No se pudo actualizar la persona.")
                else:
                    QMessageBox.warning(self, "Error", "La operación de actualización fue cancelada.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró ninguna persona con el DPI especificado.")

    def eliminar(self):
        dpi_a_eliminar, ok = QInputDialog.getText(self, "Eliminar Persona", "Ingrese el DPI de la persona a eliminar:")
        if ok:
            if self.arbol.eliminar(dpi_a_eliminar):
                QMessageBox.information(self, "Éxito", "Persona eliminada exitosamente.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró ninguna persona con el DPI especificado.")

    def comprimir_dpi(self):
        dpi_a_comprimir, ok = QInputDialog.getText(self, "Comprimir DPI", "Ingrese el DPI a comprimir:")
        if ok:
            dpi_codificado = self.compress(dpi_a_comprimir)
            QMessageBox.information(self, "Comprimir DPI", f"DPI comprimido: {dpi_codificado}")

    def descomprimir_dpi(self):
        dpi_codificado, ok = QInputDialog.getText(self, "Descomprimir DPI", "Ingrese el DPI comprimido:")
        if ok:
            dpi_decodificado = self.decompress(dpi_codificado)
            QMessageBox.information(self, "Descomprimir DPI", f"DPI descomprimido: {dpi_decodificado}")

    def cc_cartas(self):
        key_text = self.input_key.text()
        try:
            key = int(key_text)
        except ValueError:
            QMessageBox.critical(self, 'Error', 'El valor ingresado no es un entero válido', QMessageBox.Ok)

        carpeta_cartas = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Cartas")

        if not carpeta_cartas:
            return

        try:
            contenido_comprimido = {}
            contenido_descomprimido = {}

            for archivo in os.listdir(carpeta_cartas):
                if archivo.endswith(".txt") and archivo.startswith("REC-"):
                    partes = archivo.split('-')
                    dpi_persona = partes[1]
                    numero_carta = partes[2].split('.')[0] 

                    with open(os.path.join(carpeta_cartas, archivo), 'r', encoding='utf-8') as file:
                        contenido = file.read()

                    lzw = LZW()

                    contenido = cifrarMensaje(key, contenido)
                    comprimido = lzw.COMPRESS(contenido)
                    
                    descomprimido = lzw.DECOMPRESS(comprimido)
                    contenido = descifrarMensaje(key,descomprimido)

                    contenido_comprimido[dpi_persona] = contenido_comprimido.get(dpi_persona, []) + [f"{numero_carta}-{comprimido}"]
                    contenido_descomprimido[dpi_persona] = contenido_descomprimido.get(dpi_persona, []) + [f"Carta {numero_carta}-{contenido}"]

            for dpi, cartas_comprimidas in contenido_comprimido.items():
                persona = self.arbol.buscar(dpi)
                if persona:
                    persona.cartas_comprimidas = cartas_comprimidas
                    persona.cartas_descomprimidas = contenido_descomprimido[dpi]

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al comprimir las cartas: {str(e)}")

    def compresion_cartas(self):
        carpeta_cartas = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Cartas")

        if not carpeta_cartas:
            return

        try:
            contenido_comprimido = {}
            contenido_descomprimido = {}

            for archivo in os.listdir(carpeta_cartas):
                if archivo.endswith(".txt") and archivo.startswith("REC-"):
                    partes = archivo.split('-')
                    dpi_persona = partes[1]
                    numero_carta = partes[2].split('.')[0] 

                    with open(os.path.join(carpeta_cartas, archivo), 'r', encoding='utf-8') as file:
                        contenido = file.read()

                    lzw = LZW()
                    comprimido = lzw.COMPRESS(contenido)
                    contenido_comprimido[dpi_persona] = contenido_comprimido.get(dpi_persona, []) + [f"{numero_carta}-{comprimido}"]
                    contenido_descomprimido[dpi_persona] = contenido_descomprimido.get(dpi_persona, []) + [f"Carta {numero_carta}-{lzw.DECOMPRESS(comprimido)}"]

            dialogo_resultado = ResultadoCompresionDialog(contenido_comprimido)
            dialogo_resultado.exec_()

            dialogo_resultado_descomp = DescomprimirCartasDialog(contenido_descomprimido)
            dialogo_resultado_descomp.exec_()

            for dpi, cartas_comprimidas in contenido_comprimido.items():
                persona = self.arbol.buscar(dpi)
                if persona:
                    persona.cartas_comprimidas = cartas_comprimidas
                    persona.cartas_descomprimidas = contenido_descomprimido[dpi]

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al comprimir las cartas: {str(e)}")

    def cifrado_cartas(self):
        key_text = self.input_key.text()
        try:
            key = int(key_text)
        except ValueError:
            QMessageBox.critical(self, 'Error', 'El valor ingresado no es un entero válido', QMessageBox.Ok)

        carpeta_cartas = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Cartas")

        if not carpeta_cartas:
            return

        try:
            contenido_encriptado = {}
            contenido_desencriptado = {}

            for archivo in os.listdir(carpeta_cartas):
                if archivo.endswith(".txt") and archivo.startswith("REC-"):
                    partes = archivo.split('-')
                    dpi_persona = partes[1]
                    numero_carta = partes[2].split('.')[0] 

                    with open(os.path.join(carpeta_cartas, archivo), 'r', encoding='utf-8') as file:
                        contenido = file.read()
                        
                    encriptado = cifrarMensaje(key,contenido)
                    contenido_encriptado[dpi_persona] = contenido_encriptado.get(dpi_persona, []) + [f"Carta {numero_carta}-{encriptado}"]
                    contenido_desencriptado[dpi_persona] = contenido_desencriptado.get(dpi_persona, []) + [f"Carta {numero_carta}-{descifrarMensaje(key, encriptado)}"]

            dialogo_resultado = ResultadoEncriptacionDialog(contenido_encriptado)
            dialogo_resultado.exec_()

            dialogo_resultado_descomp = ResultadoDesencriptacionDialog(contenido_desencriptado)
            dialogo_resultado_descomp.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al comprimir las cartas: {str(e)}")


class MostrarDatosDialog(QDialog):
    def __init__(self, datos):
        super().__init__()

        self.setWindowTitle("Mostrar Datos")
        self.setGeometry(300, 100, 1000, 800)

        layout = QVBoxLayout()

        self.texto_datos = QTextBrowser(self)
        self.texto_datos.setPlainText(datos)
        layout.addWidget(self.texto_datos)

        self.setLayout(layout)

class MostrarBusquedaDialog(QDialog):
    def __init__(self, datos):
        super().__init__()

        self.setWindowTitle("Resultado de búsqueda")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        texto = f"Persona encontrada:\n{datos}"
        self.texto_datos = QTextBrowser(self)
        self.texto_datos.setPlainText(texto)
        layout.addWidget(self.texto_datos)

        self.setLayout(layout)

class ActualizarPersonaDialog(QDialog):
    def __init__(self, persona):
        super().__init__()

        self.setWindowTitle("Actualizar Persona")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.input_nombre = QLineEdit(self)
        self.input_nombre.setPlaceholderText("Nombre")
        self.input_nombre.setText(persona.nombre)
        layout.addWidget(self.input_nombre)

        self.input_date_birth = QLineEdit(self)
        self.input_date_birth.setPlaceholderText("Fecha de Nacimiento")
        self.input_date_birth.setText(persona.date_birth)
        layout.addWidget(self.input_date_birth)

        self.input_address = QLineEdit(self)
        self.input_address.setPlaceholderText("Dirección")
        self.input_address.setText(persona.address)
        layout.addWidget(self.input_address)

        self.boton_actualizar = QPushButton("Actualizar", self)
        self.boton_actualizar.clicked.connect(self.accept)
        layout.addWidget(self.boton_actualizar)

        self.setLayout(layout)

    def obtener_datos_actualizados(self):
        nuevos_datos = {}
        nuevos_datos['nombre'] = self.input_nombre.text()
        nuevos_datos['date_birth'] = self.input_date_birth.text()
        nuevos_datos['address'] = self.input_address.text()
        return nuevos_datos

class ResultadoCompresionDialog(QDialog):
    def __init__(self, contenido_comprimido):
        super().__init__()

        self.setWindowTitle("Resultado de Compresión")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.texto_resultado = QTextEdit(self)
        self.texto_resultado.setPlainText("Resultados de compresión por persona:\n")
        
        for dpi, contenido in contenido_comprimido.items():
            self.texto_resultado.append(f"DPI: {dpi}\nContenido Comprimido:\n{contenido}\n")

        layout.addWidget(self.texto_resultado)

        guardar_button = QPushButton("Guardar en TXT")
        guardar_button.clicked.connect(self.guardar_en_txt)
        layout.addWidget(guardar_button)

        self.setLayout(layout)

    def guardar_en_txt(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar como TXT", "", "Archivos de Texto (*.txt);;Todos los archivos (*)", options=options)

        if file_name:
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(self.texto_resultado.toPlainText())

class DescomprimirCartasDialog(QDialog):
    def __init__(self, contenido_descomprimido):
        super().__init__()

        self.setWindowTitle("Descomprimir Cartas")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.texto_resultado = QTextEdit(self)
        self.texto_resultado.setPlainText("Resultados de descompresión por persona:\n")

        for dpi, contenido in contenido_descomprimido.items():
            self.texto_resultado.append(f"DPI: {dpi}\nContenido Descomprimido:\n{contenido}\n")

        layout.addWidget(self.texto_resultado)
        
        guardar_button = QPushButton("Guardar en TXT")
        guardar_button.clicked.connect(self.guardar_en_txt)
        layout.addWidget(guardar_button)

        self.setLayout(layout)

    def guardar_en_txt(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar como TXT", "", "Archivos de Texto (*.txt);;Todos los archivos (*)", options=options)

        if file_name:
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(self.texto_resultado.toPlainText())

class ResultadoEncriptacionDialog(QDialog):
    def __init__(self, contenido_encriptado):
        super().__init__()

        self.setWindowTitle("Resultado de Encriptación")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.texto_resultado = QTextEdit(self)
        self.texto_resultado.setPlainText("Resultados de encriptacion por persona:\n")
        
        for dpi, contenido in contenido_encriptado.items():
            self.texto_resultado.append(f"DPI: {dpi}\nContenido Encriptado:\n{contenido}\n")

        layout.addWidget(self.texto_resultado)

        guardar_button = QPushButton("Guardar en TXT")
        guardar_button.clicked.connect(self.guardar_en_txt)
        layout.addWidget(guardar_button)

        self.setLayout(layout)

    def guardar_en_txt(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar como TXT", "", "Archivos de Texto (*.txt);;Todos los archivos (*)", options=options)

        if file_name:
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(self.texto_resultado.toPlainText())

class ResultadoDesencriptacionDialog(QDialog):
    def __init__(self, contenido_desencriptado):
        super().__init__()

        self.setWindowTitle("Resultado de Desencriptación")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.texto_resultado = QTextEdit(self)
        self.texto_resultado.setPlainText("Resultados de desencriptacion por persona:\n")
        
        for dpi, contenido in contenido_desencriptado.items():
            self.texto_resultado.append(f"DPI: {dpi}\nContenido Desencriptado:\n{contenido}\n")

        layout.addWidget(self.texto_resultado)

        guardar_button = QPushButton("Guardar en TXT")
        guardar_button.clicked.connect(self.guardar_en_txt)
        layout.addWidget(guardar_button)

        self.setLayout(layout)

    def guardar_en_txt(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar como TXT", "", "Archivos de Texto (*.txt);;Todos los archivos (*)", options=options)

        if file_name:
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(self.texto_resultado.toPlainText())
           

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
