"""
Module: cli.py

Command-line interface (CLI) for interacting with the GRID3 data source.

This module provides commands for managing and querying the GRID3 data source.
It supports both synchronous and asynchronous operations, allowing users to
list, search, filter, and retrieve information about datasets.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Commands:
    - docs: Launches the documentation website.
    - grid3 list-data: Lists available datasets from the GRID3 database.
    - async-grid3 list-data: Asynchronously lists available datasets from the GRID3 database.
    - grid3 search: Searches for data from the GRID3 database.
    - async-grid3 search: Asynchronously searches for data from the GRID3 database.
    - grid3 filter: Filters data from the GRID3 database.
    - async-grid3 filter: Asynchronously filters data from the GRID3 database.
    - grid3 info: Retrieves information about a specific dataset from the GRID3 database.
    - async-grid3 info: Asynchronously retrieves information about a specific dataset from the GRID3 database.
"""

import json
from typing import Any, Dict, List
import typer
from rich.progress import Progress
from nigeria_geodata import Grid3, AsyncGrid3
from rich.console import Console
from rich import print
from rich.table import Table
from typing_extensions import Annotated
import asyncio
import inspect
from functools import wraps, partial

from nigeria_geodata.utils.enums import NigeriaState


# ref - https://github.com/fastapi/typer/issues/88
class AsyncTyper(typer.Typer):
    @staticmethod
    def maybe_run_async(decorator, f):
        if inspect.iscoroutinefunction(f):

            @wraps(f)
            def runner(*args, **kwargs):
                return asyncio.run(f(*args, **kwargs))

            decorator(runner)
        else:
            decorator(f)
        return f

    def callback(self, *args, **kwargs):
        decorator = super().callback(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

    def command(self, *args, **kwargs):
        decorator = super().command(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)


console = Console()
app = typer.Typer()
grid3_app = typer.Typer()
async_grid3_app = AsyncTyper()
# Since there will potentialy be multiple datasources, we can create subcommands for each.
# Grid3 subcommands
app.add_typer(grid3_app, name="grid3")
app.add_typer(async_grid3_app, name="async-grid3")


def render_as_table(data: List[Dict[str, Any]], title: str):
    """
    Renders a list of dictionaries as a table.

    Args:
        data (List[Dict[str, Any]]): The data to render as a table.
        title (str): The title for the table.
    """
    # Create a table
    table = Table(title=title)

    for key in data[0].keys():
        table.add_column(key, style="cyan", no_wrap=True)
    # Add the rows
    for item in data:
        values = [str(value) for value in item.values()]
        table.add_row(*values)
    console.print(table)


# DOCS
@app.command("docs")
def documentation():
    """
    Launches the documentation website.
    """
    print("Opening documentation website ...")
    typer.launch("https://jeafreezy.github.io/nigeria_geodata")


# LIST DATA
@grid3_app.command("list-data")
def grid3_list_data(
    table: Annotated[
        bool,
        typer.Option(
            help="If to render results as a table or not. Use --table to enable table (default) or --notable to disable table."
        ),
    ] = True,
):
    """
    Lists the available datasets for Nigeria from the GRID3 database.

    Args:
        table (bool): If True, renders results as a table; otherwise, prints the results directly.
    """
    with Progress(transient=True) as progress:
        task = progress.add_task("[green]Fetching datasets", total=None)
        grid3 = Grid3()
        progress.start_task(task)
        results = grid3.list_data(dataframe=False)
        progress.update(task, completed=True)
        if table:
            render_as_table(results, "Available datasets")
        else:
            print(results)


@async_grid3_app.command("list-data")
async def async_grid3_list_data(
    table: Annotated[
        bool,
        typer.Option(
            help="If to render results as a table or not. Use --table to enable table (default) or --notable to disable table."
        ),
    ] = True,
):
    """
    Asynchronously lists the available datasets for Nigeria from the GRID3 database.

    Args:
        table (bool): If True, renders results as a table; otherwise, prints the results directly.
    """
    with Progress(transient=True) as progress:
        task = progress.add_task("[green]Fetching datasets", total=None)
        agrid3 = AsyncGrid3()
        progress.start_task(task)
        results = await agrid3.list_data(dataframe=False)
        progress.update(task, completed=True)
        if table:
            render_as_table(results, "Available datasets")
        else:
            print(results)


# SEARCH
@grid3_app.command("search")
def grid3_search(
    query: Annotated[str, typer.Option(help="The search query.")],
    table: Annotated[
        bool,
        typer.Option(
            help="If to render results as a table or not. Use --table to enable table (default) or --notable to disable table."
        ),
    ] = True,
):
    """
    Searches for data from the GRID3 database.

    Args:
        query (str): The search query.
        table (bool): If True, renders results as a table; otherwise, prints the results directly.
    """
    with Progress(transient=True) as progress:
        task = progress.add_task(f"[green]Searching for '{query}' ...", total=None)
        grid3 = Grid3()
        progress.start_task(task)
        search_results = grid3.search(query, False)
        progress.update(task, completed=True)
        if len(search_results) > 0 and table:
            render_as_table(search_results, f"Search Results for '{query}'")
            print(f"Search returned {len(search_results)} results.")
        else:
            print(search_results)


@async_grid3_app.command("search")
async def async_grid3_search(
    query: Annotated[str, typer.Option(help="The search query.")],
    table: Annotated[
        bool,
        typer.Option(
            help="If to render results as a table or not. Use --table to enable table (default) or --notable to disable table."
        ),
    ] = True,
):
    """
    Asynchronously searches for data from the GRID3 database.

    Args:
        query (str): The search query.
        table (bool): If True, renders results as a table; otherwise, prints the results directly.
    """
    with Progress(transient=True) as progress:
        task = progress.add_task(f"[green]Searching for '{query}' ...", total=None)
        agrid3 = AsyncGrid3()
        progress.start_task(task)
        search_results = await agrid3.search(query, False)
        progress.update(task, completed=True)
        if len(search_results) > 0 and table:
            render_as_table(search_results, f"Search Results for '{query}'")
            print(f"Search returned {len(search_results)} results.")
        else:
            print(search_results)


# FILTER
@grid3_app.command("filter")
def grid3_filter(
    data_name: Annotated[
        str,
        typer.Option(
            help="The name of the data to filter. e.g --data-name Nigeria_Health..."
        ),
    ],
    state: Annotated[
        str,
        typer.Option(
            help=f"The name of the state to filter for. Any from {[x.name for x in NigeriaState]} e.g --data-name abuja."
        ),
    ] = None,
    bbox: Annotated[
        str,
        typer.Option(
            help="The bounding box to filter with i.e 'min_x, min_y, max_x, max_y'. e.g --bbox '20.0, 12.3, 21.4, 34.5'."
        ),
    ] = None,
    aoi_geometry: Annotated[
        str,
        typer.Option(
            help="The aoi as a GeoJSON geometry string e.g --aoi-geometry '{'type': 'Point', 'coordinates': [30, 10]}'"
        ),
    ] = None,
    table: Annotated[
        bool,
        typer.Option(
            help="If to render results as a table or not. Use --table to enable table (default) or --notable to disable table."
        ),
    ] = True,
):
    """
    Filters data from the GRID3 database.

    Args:
        data_name (str): The name of the data to filter.
        state (str, optional): The name of the state to filter for.
        bbox (str, optional): The bounding box to filter with.
        aoi_geometry (str, optional): The area of interest as a GeoJSON geometry string.
        table (bool): If True, renders results as a table; otherwise, prints the results directly.
    """

    with Progress(transient=True) as progress:
        task = progress.add_task(f"[green]Filtering {data_name} data...", total=None)
        grid3 = Grid3()
        progress.start_task(task)
        search_results = grid3.filter(
            data_name=data_name,
            state=state,
            bbox=[float(num.strip()) for num in bbox.split(",")] if bbox else None,
            aoi_geometry=json.loads(aoi_geometry) if aoi_geometry else None,
            preview=False,
            geodataframe=False,
        )
        progress.update(task, completed=True)
        if len(search_results) > 0 and table:
            render_as_table(search_results, f"Filtering results for '{data_name}'")
        else:
            print(search_results)


@async_grid3_app.command("filter")
async def async_grid3_filter(
    data_name: Annotated[
        str,
        typer.Option(
            help="The name of the data to filter. e.g --data-name Nigeria_Health..."
        ),
    ],
    state: Annotated[
        str,
        typer.Option(
            help=f"The name of the state to filter for. Any from {[x.name for x in NigeriaState]} e.g --data-name abuja."
        ),
    ] = None,
    bbox: Annotated[
        str,
        typer.Option(
            help="The bounding box to filter with i.e 'min_x, min_y, max_x, max_y'. e.g --bbox '20.0, 12.3, 21.4, 34.5'."
        ),
    ] = None,
    aoi_geometry: Annotated[
        str,
        typer.Option(
            help="The aoi as a GeoJSON geometry string e.g --aoi-geometry '{'type': 'Point', 'coordinates': [30, 10]}'"
        ),
    ] = None,
    table: Annotated[
        bool,
        typer.Option(
            help="If to render results as a table or not. Use --table to enable table (default) or --notable to disable table."
        ),
    ] = True,
):
    """
    Asynchronously filters data from the GRID3 database.

    Args:
        data_name (str): The name of the data to filter.
        state (str, optional): The name of the state to filter for.
        bbox (str, optional): The bounding box to filter with.
        aoi_geometry (str, optional): The area of interest as a GeoJSON geometry string.
        table (bool): If True, renders results as a table; otherwise, prints the results directly.
    """
    with Progress(transient=True) as progress:
        task = progress.add_task(f"[green]Filtering {data_name} data...", total=None)
        agrid3 = AsyncGrid3()
        progress.start_task(task)
        search_results = await agrid3.filter(
            data_name=data_name,
            state=state,
            bbox=[float(num.strip()) for num in bbox.split(",")] if bbox else None,
            aoi_geometry=json.loads(aoi_geometry) if aoi_geometry else None,
            preview=False,
            geodataframe=False,
        )
        progress.update(task, completed=True)
        if len(search_results) > 0 and table:
            render_as_table(search_results, f"Filtering results for '{data_name}'")
        else:
            print(search_results)


@grid3_app.command("info")
def grid3_info(
    data_name: Annotated[
        str,
        typer.Option(
            help="The name of the data to get information on. e.g --data-name Nigeria_Health..."
        ),
    ],
):
    """
    Retrieves information about a specific dataset from the GRID3 database.

    Args:
        data_name (str): The name of the data to get information on.
    """
    with Progress(transient=True) as progress:
        task = progress.add_task(
            f"[green]Getting information on '{data_name}' ...", total=None
        )
        grid3 = Grid3()
        progress.start_task(task)
        info = grid3.info(data_name, False)
        progress.update(task, completed=True)
        print(info)


@async_grid3_app.command("info")
async def async_grid3_info(
    data_name: Annotated[
        str,
        typer.Option(
            help="The name of the data to get information on. e.g --data-name Nigeria_Health..."
        ),
    ],
):
    """
    Asynchronously retrieves information about a specific dataset from the GRID3 database.

    Args:
        data_name (str): The name of the data to get information on.
    """

    with Progress(transient=True) as progress:
        task = progress.add_task(
            f"[green]Getting information on '{data_name}' ...", total=None
        )
        agrid3 = AsyncGrid3()
        progress.start_task(task)
        info = await agrid3.info(data_name, False)
        progress.update(task, completed=True)
        print(info)
