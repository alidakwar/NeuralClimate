export interface City {
  name: string;
  latLng: number[];
  region: string;
  regionColor: string;
}

export interface Region {
  name: string;
  color: string;
  coordinates: number[][];
}

export const regionData: Region[] = [
  {
    name: 'Panhandle',
    color: '#808000',
    coordinates: [
      [36.519194, -100.097896],
      [36.508960, -102.988601],
      [34.289911, -103.079542],
      [34.338877, -100.044183],
      [36.519194, -100.097896]
    ]
  },
  {
    name: 'North Texas',
    color: '#FFFF00',
    coordinates: [
      [34.3, -100.0],
      [34.3, -95.5],
      [33.5, -95.5],
      [32.5, -96.5],
      [32.0, -97.5],
      [32.0, -98.5],
      [33.0, -99.5],
      [33.5, -100.0]
    ]
  },
  {
    name: 'West Texas',
    color: '#A52A2A',
    coordinates: [
      [31.953338, -106.666652],
      [30.371389, -104.923056],
      [29.500000, -104.500000],
      [29.300000, -103.500000],
      [29.200000, -102.800000],
      [29.500000, -101.943967],
      [29.847984, -101.943967],
      [30.667592, -100.416215],
      [31.463800, -100.437000],
      [32.470500, -100.405900],
      [32.717600, -100.917600],
      [33.653146, -100.036307],
      [34.289911, -103.079542],
      [34.338877, -100.044183],
      [33.097427, -98.471555],
      [32.598801, -97.985942],
      [31.997300, -102.077900],
      [31.845700, -102.367600],
      [30.588200, -103.894600],
      [31.415800, -103.493900],
      [31.953338, -106.666652]
    ]
  },
  {
    name: 'Hill Country',
    color: '#90EE90',
    coordinates: [
      [30.5, -100.2],
      [30.5, -98.5],
      [30.2, -98.2],
      [29.5, -98.8],
      [29.5, -99.5],
      [30.0, -100.0],
      [30.5, -100.2]
    ]
  },
  {
    name: 'Central Texas',
    color: '#800080',
    coordinates: [
      [32.0, -98.5],
      [32.0, -97.5],
      [31.5, -97.0],
      [30.8, -97.5],
      [30.2, -98.2],
      [30.5, -98.5],
      [31.0, -98.5],
      [32.0, -98.5]
    ]
  },
  {
    name: 'East Texas',
    color: '#008000',
    coordinates: [
      [33.5, -95.5],
      [33.5, -94.0],
      [32.5, -94.0],
      [31.5, -93.8],
      [30.5, -93.8],
      [30.2, -94.5],
      [30.5, -95.5],
      [31.0, -96.0],
      [31.5, -95.5],
      [32.5, -95.5],
      [33.5, -95.5]
    ]
  },
  {
    name: 'South Texas',
    color: '#FF0000',
    coordinates: [
      [29.5, -99.5],
      [29.5, -98.8],
      [29.2, -98.5],
      [28.8, -98.5],
      [28.5, -99.0],
      [27.5, -99.5],
      [27.2, -99.8],
      [28.0, -100.5],
      [29.0, -100.5],
      [29.5, -99.5]
    ]
  },
  {
    name: 'Gulf Coast',
    color: '#ADD8E6',
    coordinates: [
      [30.2, -94.5],
      [30.0, -94.0],
      [29.7, -94.5],
      [29.3, -94.8],
      [28.8, -95.5],
      [28.3, -96.5],
      [27.8, -97.2],
      [28.0, -97.5],
      [28.8, -97.0],
      [29.5, -96.5],
      [30.0, -95.5],
      [30.2, -94.5]
    ]
  },
  {
    name: 'Rio Grande Valley',
    color: '#FFA500',
    coordinates: [
      [27.2, -99.8],
      [26.5, -99.0],
      [26.2, -98.5],
      [26.0, -97.5],
      [25.8, -97.2],
      [26.0, -97.2],
      [26.5, -98.0],
      [27.0, -98.5],
      [27.2, -99.8]
    ]
  }
];

