<template>
  <div class="card table-card">
    <div class="table-header">
      <div>
        <h3>原始时序数据</h3>
        <p>展示地面监测与 TIF 模型的逐小时数值对比</p>
      </div>
      <span class="badge">最新</span>
    </div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>时间</th>
            <th>站点值 (µg/m³)</th>
            <th>TIF 值 (µg/m³)</th>
            <th>差值</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!rows.length">
            <td colspan="4" class="empty">暂无数据</td>
          </tr>
          <tr v-for="item in rows" :key="item.timestamp">
            <td>{{ item.timestamp }}</td>
            <td>{{ formatValue(item.stationValue) }}</td>
            <td>{{ formatValue(item.tifValue) }}</td>
            <td>
              {{
                item.stationValue !== null && item.tifValue !== null
                  ? Math.abs(item.stationValue - item.tifValue).toFixed(2)
                  : '-'
              }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChartDataPoint } from '../types';

defineProps<{
  rows: ChartDataPoint[];
}>();

const formatValue = (value: number | null) => (value === null ? '-' : value.toFixed(2));
</script>

<style scoped>
.table-card {
  padding: 24px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header h3 {
  margin: 0;
  font-size: 18px;
}

.table-header p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 13px;
}

.badge {
  background: #e0f2fe;
  color: #0369a1;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.table-scroll {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th,
td {
  padding: 12px 10px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

th {
  color: #64748b;
  font-weight: 600;
  background: #f8fafc;
}

tbody tr:hover {
  background: #f1f5f9;
}

.empty {
  text-align: center;
  color: #94a3b8;
}
</style>

