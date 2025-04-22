import * as L from 'leaflet';

export interface CountyRegion {
  name: string;
  color: string;
  counties: string[];
}

export const regionDefinitions: CountyRegion[] = [
  {
    name: 'Panhandle',
    color: '#808000',
    counties: [
      'Dallam', 'Sherman', 'Hansford', 'Ochiltree', 'Lipscomb',
      'Hartley', 'Moore', 'Hutchinson', 'Roberts', 'Hemphill',
      'Oldham', 'Potter', 'Carson', 'Gray', 'Wheeler',
      'Deaf Smith', 'Randall', 'Armstrong', 'Donley', 'Collingsworth',
      'Parmer', 'Castro', 'Swisher', 'Briscoe', 'Hall',
      'Bailey', 'Lamb', 'Hale', 'Floyd', 'Motley',
      'Cochran', 'Hockley', 'Lubbock', 'Crosby', 'Dickens'
    ]
  },
  {
    name: 'West Texas',
    color: '#A52A2A',
    counties: [
      'El Paso', 'Hudspeth', 'Culberson', 'Jeff Davis', 'Presidio',
      'Brewster', 'Loving', 'Winkler', 'Ward', 'Reeves',
      'Pecos', 'Terrell', 'Andrews', 'Martin', 'Howard',
      'Glasscock', 'Reagan', 'Upton', 'Crane', 'Ector',
      'Midland', 'Sterling', 'Coke', 'Mitchell', 'Nolan',
      'Taylor', 'Callahan', 'Shackelford', 'Jones', 'Fisher',
      'Scurry', 'Borden', 'Dawson', 'Gaines', 'Yoakum',
      'Terry', 'Lynn', 'Garza', 'Kent', 'Stonewall'
    ]
  },
  {
    name: 'North Texas',
    color: '#FFFF00',
    counties: [
      'Wichita', 'Clay', 'Montague', 'Cooke', 'Grayson',
      'Fannin', 'Lamar', 'Red River', 'Bowie', 'Delta',
      'Hopkins', 'Franklin', 'Titus', 'Camp', 'Morris',
      'Cass', 'Young', 'Jack', 'Wise', 'Denton',
      'Collin', 'Hunt', 'Rockwall', 'Kaufman', 'Dallas',
      'Tarrant', 'Parker', 'Palo Pinto', 'Stephens', 'Throckmorton',
      'Archer', 'Baylor', 'Knox', 'Haskell'
    ]
  },
  {
    name: 'East Texas',
    color: '#008000',
    counties: [
      'Marion', 'Harrison', 'Upshur', 'Wood', 'Rains',
      'Van Zandt', 'Smith', 'Gregg', 'Rusk', 'Panola',
      'Shelby', 'Nacogdoches', 'San Augustine', 'Sabine',
      'Cherokee', 'Anderson', 'Henderson', 'Houston', 'Angelina',
      'Trinity', 'Polk', 'Tyler', 'Jasper', 'Newton',
      'San Jacinto', 'Hardin', 'Orange', 'Jefferson'
    ]
  },
  {
    name: 'Central Texas',
    color: '#800080',
    counties: [
      'Brown', 'Coleman', 'McCulloch', 'San Saba', 'Mills',
      'Hamilton', 'Bosque', 'Hill', 'Johnson', 'Ellis',
      'Navarro', 'Freestone', 'Limestone', 'McLennan', 'Falls',
      'Robertson', 'Leon', 'Madison', 'Brazos', 'Burleson',
      'Lee', 'Bastrop', 'Travis', 'Williamson', 'Bell',
      'Milam', 'Coryell', 'Lampasas', 'Burnet', 'Llano',
      'Mason', 'Gillespie', 'Blanco', 'Hays'
    ]
  },
  {
    name: 'Hill Country',
    color: '#90EE90',
    counties: [
      'Kerr', 'Kendall', 'Comal', 'Real', 'Bandera',
      'Medina', 'Uvalde', 'Kimble', 'Edwards', 'Val Verde',
      'Kinney', 'Menard', 'Schleicher', 'Sutton', 'Concho'
    ]
  },
  {
    name: 'South Texas',
    color: '#FF0000',
    counties: [
      'Maverick', 'Zavala', 'Frio', 'Atascosa', 'Karnes',
      'Dimmit', 'La Salle', 'McMullen', 'Live Oak', 'Bee',
      'Webb', 'Duval', 'Jim Wells', 'San Patricio', 'Nueces',
      'Kleberg', 'Jim Hogg', 'Brooks', 'Kenedy'
    ]
  },
  {
    name: 'Gulf Coast',
    color: '#ADD8E6',
    counties: [
      'Aransas', 'Refugio', 'Calhoun', 'Victoria', 'Jackson',
      'Matagorda', 'Brazoria', 'Galveston', 'Chambers',
      'Liberty', 'Montgomery', 'Walker', 'Grimes', 'Washington',
      'Austin', 'Waller', 'Harris', 'Fort Bend', 'Wharton',
      'Colorado', 'Lavaca', 'DeWitt', 'Goliad'
    ]
  },
  {
    name: 'Rio Grande Valley',
    color: '#FFA500',
    counties: [
      'Starr', 'Hidalgo', 'Willacy', 'Cameron'
    ]
  }
]; 