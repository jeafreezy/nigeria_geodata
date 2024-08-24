# CLI

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `async-grid3`
* `docs`: Launches the documentation website.
* `grid3`

## `async-grid3`

**Usage**:

```console
$ async-grid3 [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `filter`: Asynchronously filters data from the GRID3...
* `info`: Asynchronously retrieves information about...
* `list-data`: Asynchronously lists the available...
* `search`: Asynchronously searches for data from the...

### `async-grid3 filter`

Asynchronously filters data from the GRID3 database.

Args:
    data_name (str): The name of the data to filter.
    state (str, optional): The name of the state to filter for.
    bbox (str, optional): The bounding box to filter with.
    aoi_geometry (str, optional): The area of interest as a GeoJSON geometry string.
    table (bool): If True, renders results as a table; otherwise, prints the results directly.

**Usage**:

```console
$ async-grid3 filter [OPTIONS]
```

**Options**:

* `--data-name TEXT`: The name of the data to filter. e.g --data-name Nigeria_Health...  [required]
* `--state TEXT`: The name of the state to filter for. Any from ['ABIA', 'ADAMAWA', 'AKWA_IBOM', 'ANAMBRA', 'BAUCHI', 'BAYELSA', 'BENUE', 'BORNO', 'CROSS_RIVER', 'DELTA', 'EBONYI', 'EDO', 'EKITI', 'ENUGU', 'GOMBE', 'IMO', 'JIGAWA', 'KADUNA', 'KANO', 'KATSINA', 'KEBBI', 'KOGI', 'KWARA', 'LAGOS', 'NASARAWA', 'NIGER', 'OGUN', 'ONDO', 'OSUN', 'OYO', 'PLATEAU', 'RIVERS', 'SOKOTO', 'TARABA', 'YOBE', 'ZAMFARA', 'FCT'] e.g --data-name abuja.
* `--bbox TEXT`: The bounding box to filter with i.e 'min_x, min_y, max_x, max_y'. e.g --bbox '20.0, 12.3, 21.4, 34.5'.
* `--aoi-geometry TEXT`: The aoi as a GeoJSON geometry string e.g --aoi-geometry '{'type': 'Point', 'coordinates': [30, 10]}'
* `--table / --no-table`: If to render results as a table or not. Use --table to enable table (default) or --notable to disable table.  [default: table]
* `--help`: Show this message and exit.

### `async-grid3 info`

Asynchronously retrieves information about a specific dataset from the GRID3 database.

Args:
    data_name (str): The name of the data to get information on.

**Usage**:

```console
$ async-grid3 info [OPTIONS]
```

**Options**:

* `--data-name TEXT`: The name of the data to get information on. e.g --data-name Nigeria_Health...  [required]
* `--help`: Show this message and exit.

### `async-grid3 list-data`

Asynchronously lists the available datasets for Nigeria from the GRID3 database.

Args:
    table (bool): If True, renders results as a table; otherwise, prints the results directly.

**Usage**:

```console
$ async-grid3 list-data [OPTIONS]
```

**Options**:

* `--table / --no-table`: If to render results as a table or not. Use --table to enable table (default) or --notable to disable table.  [default: table]
* `--help`: Show this message and exit.

### `async-grid3 search`

Asynchronously searches for data from the GRID3 database.

Args:
    query (str): The search query.
    table (bool): If True, renders results as a table; otherwise, prints the results directly.

**Usage**:

```console
$ async-grid3 search [OPTIONS]
```

**Options**:

* `--query TEXT`: The search query.  [required]
* `--table / --no-table`: If to render results as a table or not. Use --table to enable table (default) or --notable to disable table.  [default: table]
* `--help`: Show this message and exit.

## `docs`

Launches the documentation website.

**Usage**:

```console
$ docs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `grid3`

**Usage**:

```console
$ grid3 [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `filter`: Filters data from the GRID3 database.
* `info`: Retrieves information about a specific...
* `list-data`: Lists the available datasets for Nigeria...
* `search`: Searches for data from the GRID3 database.

### `grid3 filter`

Filters data from the GRID3 database.

Args:
    data_name (str): The name of the data to filter.
    state (str, optional): The name of the state to filter for.
    bbox (str, optional): The bounding box to filter with.
    aoi_geometry (str, optional): The area of interest as a GeoJSON geometry string.
    table (bool): If True, renders results as a table; otherwise, prints the results directly.

**Usage**:

```console
$ grid3 filter [OPTIONS]
```

**Options**:

* `--data-name TEXT`: The name of the data to filter. e.g --data-name Nigeria_Health...  [required]
* `--state TEXT`: The name of the state to filter for. Any from ['ABIA', 'ADAMAWA', 'AKWA_IBOM', 'ANAMBRA', 'BAUCHI', 'BAYELSA', 'BENUE', 'BORNO', 'CROSS_RIVER', 'DELTA', 'EBONYI', 'EDO', 'EKITI', 'ENUGU', 'GOMBE', 'IMO', 'JIGAWA', 'KADUNA', 'KANO', 'KATSINA', 'KEBBI', 'KOGI', 'KWARA', 'LAGOS', 'NASARAWA', 'NIGER', 'OGUN', 'ONDO', 'OSUN', 'OYO', 'PLATEAU', 'RIVERS', 'SOKOTO', 'TARABA', 'YOBE', 'ZAMFARA', 'FCT'] e.g --data-name abuja.
* `--bbox TEXT`: The bounding box to filter with i.e 'min_x, min_y, max_x, max_y'. e.g --bbox '20.0, 12.3, 21.4, 34.5'.
* `--aoi-geometry TEXT`: The aoi as a GeoJSON geometry string e.g --aoi-geometry '{'type': 'Point', 'coordinates': [30, 10]}'
* `--table / --no-table`: If to render results as a table or not. Use --table to enable table (default) or --notable to disable table.  [default: table]
* `--help`: Show this message and exit.

### `grid3 info`

Retrieves information about a specific dataset from the GRID3 database.

Args:
    data_name (str): The name of the data to get information on.

**Usage**:

```console
$ grid3 info [OPTIONS]
```

**Options**:

* `--data-name TEXT`: The name of the data to get information on. e.g --data-name Nigeria_Health...  [required]
* `--help`: Show this message and exit.

### `grid3 list-data`

Lists the available datasets for Nigeria from the GRID3 database.

Args:
    table (bool): If True, renders results as a table; otherwise, prints the results directly.

**Usage**:

```console
$ grid3 list-data [OPTIONS]
```

**Options**:

* `--table / --no-table`: If to render results as a table or not. Use --table to enable table (default) or --notable to disable table.  [default: table]
* `--help`: Show this message and exit.

### `grid3 search`

Searches for data from the GRID3 database.

Args:
    query (str): The search query.
    table (bool): If True, renders results as a table; otherwise, prints the results directly.

**Usage**:

```console
$ grid3 search [OPTIONS]
```

**Options**:

* `--query TEXT`: The search query.  [required]
* `--table / --no-table`: If to render results as a table or not. Use --table to enable table (default) or --notable to disable table.  [default: table]
* `--help`: Show this message and exit.
