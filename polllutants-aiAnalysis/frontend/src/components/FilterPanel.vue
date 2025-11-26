<template>
  <div class="card filter-panel">
    <div class="field">
      <label>监测站点</label>
      <select :value="selectedSite ?? ''" @change="onSiteChangeHandler">
        <option value="" disabled>请选择监测站点</option>
        <option v-for="site in sites" :key="site.site_id" :value="site.site_id">
          {{ site.site_name }}（ID: {{ site.site_id }}）
        </option>
      </select>
    </div>
    <div class="field">
      <label>污染物类型</label>
      <select :value="selectedPollutant ?? ''" @change="onPollutantChangeHandler">
        <option value="" disabled>请选择污染物</option>
        <option v-for="pollutant in pollutants" :key="pollutant.pollutant_id" :value="pollutant.pollutant_id">
          {{ pollutant.pollutant_name }}
        </option>
      </select>
    </div>
    <div class="field">
      <label>开始日期</label>
      <input type="date" :value="dateRange.startDate" @change="updateDate('start', $event)" />
    </div>
    <div class="field">
      <label>结束日期</label>
      <input type="date" :value="dateRange.endDate" @change="updateDate('end', $event)" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Pollutant, Site, DateRange } from '../types';

const props = defineProps<{
  sites: Site[];
  pollutants: Pollutant[];
  selectedSite: number | null;
  selectedPollutant: number | null;
  dateRange: DateRange;
}>();

const emits = defineEmits<{
  (e: 'update:site', value: number): void;
  (e: 'update:pollutant', value: number): void;
  (e: 'update:dateRange', value: DateRange): void;
}>();

const onSiteChangeHandler = (event: Event) => {
  const value = Number((event.target as HTMLSelectElement).value);
  emits('update:site', value);
};

const onPollutantChangeHandler = (event: Event) => {
  const value = Number((event.target as HTMLSelectElement).value);
  emits('update:pollutant', value);
};

const updateDate = (type: 'start' | 'end', event: Event) => {
  const value = (event.target as HTMLInputElement).value;
  if (!value) return;
  emits('update:dateRange', {
    ...props.dateRange,
    startDate: type === 'start' ? value : props.dateRange.startDate,
    endDate: type === 'end' ? value : props.dateRange.endDate
  });
};
</script>

<style scoped>
.filter-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  padding: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 12px;
  color: #64748b;
  letter-spacing: 0.1em;
}

select,
input[type='date'] {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  background: #f8fafc;
  color: #0f172a;
}
</style>

