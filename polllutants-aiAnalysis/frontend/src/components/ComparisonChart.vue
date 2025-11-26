<template>
  <div class="card chart-card">
    <h3>{{ pollutantName }} 浓度对比</h3>
    <div class="chart-body">
      <div v-if="loading" class="placeholder">正在加载分析结果...</div>
      <div v-else-if="!data.length" class="placeholder">暂无数据，请调整过滤条件。</div>
      <Line v-else :data="chartData" :options="chartOptions" />
    </div>
    <div class="legend">
      <span><span class="dot station"></span>地面监测站</span>
      <span><span class="dot tif"></span>TIF 模型/反演</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import type { ChartDataPoint } from '../types';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);

const props = defineProps<{
  data: ChartDataPoint[];
  loading: boolean;
  pollutantName: string;
}>();

const chartData = computed(() => ({
  labels: props.data.map((item) => item.timestamp),
  datasets: [
    {
      label: '地面监测站',
      data: props.data.map((item) => item.stationValue),
      fill: false,
      borderColor: '#0ea5e9',
      tension: 0.3,
      pointRadius: 0,
      borderWidth: 2
    },
    {
      label: 'TIF 模型',
      data: props.data.map((item) => item.tifValue),
      borderDash: [6, 6],
      fill: false,
      borderColor: '#8b5cf6',
      tension: 0.3,
      pointRadius: 0,
      borderWidth: 2
    }
  ]
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false
  },
  plugins: {
    legend: {
      position: 'top'
    }
  },
  scales: {
    y: {
      title: {
        display: true,
        text: 'µg/m³'
      },
      ticks: {
        color: '#475569'
      }
    },
    x: {
      ticks: {
        maxRotation: 30,
        minRotation: 30,
        color: '#475569'
      }
    }
  }
};
</script>

<style scoped>
.chart-card {
  padding: 24px;
}

h3 {
  margin: 0;
  font-size: 20px;
}

.chart-body {
  height: 340px;
  margin-top: 16px;
}

.placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 14px;
}

.legend {
  margin-top: 12px;
  display: flex;
  gap: 18px;
  color: #475569;
  font-size: 14px;
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
}

.station {
  background: #0ea5e9;
}

.tif {
  background: #8b5cf6;
}
</style>

