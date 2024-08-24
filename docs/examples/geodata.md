# Geodata Utils


The `Geodata Utils` module provides various utility functions for working with geospatial data. These utilities are designed to simplify common tasks such as converting between coordinate formats, validating geometries, and handling spatial references.

**Get all Nigeria States**

```python
from nigeria_geodata.utils import GeodataUtils
nigeria_states = GeodataUtils.get_states()
print(nigeria_states)
# returns all the states in Nigeria as a GeoJSON FeatureCollection.
```

**Get the boundary of a Nigeria State**

```python
from nigeria_geodata.utils import GeodataUtils, NigeriaState

lagos_state = GeodataUtils.get_state_geometry(NigeriaState.LAGOS)
print(lagos_state)
# returns Lagos state boudary as a GeoJSON geometry.
```