export const cityData: City[] = [
  // Texas Panhandle (Olive Green)
  { name: 'Dumas', latLng: [35.8656, -101.9732], region: 'Panhandle', regionColor: '#808000' },
  { name: 'Pampa', latLng: [35.5362, -100.9599], region: 'Panhandle', regionColor: '#808000' },
  { name: 'Amarillo', latLng: [35.221997, -101.831297], region: 'Panhandle', regionColor: '#808000' },
  { name: 'Borger', latLng: [35.6678, -101.3974], region: 'Panhandle', regionColor: '#808000' },
  { name: 'Hereford', latLng: [34.8151, -102.3977], region: 'Panhandle', regionColor: '#808000' },
  { name: 'Plainview', latLng: [34.1848, -101.7068], region: 'Panhandle', regionColor: '#808000' },
  { name: 'Lubbock', latLng: [33.5779, -101.8552], region: 'Panhandle', regionColor: '#808000' },
  { name: 'Brownfield', latLng: [33.1818, -102.2744], region: 'Panhandle', regionColor: '#808000' },

  // North Texas (Yellow)
  { name: 'Wichita Falls', latLng: [33.9137, -98.4934], region: 'North Texas', regionColor: '#FFFF00' },
  { name: 'Gainesville', latLng: [33.6259, -97.1334], region: 'North Texas', regionColor: '#FFFF00' },
  { name: 'Denton', latLng: [33.2148, -97.1331], region: 'North Texas', regionColor: '#FFFF00' },
  { name: 'Sherman', latLng: [33.6357, -96.6089], region: 'North Texas', regionColor: '#FFFF00' },
  { name: 'Paris', latLng: [33.6609, -95.5555], region: 'North Texas', regionColor: '#FFFF00' },
  { name: 'Fort Worth', latLng: [32.7555, -97.3308], region: 'North Texas', regionColor: '#FFFF00' },
  { name: 'Dallas', latLng: [32.7767, -96.7970], region: 'North Texas', regionColor: '#FFFF00' },

  // West Texas (Brown)
  { name: 'El Paso', latLng: [31.7619, -106.4850], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Pecos', latLng: [31.4158, -103.4939], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Fort Davis', latLng: [30.5882, -103.8946], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Andrews', latLng: [32.3187, -102.5457], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Odessa', latLng: [31.8457, -102.3676], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Midland', latLng: [31.9973, -102.0779], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Alpine', latLng: [30.3584, -103.6611], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Del Rio', latLng: [29.3627, -100.8968], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Lamesa', latLng: [32.7376, -101.9507], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Snyder', latLng: [32.7176, -100.9176], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'Sweetwater', latLng: [32.4705, -100.4059], region: 'West Texas', regionColor: '#A52A2A' },
  { name: 'San Angelo', latLng: [31.4638, -100.4370], region: 'West Texas', regionColor: '#A52A2A' },

  // Hill Country (Light Green)
  { name: 'Fredericksburg', latLng: [30.2752, -98.8720], region: 'Hill Country', regionColor: '#90EE90' },
  { name: 'Kerrville', latLng: [30.0474, -99.1403], region: 'Hill Country', regionColor: '#90EE90' },
  { name: 'Boerne', latLng: [29.7947, -98.7310], region: 'Hill Country', regionColor: '#90EE90' },
  { name: 'San Marcos', latLng: [29.8833, -97.9414], region: 'Hill Country', regionColor: '#90EE90' },
  { name: 'New Braunfels', latLng: [29.7030, -98.1245], region: 'Hill Country', regionColor: '#90EE90' },

  // Central Texas (Purple)
  { name: 'Stephenville', latLng: [32.2207, -98.2023], region: 'Central Texas', regionColor: '#800080' },
  { name: 'Waco', latLng: [31.5493, -97.1467], region: 'Central Texas', regionColor: '#800080' },
  { name: 'Temple', latLng: [31.0982, -97.3428], region: 'Central Texas', regionColor: '#800080' },
  { name: 'Killeen', latLng: [31.1171, -97.7278], region: 'Central Texas', regionColor: '#800080' },
  { name: 'Austin', latLng: [30.2672, -97.7431], region: 'Central Texas', regionColor: '#800080' },
  { name: 'College Station', latLng: [30.6279, -96.3344], region: 'Central Texas', regionColor: '#800080' },
  { name: 'Bryan', latLng: [30.6744, -96.3698], region: 'Central Texas', regionColor: '#800080' },
  { name: 'Georgetown', latLng: [30.6333, -97.6772], region: 'Central Texas', regionColor: '#800080' },
  { name: 'Round Rock', latLng: [30.5083, -97.6789], region: 'Central Texas', regionColor: '#800080' },

  // East Texas (Green)
  { name: 'Tyler', latLng: [32.3513, -95.3011], region: 'East Texas', regionColor: '#008000' },
  { name: 'Longview', latLng: [32.5007, -94.7405], region: 'East Texas', regionColor: '#008000' },
  { name: 'Marshall', latLng: [32.5449, -94.3674], region: 'East Texas', regionColor: '#008000' },
  { name: 'Nacogdoches', latLng: [31.6035, -94.6555], region: 'East Texas', regionColor: '#008000' },
  { name: 'Lufkin', latLng: [31.3382, -94.7291], region: 'East Texas', regionColor: '#008000' },
  { name: 'Palestine', latLng: [31.7621, -95.6308], region: 'East Texas', regionColor: '#008000' },
  { name: 'Texarkana', latLng: [33.4251, -94.0477], region: 'East Texas', regionColor: '#008000' },

  // South Texas (Red)
  { name: 'San Antonio', latLng: [29.4241, -98.4936], region: 'South Texas', regionColor: '#FF0000' },
  { name: 'Pleasanton', latLng: [28.9672, -98.4786], region: 'South Texas', regionColor: '#FF0000' },
  { name: 'Laredo', latLng: [27.5306, -99.4803], region: 'South Texas', regionColor: '#FF0000' },
  { name: 'Eagle Pass', latLng: [28.7091, -100.4999], region: 'South Texas', regionColor: '#FF0000' },
  { name: 'Uvalde', latLng: [29.2097, -99.7862], region: 'South Texas', regionColor: '#FF0000' },
  { name: 'Del Rio', latLng: [29.3627, -100.8968], region: 'South Texas', regionColor: '#FF0000' },

  // Texas Gulf Coast (Light Blue)
  { name: 'Corpus Christi', latLng: [27.8006, -97.3964], region: 'Gulf Coast', regionColor: '#ADD8E6' },
  { name: 'Victoria', latLng: [28.8053, -97.0036], region: 'Gulf Coast', regionColor: '#ADD8E6' },
  { name: 'Bay City', latLng: [28.9828, -95.9694], region: 'Gulf Coast', regionColor: '#ADD8E6' },
  { name: 'Galveston', latLng: [29.3013, -94.7977], region: 'Gulf Coast', regionColor: '#ADD8E6' },
  { name: 'Houston', latLng: [29.7604, -95.3698], region: 'Gulf Coast', regionColor: '#ADD8E6' },
  { name: 'Port Arthur', latLng: [29.8849, -93.9399], region: 'Gulf Coast', regionColor: '#ADD8E6' },
  { name: 'Beaumont', latLng: [30.0802, -94.1266], region: 'Gulf Coast', regionColor: '#ADD8E6' },

  // Rio Grande Valley (Orange)
  { name: 'McAllen', latLng: [26.2034, -98.2300], region: 'Rio Grande Valley', regionColor: '#FFA500' },
  { name: 'Harlingen', latLng: [26.1906, -97.6961], region: 'Rio Grande Valley', regionColor: '#FFA500' },
  { name: 'Brownsville', latLng: [25.9018, -97.4975], region: 'Rio Grande Valley', regionColor: '#FFA500' },
  { name: 'Mission', latLng: [26.2159, -98.3253], region: 'Rio Grande Valley', regionColor: '#FFA500' }
];
