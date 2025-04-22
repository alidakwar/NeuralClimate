import * as React from 'react';
import * as L from 'leaflet';
import countyBoundaries from './countyBoundaries.ts';  // Import the county boundaries data
import 'leaflet/dist/leaflet.css';

interface CountyGeoJSON {
  type: 'FeatureCollection';
  features: any[];
}

interface County {
  name: string;
  coordinates: number[][][];
}

const MAP_TILE = L.tileLayer(
  `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`,
  {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }
);

const mapStyles: React.CSSProperties = {
  overflow: 'hidden',
  width: '100%',
  height: '100vh',
};

const controlContainerStyles: React.CSSProperties = {
  position: 'absolute',
  top: '10px',
  left: '10px',
  zIndex: 1000,
  backgroundColor: 'white',
  padding: '10px',
  borderRadius: '5px',
  boxShadow: '0 0 10px rgba(0,0,0,0.2)',
};

const selectStyles: React.CSSProperties = {
  padding: '8px',
  marginRight: '10px',
  borderRadius: '4px',
  border: '1px solid #ccc',
};

const buttonStyles: React.CSSProperties = {
  padding: '8px 16px',
  backgroundColor: '#f44336',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
};

function App(): JSX.Element {
  const mapRef = React.useRef<L.Map | null>(null);
  const layerRef = React.useRef<L.LayerGroup | null>(null);
  const controlRef = React.useRef<L.Control.Layers | null>(null);
  const [selectedCounty, setSelectedCounty] = React.useState<County | null>(null);
  const [counties] = React.useState<County[]>(countyBoundaries);

  const mapParams: L.MapOptions = {
    center: L.latLng(31.9686, -99.9018),
    zoom: 6,
    zoomControl: false,
    maxBounds: L.latLngBounds(L.latLng(-150, -240), L.latLng(150, 240)),
    layers: [MAP_TILE],
  };

  /**
   * Map Instance Creation
   */
  React.useEffect(() => {
    mapRef.current = L.map('map', mapParams);
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
      }
    };
  }, []);

  /**
   * Add Controls
   */
  React.useEffect(() => {
    if (!mapRef.current) return;

    controlRef.current = L.control
      .layers({
        OpenStreetMap: MAP_TILE,
      })
      .addTo(mapRef.current);

    L.control
      .zoom({
        position: 'topright',
      })
      .addTo(mapRef.current);
  }, []);

  /**
   * Load GeoJSON and draw the county boundaries
   */
  React.useEffect(() => {
    if (!mapRef.current) return;

    // Clear existing layers
    if (layerRef.current) {
      layerRef.current.clearLayers();
    }

    layerRef.current = L.layerGroup().addTo(mapRef.current);

    // Add polygons for each county
    counties.forEach(county => {
      const isSelected = selectedCounty?.name === county.name;
      L.geoJSON({
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: county.coordinates
        }
      } as GeoJSON.Feature, {
        style: {
          color: isSelected ? 'red' : 'blue',
          fillColor: isSelected ? 'red' : 'blue',
          fillOpacity: isSelected ? 0.5 : 0.3,
          weight: isSelected ? 3 : 2
        }
      }).addTo(layerRef.current!);
    });

  }, [selectedCounty, counties]);

  const handleCountySelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedName = event.target.value;
    const county = counties.find(c => c.name === selectedName);
    setSelectedCounty(county || null);
  };

  const handleClearSelection = () => {
    setSelectedCounty(null);
  };

  return (
    <React.Fragment>
      <div id="map" style={mapStyles} />
      <div style={controlContainerStyles}>
        <select 
          style={selectStyles} 
          value={selectedCounty?.name || ''} 
          onChange={handleCountySelect}
        >
          <option value="">Select a county</option>
          {counties.map((county, index) => (
            <option key={index} value={county.name}>
              {county.name}
            </option>
          ))}
        </select>
        <button 
          style={buttonStyles} 
          onClick={handleClearSelection}
          disabled={!selectedCounty}
        >
          Clear Selection
        </button>
      </div>
    </React.Fragment>
  );
}

export default App;
