"""

Grid3 data source implementation module.

Authors:

Date:

"""

import httpx
from nigeria_geodata.config import Config
from nigeria_geodata.core import ASyncBaseDataSource, SyncBaseDataSource
from nigeria_geodata.datasources import DataSource
from nigeria_geodata.utils.common import in_jupyter_notebook
import pandas as pd
import tabulate


class Grid3(SyncBaseDataSource):
    service_url: str = Config.get_service_url(DataSource.GRID3)
    health_check_url: str = Config.get_health_check_url(DataSource.GRID3)
    service_info_url: str = Config.get_service_info_url(DataSource.GRID3)
    # todo - automaticlly update version
    headers = {"user-agent": "nigeria_geodata/dev-0.0.1"}

    def health_check(self):
        with httpx.Client() as client:
            response = client.get(self.health_check_url, headers=self.headers)
            return response.status_code == 200

    def api_client(self, service_url: str):
        if self.health_check():
            with httpx.Client() as client:
                response = client.get(service_url, headers=self.headers)
                return response.json()
        return None

    def info(self):
        # return the server info with additional data such as total number of available datasets
        nigeria_services = self.get_services()
        response = self.api_client(self.service_info_url)
        response.update(
            {
                "Available Datasets": len(nigeria_services),
            }
        )

        if in_jupyter_notebook():
            return pd.DataFrame(response)
        else:
            table_data = [
                list(
                    zip(
                        [
                            response["Available Datasets"],
                            response["currentVersion"],
                            response["fullVersion"],
                            response["owningSystemUrl"],
                            response["owningTenant"],
                        ],
                    )
                )
            ]
            headers = [
                "Available Datasets",
                "currentVersion",
                "fullVersion",
                "owningSystemUrl",
                "owningTenant",
            ]
            return tabulate.tabulate(table_data, headers=headers, tablefmt="grid")

    def get_services(self):
        # for grid3, we need to hit the ArcGIS server root directory and then filter for Nigeria data alone
        # based on review of the datasets, Nigeria is either represented as Nigeria or NGA
        response = self.api_client(self.service_url)
        nigeria_services = list(
            filter(
                lambda x: "NGA" in x["name"] or "NIGERIA" in x["name"].upper(),
                response["services"],
            )
        )

        return nigeria_services

    def list_data(self):
        """List available datasets from the datasource"""
        nigeria_services = self.get_services()
        # todo, it's returning a tabulate object which is not accessible programmatically
        # e.g when you do a search and it returns 2 result, instead of
        # typing the name of the data manually, the user should be able to use list indexing to grab the name
        # but as it stands it's not possible, so we need to find a way to make it possible, while also providing a nice cli and jupyter notebook view
        data = {
            "Name": [service["name"] for service in nigeria_services],
            "Type": [service["type"] for service in nigeria_services],
            "Description": [
                service.get("description", "No description")
                for service in nigeria_services
            ],
        }

        if in_jupyter_notebook():
            return pd.DataFrame(data)
        else:
            table_data = list(zip(data["Name"], data["Type"], data["Description"]))
            headers = ["Name", "Type", "Description"]
            return tabulate.tabulate(table_data, headers=headers, tablefmt="grid")

    def search(self, query: str):
        services = self.get_services()
        search_results = list(
            filter(
                lambda x: query.upper() in x["name"].upper(),
                services,
            )
        )

        data = {
            "Name": [service["name"] for service in search_results],
            "Type": [service["type"] for service in search_results],
            "Description": [
                service.get("description", "No description")
                for service in search_results
            ],
        }

        if in_jupyter_notebook():
            return pd.DataFrame(data)
        else:
            table_data = list(zip(data["Name"], data["Type"], data["Description"]))
            headers = ["Name", "Type", "Description"]
            return tabulate.tabulate(table_data, headers=headers, tablefmt="grid")

        # then they can pass the dataset name to the get_data() function and also pass a bounding box to it.
        # in the future, we can do search by bounding box

    def get_data(self, name: str):
        # retreive the data from the feature server
        return super().get_data()

    def __repr__(self) -> str:
        return "<Grid3Data>"


class AsyncGrid3(ASyncBaseDataSource):
    service_url: str = Config.get_service_url(DataSource.GRID3)

    async def list_data(self):
        # list available datasets in the data source
        # preview = true to preview on a static map as thumbnail, interactive = true to preview on interactive map e.g lon board
        ...

    def __repr__(self) -> str:
        return "<AsyncGrid3Data>"


if __name__ == "__main__":
    data_source = Grid3()
    search_results = data_source.search("health")
    data = data_source.get_data(
        "GRID3_Nigeria__Lagos__Health_Care_Facilities",
    )
