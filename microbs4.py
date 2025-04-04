# microbs4.py - Versión para MicroPython
# Parser HTML optimizado para MicroPython, con manejo correcto de múltiples clases y
# una API pública consistente (find y select_one retornan un Element, no una tupla).

class MicroBS4:
    def __init__(self, html):
        self.html = html
        self.length = len(html)
        # Caché que usa (tag, str(attrs), start) para almacenar resultados
        self._cache = {}

    def _find(self, tag, attrs=None, class_name=None, id=None, start=0):
        """
        Búsqueda interna que devuelve una tupla (elemento, posición siguiente).
        """
        attrs = self._consolidate_attrs(attrs, class_name, id)
        cache_key = (tag, str(attrs), start)
        if cache_key in self._cache:
            return self._cache[cache_key]

        tag_open = f"<{tag}"
        tag_close = f"</{tag}>"
        pos = start

        while pos < self.length:
            start_pos = self.html.find(tag_open, pos)
            if start_pos == -1:
                return None, self.length

            next_char_pos = start_pos + len(tag_open)
            if next_char_pos >= self.length:
                return None, self.length

            next_char = self.html[next_char_pos]
            # Verifica que se trate de la etiqueta buscada (para evitar coincidencias parciales)
            if next_char in [' ', '>', '\t', '\n', '/']:
                gt_pos = self.html.find(">", start_pos)
                if gt_pos == -1:
                    return None, self.length

                is_self_closing = (self.html[gt_pos - 1] == "/")

                if is_self_closing:
                    tag_attrs = self.html[start_pos + len(tag_open):gt_pos - 1].strip()
                    content_start = gt_pos + 1
                    content_end = gt_pos  # No hay contenido en etiquetas auto-cerradas
                else:
                    tag_attrs = self.html[start_pos + len(tag_open):gt_pos].strip()
                    content_start = gt_pos + 1
                    content_end = self._find_matching_end_tag(tag, content_start)
                    if content_end == -1:
                        content_end = self.length

                parsed_attrs = self._parse_attrs(tag_attrs)
                if attrs and not self._attrs_match(parsed_attrs, attrs):
                    pos = gt_pos + 1
                    continue

                if is_self_closing:
                    element = Element(
                        tag=tag,
                        attrs=parsed_attrs,
                        content="",
                        raw_html=self.html[start_pos:gt_pos + 1],
                        self_closing=True
                    )
                    end_pos = gt_pos + 1
                else:
                    element = Element(
                        tag=tag,
                        attrs=parsed_attrs,
                        content=self.html[content_start:content_end],
                        raw_html=self.html[start_pos:content_end + len(tag_close)],
                        self_closing=False
                    )
                    end_pos = content_end + len(tag_close)

                result = (element, end_pos)
                self._cache[cache_key] = result
                return result
            else:
                pos = start_pos + 1

        return None, self.length

    def find(self, tag, attrs=None, class_name=None, id=None):
        """
        Busca la primera ocurrencia de la etiqueta y devuelve el elemento encontrado.
        """
        result = self._find(tag, attrs, class_name, id, start=0)
        if result is None:
            return None
        element, _ = result
        return element

    def find_all(self, tag, attrs=None, class_name=None, id=None, limit=None):
        """
        Encuentra todas las ocurrencias de la etiqueta especificada.
        """
        attrs = self._consolidate_attrs(attrs, class_name, id)
        results = []
        pos = 0
        safety_counter = 0
        max_iterations = 1000

        while pos < self.length and (limit is None or len(results) < limit) and safety_counter < max_iterations:
            safety_counter += 1
            found = self._find(tag, attrs, start=pos)
            if not found:
                break
            element, next_pos = found
            if element is None:
                break
            results.append(element)
            pos = next_pos

        return results

    def select_one(self, selector):
        """
        Selecciona el primer elemento que coincide con un selector CSS simplificado.
        """
        tag, attrs = self._parse_selector(selector)
        result = self._find(tag, attrs, start=0)
        if result is None:
            return None
        element, _ = result
        return element

    def select(self, selector):
        """
        Selecciona todos los elementos que coinciden con el selector CSS simplificado.
        """
        tag, attrs = self._parse_selector(selector)
        return self.find_all(tag, attrs)

    def _parse_selector(self, selector):
        """
        Convierte un selector CSS simplificado en parámetros para búsqueda.
        Soporta:
          - Selector por etiqueta: div, span, etc.
          - Selector por ID: #content
          - Selector por clase: .item
          - Selector mixto: tag.class o tag#id
        """
        if not selector:
            return '*', None

        tag = '*'
        attrs = {}

        if selector.startswith('#'):
            id_value = selector[1:]
            return tag, {'id': id_value}
        if selector.startswith('.'):
            class_value = selector[1:]
            return tag, {'class': class_value}

        if '#' in selector:
            parts = selector.split('#', 1)
            tag = parts[0] or '*'
            attrs['id'] = parts[1]
        elif '.' in selector:
            parts = selector.split('.', 1)
            tag = parts[0] or '*'
            attrs['class'] = parts[1]
        else:
            tag = selector

        return tag, attrs if attrs else None

    def _find_matching_end_tag(self, tag, start_pos):
        """
        Encuentra la posición en el HTML donde se cierra la etiqueta 'tag',
        considerando etiquetas anidadas.
        """
        tag_open = f"<{tag}"
        tag_close = f"</{tag}>"
        nesting_level = 1
        pos = start_pos

        while nesting_level > 0 and pos < self.length:
            next_open = self.html.find(tag_open, pos)
            next_close = self.html.find(tag_close, pos)

            if next_close == -1:
                return -1

            if next_open == -1 or next_close < next_open:
                nesting_level -= 1
                pos = next_close + len(tag_close)
            else:
                tag_attr_pos = next_open + len(tag_open)
                if (tag_attr_pos < self.length and
                    self.html[tag_attr_pos] in [' ', '>', '\t', '\n', '/']):
                    gt_pos = self.html.find(">", next_open)
                    if gt_pos == -1:
                        return -1
                    if self.html[gt_pos - 1] != '/':
                        nesting_level += 1
                    pos = gt_pos + 1
                else:
                    pos = next_open + 1

        if nesting_level == 0:
            return pos - len(tag_close)
        return -1

    def _parse_attrs(self, attrs_str):
        """
        Convierte una cadena de atributos HTML en un diccionario.
        Soporta comillas dobles, simples, sin comillas y atributos booleanos.
        """
        if not attrs_str:
            return {}
        attrs = {}
        i = 0
        current_attr = ""
        in_value = False
        quote_char = None
        value = ""

        while i < len(attrs_str):
            char = attrs_str[i]
            if in_value:
                if char == quote_char:
                    in_value = False
                    attrs[current_attr.strip()] = value
                    current_attr = ""
                    value = ""
                else:
                    value += char
            elif char == '=':
                current_attr = current_attr.strip()
                i += 1
                while i < len(attrs_str) and attrs_str[i].isspace():
                    i += 1
                if i < len(attrs_str) and attrs_str[i] in ['"', "'"]:
                    quote_char = attrs_str[i]
                    in_value = True
                    i += 1
                    continue
                else:
                    value_end = i
                    while value_end < len(attrs_str) and not attrs_str[value_end].isspace():
                        value_end += 1
                    attrs[current_attr] = attrs_str[i:value_end]
                    i = value_end
                    current_attr = ""
                    continue
            elif char.isspace():
                if current_attr:
                    attrs[current_attr.strip()] = True
                    current_attr = ""
            else:
                current_attr += char
            i += 1

        if current_attr:
            attrs[current_attr.strip()] = True

        return attrs

    def _attrs_match(self, element_attrs, search_attrs):
        """
        Verifica que los atributos del elemento coincidan con los de búsqueda.
        Para la clase se permite que la clase buscada esté presente en la lista.
        """
        for key, value in search_attrs.items():
            if key not in element_attrs:
                return False

            if key == 'class':
                if element_attrs[key] is True:
                    return False
                element_class = str(element_attrs[key])
                search_class = str(value)
                element_classes = element_class.split()
                if search_class not in element_classes:
                    # Soporte para coincidencia parcial legacy
                    if search_class not in element_class:
                        return False
            elif element_attrs[key] != value:
                return False

        return True

    def _consolidate_attrs(self, attrs, class_name, id):
        """
        Consolida parámetros de atributos en un único diccionario.
        """
        result = attrs.copy() if attrs else {}
        if class_name:
            result['class'] = class_name
        if id:
            result['id'] = id
        return result if result else None


