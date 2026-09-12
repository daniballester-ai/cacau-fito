/**
 * CacauFito Statistics Dashboard
 */

const CLASS_LABELS_PT = {
  healthy: "Sadia",
  cssvd: "CSSVD",
  anthracnose: "Antracnose",
};

const CLASS_COLORS = {
  healthy: "#4CAF7D",
  cssvd: "#E5533D",
  anthracnose: "#E5A83D",
};

const totalsListEl = document.getElementById("totals-list");
const totalsEmptyEl = document.getElementById("totals-empty");
const chartEmptyEl = document.getElementById("chart-empty");
const canvasEl = document.getElementById("timeseries-chart");

document.addEventListener("DOMContentLoaded", () => {
  loadTotals();
  loadTimeseries();
});

async function loadTotals() {
  try {
    const response = await fetch("/stats");
    const data = await response.json();

    if (!data.total) {
      totalsEmptyEl.hidden = false;
      totalsListEl.innerHTML = "";
      return;
    }

    totalsEmptyEl.hidden = true;
    totalsListEl.innerHTML = "";
    Object.entries(data.by_class).forEach(([label, count]) => {
      const labelPt = CLASS_LABELS_PT[label] || label;
      const row = document.createElement("div");
      row.className = "history-item";
      row.innerHTML = `
        <span class="sample-badge badge-${label}">${labelPt}</span>
        <span class="history-confidence">${count}</span>
      `;
      totalsListEl.appendChild(row);
    });
  } catch (err) {
    totalsEmptyEl.hidden = false;
    totalsEmptyEl.textContent = "Não foi possível carregar as estatísticas.";
  }
}

async function loadTimeseries() {
  try {
    const response = await fetch("/stats/timeseries");
    const data = await response.json();

    if (!data.days || data.days.length === 0) {
      chartEmptyEl.hidden = false;
      canvasEl.hidden = true;
      return;
    }

    chartEmptyEl.hidden = true;
    canvasEl.hidden = false;
    renderChart(fillGaps(data.days));
  } catch (err) {
    chartEmptyEl.hidden = false;
    chartEmptyEl.textContent = "Não foi possível carregar o gráfico de evolução.";
    canvasEl.hidden = true;
  }
}

function fillGaps(days) {
  const byDate = Object.fromEntries(days.map((d) => [d.date, d.by_class]));
  const start = new Date(days[0].date);
  const end = new Date(days[days.length - 1].date);
  const filled = [];

  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const iso = d.toISOString().slice(0, 10);
    filled.push({ date: iso, by_class: byDate[iso] || {} });
  }
  return filled;
}

function renderChart(days) {
  const labels = days.map((d) => d.date);
  const classes = Object.keys(CLASS_LABELS_PT);

  const datasets = classes.map((cls) => ({
    label: CLASS_LABELS_PT[cls],
    data: days.map((d) => d.by_class[cls] || 0),
    borderColor: CLASS_COLORS[cls],
    backgroundColor: CLASS_COLORS[cls],
    tension: 0.3,
  }));

  new Chart(canvasEl, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 } },
      },
    },
  });
}
