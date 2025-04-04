# micropython-microbs4


A lightweight HTML parser for MicroPython inspired by BeautifulSoup4, optimized for resource-constrained environments.

## Features

- **Lightweight**: Designed specifically for MicroPython and embedded systems
- **CSS Selector Support**: Simple CSS selector syntax for element selection
- **Efficient Parsing**: Optimized for memory usage with minimal dependencies
- **Caching**: Internal caching mechanism to improve performance for repeated searches
- **Consistent API**: Familiar interface for those coming from BeautifulSoup4

## Installation

Simply copy the `microbs4.py` file to your MicroPython device.

```python
# For example, using ampy:
ampy --port /dev/ttyUSB0 put microbs4.py
```

## Usage

### Basic Parsing

```python
from microbs4 import MicroBS4

# Parse HTML content
html = """
<div class="container">
  <h1 class="title">Hello World</h1>
  <p>This is a paragraph.</p>
  <ul class="list">
    <li class="item">Item 1</li>
    <li class="item selected">Item 2</li>
    <li class="item">Item 3</li>
  </ul>
</div>
"""

soup = MicroBS4(html)
```

### Finding Elements

```python
# Find the first occurrence of a tag
title = soup.find("h1")
print(title.get_text())  # "Hello World"

# Find elements with specific attributes
container = soup.find("div", class_name="container")

# Find elements with multiple attributes
element = soup.find("li", attrs={"class": "item", "id": "special"})

# Find all matching elements
items = soup.find_all("li", class_name="item")
for item in items:
    print(item.get_text())
```

### CSS Selectors

```python
# Select by tag
paragraphs = soup.select("p")

# Select by class
items = soup.select(".item")

# Select by ID
header = soup.select_one("#header")

# Select by tag and class
selected_item = soup.select_one("li.selected")
```

### Element Navigation

```python
# Get direct children of an element
container = soup.find("div", class_name="container")
children = container.children()

# Get filtered children
list_items = container.children("li")

# Get specific attributes
link = soup.find("a")
url = link.get_attribute("href")
# Or use the convenience method
url = link.get_url()

# Extract text content
text = element.get_text()
```

## Advanced Features

### Multiple Class Support

```python
# Find elements with multiple classes
element = soup.find("div", class_name="multi class test")

# This works for CSS selectors too
elements = soup.select(".multi.class.test")
```

### List Operations

```python
# If the element is a list (<ul> or <ol>), get its items
ul_element = soup.find("ul")
list_items = ul_element.find_list_items()
```

### Nested Searches

```python
# Find elements within elements
container = soup.find("div", class_name="container")
title = container.find("h1")
items = container.find_all("li")
```

## Limitations

- Does not support all BeautifulSoup4 features
- Limited CSS selector support (basic tag, class, and ID selectors)
- No XPath support
- No DOM manipulation, only parsing and searching

## Performance Considerations

MicroBS4 is optimized for MicroPython environments with limited resources. To maximize performance:

- Use the most specific selectors possible
- Cache frequently accessed elements
- Limit the use of `.find_all()` on large documents
- When possible, use `.children()` instead of global searches


## Contributing

Please feel free to submit a Pull Request.
