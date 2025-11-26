export interface Site {
  site_id: number;
  site_name: string;
  longitude: number;
  latitude: number;
}

export interface Pollutant {
  pollutant_id: number;
  pollutant_name: string;
}

export interface ChartDataPoint {
  date: string;
  hour: number;
  timestamp: string;
  stationValue: number | null;
  tifValue: number | null;
}

export interface DateRange {
  startDate: string;
  endDate: string;
}


