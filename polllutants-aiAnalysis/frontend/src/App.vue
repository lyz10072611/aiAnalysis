<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <span class="dot"></span>
        <div>
          <p class="brand-title">城市污染物洞察</p>
          <p class="brand-subtitle">FastAPI + Vue</p>
        </div>
      </div>
      <nav>
        <p class="nav-title">主菜单</p>
        <button class="nav-item active">数据驾驶舱</button>
        <button class="nav-item" disabled>地图视图（开发中）</button>
        <button class="nav-item" disabled>系统配置</button>
      </nav>
      <div class="status-card">
        <p>数据库连接</p>
        <strong>{{ dbStatus }}</strong>
        <small>PostgreSQL · measurements / measurements_tif</small>
      </div>
    </aside>

    <main class="content">
      <header class="page-header">
        <div>
          <h1>污染物监测分析平台</h1>
          <p>支持站点数据与 TIF 模型的对比分析，快速掌握污染物变化趋势</p>
        </div>
        <div class="meta">
          <span class="badge">Beta</span>
          <span>后端：FastAPI</span>
          <span>前端：Vue 3 + Vite</span>
        </div>
      </header>

      <section v-if="errorMessage" class="error-card card">
        <strong>数据加载失败：</strong>{{ errorMessage }}
      </section>

      <FilterPanel
        class="section"
        :sites="sites"
        :pollutants="pollutants"
        :selected-site="selectedSite"
        :selected-pollutant="selectedPollutant"
        :date-range="dateRange"
        @update:site="handleSiteChange"
        @update:pollutant="handlePollutantChange"
        @update:date-range="handleDateRangeChange"
      />

      <MetricsBoard class="section" :data="chartData" />

      <ComparisonChart
        class="section"
        :data="chartData"
        :loading="loadingChart"
        :pollutant-name="currentPollutantName"
      />

      <DataTable class="section" :rows="chartData" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue';
import FilterPanel from './components/FilterPanel.vue';
import MetricsBoard from './components/MetricsBoard.vue';
import ComparisonChart from './components/ComparisonChart.vue';
import DataTable from './components/DataTable.vue';
import type { Site, Pollutant, ChartDataPoint, DateRange } from './types';
import { fetchSites, fetchPollutants, fetchAnalysis } from './services/api';

const sites = ref<Site[]>([]);
const pollutants = ref<Pollutant[]>([]);
const chartData = ref<ChartDataPoint[]>([]);
const selectedSite = ref<number | null>(null);
const selectedPollutant = ref<number | null>(null);
const loadingChart = ref(false);
const errorMessage = ref<string | null>(null);

const dbStatus = computed(() => (errorMessage.value ? '断开' : '已连接'));

const defaultStart = new Date(Date.now() - 6 * 24 * 60 * 60 * 1000);
const defaultEnd = new Date();

const formatDate = (date: Date) => date.toISOString().split('T')[0];

const dateRange = ref<DateRange>({
  startDate: formatDate(defaultStart),
  endDate: formatDate(defaultEnd)
});

const currentPollutantName = computed(() => {
  const target = pollutants.value.find((item) => item.pollutant_id === selectedPollutant.value);
  return target ? target.pollutant_name : '污染物';
});

const handleSiteChange = (value: number) => {
  selectedSite.value = value;
};

const handlePollutantChange = (value: number) => {
  selectedPollutant.value = value;
};

const handleDateRangeChange = (value: DateRange) => {
  dateRange.value = value;
};

const loadMetaData = async () => {
  errorMessage.value = null;
  try {
    const [siteRes, pollutantRes] = await Promise.all([fetchSites(), fetchPollutants()]);
    sites.value = siteRes;
    pollutants.value = pollutantRes;
    if (!selectedSite.value && siteRes.length) selectedSite.value = siteRes[0].site_id;
    if (!selectedPollutant.value && pollutantRes.length) selectedPollutant.value = pollutantRes[0].pollutant_id;
  } catch (error) {
    errorMessage.value = '无法连接到后端 API，请确认 FastAPI 服务已启动。';
  }
};

const loadChartData = async () => {
  if (!selectedSite.value || !selectedPollutant.value) return;
  loadingChart.value = true;
  errorMessage.value = null;
  try {
    chartData.value = await fetchAnalysis(selectedSite.value, selectedPollutant.value, dateRange.value);
  } catch (error) {
    chartData.value = [];
    errorMessage.value = '查询分析数据失败，请检查数据库或日期范围。';
  } finally {
    loadingChart.value = false;
  }
};

onMounted(async () => {
  await loadMetaData();
  await loadChartData();
});

watch([selectedSite, selectedPollutant, dateRange], () => {
  loadChartData();
});
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  background: #f8fafc;
}

.sidebar {
  background: #0f172a;
  color: #fff;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
}

.dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #10b981;
  display: inline-block;
}

.brand-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.brand-subtitle {
  margin: 0;
  font-size: 13px;
  color: #94a3b8;
}

.nav-title {
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.2em;
  color: #94a3b8;
}

.nav-item {
  width: 100%;
  padding: 12px 14px;
  margin-top: 12px;
  border-radius: 10px;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  text-align: left;
  font-size: 14px;
}

.nav-item.active {
  background: linear-gradient(120deg, #2563eb, #38bdf8);
}

.status-card {
  margin-top: auto;
  padding: 16px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.status-card strong {
  display: block;
  font-size: 20px;
  margin: 4px 0;
}

.content {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
}

.page-header p {
  margin: 8px 0 0;
  color: #475569;
}

.meta {
  display: flex;
  gap: 12px;
  align-items: center;
  color: #64748b;
}

.badge {
  background: #dbeafe;
  color: #1d4ed8;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 13px;
}

.section {
  width: 100%;
}

.error-card {
  padding: 16px;
  border-left: 4px solid #f97316;
  color: #c2410c;
  background: #fff7ed;
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 16px;
  }
}
</style>

