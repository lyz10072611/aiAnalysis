import axios from 'axios';
import type { Site, Pollutant, ChartDataPoint, DateRange } from '../types';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api',
  timeout: 10000
});

export const fetchSites = async (): Promise<Site[]> => {
  const { data } = await apiClient.get<Site[]>('/sites');
  return data;
};

export const fetchPollutants = async (): Promise<Pollutant[]> => {
  const { data } = await apiClient.get<Pollutant[]>('/pollutants');
  return data;
};

export const fetchAnalysis = async (
  siteId: number,
  pollutantId: number,
  range: DateRange
): Promise<ChartDataPoint[]> => {
  const { data } = await apiClient.get<ChartDataPoint[]>('/analysis', {
    params: {
      site_id: siteId,
      pollutant_id: pollutantId,
      start_date: range.startDate,
      end_date: range.endDate
    }
  });
  return data;
};

