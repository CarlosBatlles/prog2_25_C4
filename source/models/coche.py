
import pandas as pd

class Coche:
    def __init__(self, id: str, marca: str, modelo: str, matricula: str, categoria_tipo: str, categoria_precio: str,
                año: int, precio_diario: float, kilometraje: float, color: str, combustible: str, cv: int,
                plazas: int, disponible: bool):
        self.id = id
        self.marca = marca
        self.modelo = modelo
        self.matricula = matricula
        self.categoria_tipo = categoria_tipo
        self.categoria_precio = categoria_precio
        self.año = año
        self.precio_diario = precio_diario
        self.kilometraje = kilometraje
        self.color = color
        self.combustible = combustible
        self.cv = cv
        self.plazas = plazas
        self.disponible = disponible

    @staticmethod
    def registrar_coche(empresa, marca: str, modelo: str, matricula: str, categoria_tipo: str, categoria_precio: str,
                        año: int, precio_diario: float, kilometraje: float, color: str, combustible: str, cv: int,
                        plazas: int, disponible: bool) -> bool:
        """
        Registra un nuevo coche en el sistema.

        Este método realiza validaciones y añade el coche al archivo CSV correspondiente.
        """
        # Validaciones de campos obligatorios
        if not all([marca, modelo, matricula, categoria_tipo, categoria_precio]):
            raise ValueError("Todos los campos de texto (marca, modelo, matricula, categoria_tipo, categoria_precio) deben tener un valor.")

        if precio_diario <= 0:
            raise ValueError("El precio diario debe ser mayor que 0.")
        if kilometraje < 0:
            raise ValueError("El kilometraje no puede ser negativo.")
        if cv <= 0:
            raise ValueError("La potencia del coche debe ser mayor que 0.")
        if plazas < 2:
            raise ValueError("Las plazas del coche deben ser mayores o iguales a 2.")
        if not isinstance(disponible, bool):
            raise TypeError("El campo 'disponible' debe ser True o False.")

        # Cargar los coches existentes
        df_coches = empresa.cargar_coches()
        if df_coches is None:
            raise ValueError("No se pudieron cargar los coches. Verifica el archivo CSV.")

        # Generar un ID único para el coche
        id_coche = empresa.generar_id_coche()

        # Crear un diccionario con los datos del nuevo coche
        nuevo_coche = {
            'id': id_coche,
            'marca': marca,
            'modelo': modelo,
            'matricula': matricula,
            'categoria_tipo': categoria_tipo,
            'categoria_precio': categoria_precio,
            'año': año,
            'precio_diario': precio_diario,
            'kilometraje': kilometraje,
            'color': color,
            'combustible': combustible,
            'cv': cv,
            'plazas': plazas,
            'disponible': disponible
        }

        # Crear un DataFrame con el nuevo coche y actualizar el archivo CSV
        df_nuevo_coche = pd.DataFrame([nuevo_coche])
        df_actualizado = pd.concat([df_coches, df_nuevo_coche], ignore_index=True)

        try:
            empresa._guardar_csv('coches.csv', df_actualizado)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar el coche en el archivo CSV: {e}")
        
    @staticmethod
    def actualizar_matricula(empresa, id_coche: str, nueva_matricula: str) -> bool:
        """
        Actualiza la matrícula de un coche existente en el sistema.

        Este método verifica si el ID del coche existe y si la nueva matrícula no está duplicada 
        antes de realizar la actualización en el archivo CSV correspondiente.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar/guardar datos.
        id_coche : str
            El ID único del coche cuya matrícula se desea actualizar.
        nueva_matricula : str
            La nueva matrícula que se asignará al coche.

        Returns
        -------
        bool
            True si la matrícula se actualizó correctamente.

        Raises
        ------
        ValueError
            Si el ID del coche no está registrado o si la nueva matrícula ya está en uso.
        Exception
            Si ocurre un error al guardar los cambios en el archivo CSV.
        """
        # Cargar los coches actuales
        df_coches = empresa.cargar_coches()
        if df_coches is None:
            raise ValueError("No se pudieron cargar los coches. Revisa el archivo CSV.")

        # Verificar si el ID existe en el DataFrame
        if id_coche not in df_coches['id'].values:
            raise ValueError(f"El coche con ID {id_coche} no está registrado.")
        
        # Verificar si la nueva matrícula ya existe
        if nueva_matricula in df_coches['matricula'].values:
            raise ValueError(f"La matrícula {nueva_matricula} ya está registrada en otro coche.")

        # Actualizar la matrícula en el DataFrame
        df_coches.loc[df_coches['id'] == id_coche, 'matricula'] = nueva_matricula

        # Guardar los cambios en el archivo CSV
        try:
            empresa._guardar_csv("coches.csv", df_coches)
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")

        return True
    
    
    @staticmethod
    def eliminar_coche(empresa, id_coche: str) -> bool:
        """
        Elimina un coche del sistema basándose en su ID.

        Este método verifica si el coche con el ID proporcionado existe en el sistema 
        y lo elimina del archivo CSV correspondiente.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar/guardar datos.
        id_coche : str
            El ID único del coche que se desea eliminar.

        Returns
        -------
        bool
            True si el coche se eliminó correctamente.

        Raises
        ------
        ValueError
            Si el coche con el ID proporcionado no está registrado o si ocurre un error al guardar los cambios.

        Notes
        -----
        - Antes de eliminar el coche, se verifica que el ID exista en el sistema.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        # Cargar los coches actuales
        df_coches = empresa.cargar_coches()
        if df_coches is None:
            raise ValueError("No se pudieron cargar los coches. Revisa el archivo CSV.")

        # Verificar si el ID existe en el DataFrame
        if id_coche not in df_coches['id'].values:
            raise ValueError(f"El coche con ID {id_coche} no está registrado.")

        # Filtrar el DataFrame para excluir al coche con el ID proporcionado
        df_actualizado = df_coches[df_coches['id'] != id_coche]

        # Guardar los cambios usando el método auxiliar
        try:
            empresa._guardar_csv('coches.csv', df_actualizado)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")
        
        
    @staticmethod
    def mostrar_categorias_tipo(empresa) -> list:
        """
        Muestra las categorías de tipo de los coches disponibles en el sistema.

        Este método carga los datos de los coches desde el archivo CSV y devuelve una lista 
        de las categorías de tipo únicas disponibles.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.

        Returns
        -------
        list
            Una lista de las categorías de tipo únicas de los coches.

        Raises
        ------
        ValueError
            Si no se pueden cargar los datos o si no hay coches disponibles.
        """
        # Cargar los datos de los coches
        df_coches = empresa.cargar_coches()

        # Validar que el DataFrame no esté vacío
        if df_coches is None or df_coches.empty:
            raise ValueError('No hay datos disponibles para mostrar categorías.')

        # Obtener las categorías de tipo únicas
        categorias_tipo = df_coches['categoria_tipo'].unique()

        return list(categorias_tipo)
    
    
    @staticmethod
    def mostrar_categorias_precio(empresa) -> list:
        """
        Muestra las categorías de precio de los coches disponibles en el sistema.

        Este método carga los datos de los coches desde el archivo CSV y devuelve una lista 
        de las categorías de precio únicas disponibles.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.

        Returns
        -------
        list
            Una lista de las categorías de precio únicas de los coches.

        Raises
        ------
        ValueError
            Si no se pueden cargar los datos o si no hay coches disponibles.
        """
        # Cargar los datos de los coches
        df_coches = empresa.cargar_coches()

        # Validar que el DataFrame no esté vacío
        if df_coches is None or df_coches.empty:
            raise ValueError('No hay datos disponibles para mostrar categorías.')

        # Obtener las categorías de precio únicas
        categorias_precio = df_coches['categoria_precio'].unique()

        return list(categorias_precio)
    
    
    @staticmethod
    def cargar_coches_disponibles(empresa) -> pd.DataFrame:
        """
        Carga los coches disponibles desde el archivo CSV.

        Este método carga los datos de los coches desde el archivo CSV y filtra solo 
        aquellos que están marcados como disponibles.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches disponibles.

        Raises
        ------
        ValueError
            Si no hay coches disponibles o si el archivo CSV no se pudo cargar.

        Notes
        -----
        - Los coches disponibles son aquellos donde el campo 'disponible' es True.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        df = empresa.cargar_coches()
        if df is None or df.empty:
            raise ValueError("No hay coches disponibles o el archivo no se pudo cargar.")
        return df[df['disponible'] == True]  # Filtrar solo coches disponibles
    
    
    @staticmethod
    def obtener_categorias_precio(empresa) -> list:
        """
        Devuelve una lista de categorías de precio disponibles.

        Este método carga los coches disponibles y extrae las categorías de precio únicas.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.

        Returns
        -------
        list
            Una lista de las categorías de precio únicas disponibles.

        Raises
        ------
        ValueError
            Si no hay coches disponibles o si el archivo CSV no se pudo cargar.

        Notes
        -----
        - Las categorías de precio son únicas y se extraen del campo 'categoria_precio' del DataFrame.
        """
        df = Coche.cargar_coches_disponibles(empresa)
        return df['categoria_precio'].unique().tolist()
    
    
    @staticmethod
    def filtrar_por_categoria_precio(empresa, categoria_precio: str) -> pd.DataFrame:
        """
        Filtra coches disponibles por categoría de precio.

        Este método carga los coches disponibles y filtra aquellos que pertenecen 
        a la categoría de precio especificada.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches filtrados por la categoría de precio.

        Raises
        ------
        ValueError
            Si la categoría de precio seleccionada no es válida o si no hay coches disponibles.

        Notes
        -----
        - La categoría de precio debe ser una de las categorías disponibles en el sistema.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        df = Coche.cargar_coches_disponibles(empresa)
        if categoria_precio not in df['categoria_precio'].unique():
            raise ValueError("La categoría de precio seleccionada no es válida.")
        return df[df['categoria_precio'] == categoria_precio]
    
    
    @staticmethod
    def obtener_categorias_tipo(empresa, categoria_precio: str) -> list:
        """
        Devuelve una lista de categorías de tipo disponibles para una categoría de precio.

        Este método filtra los coches disponibles por la categoría de precio especificada 
        y devuelve una lista de las categorías de tipo únicas dentro de esa categoría de precio.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.

        Returns
        -------
        list
            Una lista de las categorías de tipo únicas disponibles para la categoría de precio especificada.

        Raises
        ------
        ValueError
            Si la categoría de precio seleccionada no es válida o si no hay coches disponibles.

        Notes
        -----
        - Las categorías de tipo son únicas y se extraen del campo 'categoria_tipo' del DataFrame filtrado.
        """
        df_filtrado = Coche.filtrar_por_categoria_precio(empresa, categoria_precio)
        return df_filtrado['categoria_tipo'].unique().tolist()
    
    
    @staticmethod
    def filtrar_por_categoria_tipo(empresa, categoria_precio: str, categoria_tipo: str) -> pd.DataFrame:
        """
        Filtra coches disponibles por categoría de tipo dentro de una categoría de precio.

        Este método filtra los coches disponibles primero por la categoría de precio y luego 
        por la categoría de tipo especificada.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches filtrados por la categoría de tipo dentro de la categoría de precio.

        Raises
        ------
        ValueError
            Si la categoría de precio o la categoría de tipo seleccionadas no son válidas.

        Notes
        -----
        - La categoría de tipo debe ser una de las categorías disponibles dentro de la categoría de precio especificada.
        """
        df_filtrado = Coche.filtrar_por_categoria_precio(empresa, categoria_precio)
        if categoria_tipo not in df_filtrado['categoria_tipo'].unique():
            raise ValueError("La categoría de tipo seleccionada no es válida.")
        return df_filtrado[df_filtrado['categoria_tipo'] == categoria_tipo]
    
    
    @staticmethod
    def obtener_marcas(empresa, categoria_precio: str, categoria_tipo: str) -> list:
        """
        Devuelve una lista de marcas disponibles para una categoría de precio y tipo.

        Este método filtra los coches disponibles por la categoría de precio y tipo especificadas, 
        y devuelve una lista de las marcas únicas dentro de esa combinación de categorías.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.

        Returns
        -------
        list
            Una lista de las marcas únicas disponibles para la categoría de precio y tipo especificadas.

        Raises
        ------
        ValueError
            Si la categoría de precio o la categoría de tipo seleccionadas no son válidas.

        Notes
        -----
        - Las marcas son únicas y se extraen del campo 'marca' del DataFrame filtrado.
        """
        df_filtrado = Coche.filtrar_por_categoria_tipo(empresa, categoria_precio, categoria_tipo)
        return df_filtrado['marca'].unique().tolist()
    
    
    @staticmethod
    def filtrar_por_marca(empresa, categoria_precio: str, categoria_tipo: str, marca: str) -> pd.DataFrame:
        """
        Filtra coches disponibles por marca dentro de una categoría de precio y tipo.

        Este método filtra los coches disponibles primero por la categoría de precio y tipo, 
        y luego por la marca especificada.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.
        marca : str
            La marca por la cual se desea filtrar los coches.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches filtrados por la marca dentro de la categoría de precio y tipo.

        Raises
        ------
        ValueError
            Si la categoría de precio, la categoría de tipo o la marca seleccionadas no son válidas.

        Notes
        -----
        - La marca debe ser una de las marcas disponibles dentro de la combinación de categoría de precio y tipo especificadas.
        """
        df_filtrado = Coche.filtrar_por_categoria_tipo(empresa, categoria_precio, categoria_tipo)
        if marca not in df_filtrado['marca'].unique():
            raise ValueError("La marca seleccionada no es válida.")
        return df_filtrado[df_filtrado['marca'] == marca]
    
    
    @staticmethod
    def obtener_modelos(empresa, categoria_precio: str, categoria_tipo: str, marca: str) -> list:
        """
        Devuelve una lista de modelos disponibles para una marca, categoría de precio y tipo.

        Este método filtra los coches disponibles por la categoría de precio, tipo y marca especificadas, 
        y devuelve una lista de los modelos únicos dentro de esa combinación de categorías.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.
        marca : str
            La marca por la cual se desea filtrar los coches.

        Returns
        -------
        list
            Una lista de los modelos únicos disponibles para la combinación de categoría de precio, tipo y marca.

        Raises
        ------
        ValueError
            Si la categoría de precio, la categoría de tipo o la marca seleccionadas no son válidas.

        Notes
        -----
        - Los modelos son únicos y se extraen del campo 'modelo' del DataFrame filtrado.
        """
        df_filtrado = Coche.filtrar_por_marca(empresa, categoria_precio, categoria_tipo, marca)
        return df_filtrado['modelo'].unique().tolist()
    
    
    @staticmethod
    def filtrar_por_modelo(
        empresa, categoria_precio: str, categoria_tipo: str, marca: str, modelo: str
    ) -> pd.DataFrame:
        """
        Filtra coches disponibles por modelo dentro de una marca, categoría de precio y tipo.

        Este método filtra los coches disponibles primero por la categoría de precio, tipo y marca, 
        y luego por el modelo especificado.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.
        marca : str
            La marca por la cual se desea filtrar los coches.
        modelo : str
            El modelo por el cual se desea filtrar los coches.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches filtrados por el modelo dentro de la combinación de categoría de precio, tipo y marca.

        Raises
        ------
        ValueError
            Si la categoría de precio, la categoría de tipo, la marca o el modelo seleccionados no son válidos.

        Notes
        -----
        - El modelo debe ser uno de los modelos disponibles dentro de la combinación de categoría de precio, tipo y marca especificadas.
        """
        df_filtrado = Coche.filtrar_por_marca(empresa, categoria_precio, categoria_tipo, marca)
        if modelo not in df_filtrado['modelo'].unique():
            raise ValueError("El modelo seleccionado no está disponible.")
        return df_filtrado[df_filtrado['modelo'] == modelo]
    
    
    @staticmethod
    def obtener_detalles_coches(
        empresa, categoria_precio: str, categoria_tipo: str, marca: str, modelo: str
    ) -> list[dict]:
        """
        Devuelve los detalles de los coches filtrados por modelo.

        Este método filtra los coches disponibles por la combinación de categoría de precio, 
        categoría de tipo, marca y modelo, y devuelve una lista de diccionarios con los detalles 
        de cada coche que cumple con los criterios.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.
        marca : str
            La marca por la cual se desea filtrar los coches.
        modelo : str
            El modelo por el cual se desea filtrar los coches.

        Returns
        -------
        list[dict]
            Una lista de diccionarios que contienen los detalles de los coches filtrados. 
            Cada diccionario incluye las siguientes claves:
            - matricula (str)
            - marca (str)
            - modelo (str)
            - categoria_precio (str)
            - categoria_tipo (str)
            - disponible (bool)
            - año (int)
            - precio_diario (float)
            - kilometraje (float)
            - color (str)
            - combustible (str)
            - cv (int)
            - plazas (int)

        Raises
        ------
        ValueError
            Si la categoría de precio, la categoría de tipo, la marca o el modelo seleccionados no son válidos.

        Notes
        -----
        - Los detalles de los coches se extraen del DataFrame filtrado y se formatean como una lista de diccionarios.
        """
        df_filtrado = Coche.filtrar_por_modelo(empresa, categoria_precio, categoria_tipo, marca, modelo)
        detalles = []
        for _, coche in df_filtrado.iterrows():
            detalles.append({
                "matricula": coche['matricula'],
                "marca": coche['marca'],
                "modelo": coche['modelo'],
                "categoria_precio": coche['categoria_precio'],
                "categoria_tipo": coche['categoria_tipo'],
                "disponible": coche['disponible'],
                "año": coche['año'],
                "precio_diario": coche['precio_diario'],
                "kilometraje": coche['kilometraje'],
                "color": coche['color'],
                "combustible": coche['combustible'],
                "cv": coche['cv'],
                "plazas": coche['plazas']
            })
        return detalles