class Element:
    def __init__(self, tag, attrs, content, raw_html, self_closing=False):
        self.name = tag
        self.attrs = attrs if attrs else {}
        self.content = content
        self.raw_html = raw_html
        self.self_closing = self_closing
        # El parser para el contenido interno se inicializa bajo demanda
        self._parser = None

    @property
    def parser(self):
        """Inicialización perezosa del parser para el contenido interno."""
        if self._parser is None and not self.self_closing:
            self._parser = MicroBS4(self.content)
        return self._parser

    def find(self, tag, attrs=None, class_name=None, id=None):
        """
        Busca la primera ocurrencia de la etiqueta dentro de este elemento.
        """
        if self.self_closing:
            return None
        return self.parser.find(tag, attrs, class_name, id)

    def find_all(self, tag, attrs=None, class_name=None, id=None, limit=None):
        """
        Busca todas las ocurrencias de la etiqueta dentro de este elemento.
        """
        if self.self_closing:
            return []
        return self.parser.find_all(tag, attrs, class_name, id, limit)

    def select_one(self, selector):
        """
        Selecciona el primer elemento que coincide con el selector.
        """
        if self.self_closing:
            return None
        return self.parser.select_one(selector)

    def select(self, selector):
        """
        Selecciona todos los elementos que coinciden con el selector.
        """
        if self.self_closing:
            return []
        return self.parser.select(selector)

    def get_text(self, separator=" "):
        """
        Extrae el texto del contenido eliminando las etiquetas HTML.
        """
        if self.self_closing:
            return ""
        result = ""
        i = 0
        in_tag = False
        while i < len(self.content):
            char = self.content[i]
            if char == "<":
                in_tag = True
            elif char == ">":
                in_tag = False
            elif not in_tag:
                result += char
            i += 1
        words = [word for word in result.split() if word]
        return separator.join(words)

    def children(self, tag=None):
        """
        Obtiene los elementos hijo directos.
        Si se especifica 'tag', se filtra por esa etiqueta.
        """
        if self.self_closing:
            return []
        all_tags = tag.split(',') if tag else [
            "div", "p", "span", "a", "ul", "ol", "li", "h1", "h2", "h3",
            "h4", "h5", "h6", "table", "tr", "td", "th", "img", "form",
            "input", "button", "select", "option", "textarea", "label", "br", "hr",
            "header", "footer", "nav", "section", "article", "aside", "main"
        ]
        children = []
        for t in all_tags:
            t = t.strip()
            elems = self.parser.find_all(t)
            for elem in elems:
                if self._is_direct_child(elem):
                    children.append(elem)
        return children

    def _is_direct_child(self, potential_child):
        """
        Heurística para determinar si un elemento es hijo directo basándose en la posición.
        """
        child_html = potential_child.raw_html
        child_start = self.content.find(child_html)
        if child_start == -1:
            return False
        prefix = self.content[:child_start]
        last_close_tag = prefix.rfind(">")
        if last_close_tag == -1:
            return True
        between = prefix[last_close_tag + 1:].strip()
        return not between or between.isspace()

    def find_list_items(self):
        """Si el elemento es una lista (<ul> o <ol>), retorna sus <li>."""
        if self.name in ["ul", "ol"]:
            return self.find_all("li")
        return []

    def get_attribute(self, attr_name):
        """Obtiene el valor de un atributo específico."""
        return self.attrs.get(attr_name, None)

    def get_url(self):
        """Obtiene la URL del atributo href si el elemento es un enlace (<a>)."""
        if self.name == "a" and "href" in self.attrs:
            return self.attrs["href"]
        return None

    def __str__(self):
        return self.raw_html

    def __repr__(self):
        if not self.attrs:
            return f"<{self.name}>"
        else:
            attrs_str = ' '.join([f'{k}="{v}"' for k, v in self.attrs.items()])
            return f"<{self.name} {attrs_str}>"

