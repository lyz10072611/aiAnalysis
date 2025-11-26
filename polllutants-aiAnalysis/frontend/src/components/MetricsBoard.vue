<template>
  <div class="metrics-grid">
    <div class="metric card" v-for="item in metricList" :key="item.label">
      <p class="metric-label">{{ item.label }}</p>
      <p class="metric-value" :style="{ color: item.color }">{{ item.value }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { ChartDataPoint } from '../types';

const props = defineProps<{
  data: ChartDataPoint[];
}>();

const metricList = computed(() => {
  const stationVals = props.data
    .map((item) => item.stationValue)
    .filter((val): val is number => val !== null);
  const tifVals = props.data
    .map((item) => item.tifValue)
    .filter((val): val is number => val !== null);

  const avg = (arr: number[]) => (arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0);
  const max = (arr: number[]) => (arr.length ? Math.max(...arr) : 0);

  const avgStation = avg(stationVals);
  const avgTif = avg(tifVals);
  let correlation = 0;

  const pairs = props.data.filter((item) => item.stationValue !== null && item.tifValue !== null);
  const n = pairs.length;
  if (n > 0) {
    const x = pairs.map((p) => p.stationValue!) as number[];
    const y = pairs.map((p) => p.tifValue!) as number[];
    const sumX = x.reduce((acc, value) => acc + value, 0);
    const sumY = y.reduce((acc, value) => acc + value, 0);
    const sumXY = x.reduce((acc, value, idx) => acc + value * y[idx], 0);
    const sumX2 = x.reduce((acc, value) => acc + value * value, 0);
    const sumY2 = y.reduce((acc, value) => acc + value * value, 0);
    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX ** 2) * (n * sumY2 - sumY ** 2));
    if (denominator !== 0) correlation = numerator / denominator;
  }

  return [
    { label: '地面监测平均值 (µg/m³)', value: avgStation.toFixed(2), color: '#0f172a' },
    { label: '地面监测最大值 (µg/m³)', value: max(stationVals).toFixed(2), color: '#0f172a' },
    { label: 'TIF 模型平均值 (µg/m³)', value: avgTif.toFixed(2), color: '#0f172a' },
    { label: '地面 vs TIF 相关系数 R', value: correlation.toFixed(3), color: correlation > 0.8 ? '#10b981' : '#f59e0b' }
  ];
});
</script>

<style scoped>
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric {
  padding: 18px;
}

.metric-label {
  font-size: 12px;
  color: #94a3b8;
  text-transform: uppercase;
  margin: 0;
}

.metric-value {
  margin: 8px 0 0;
  font-size: 28px;
  font-weight: 700;
}
</style>


