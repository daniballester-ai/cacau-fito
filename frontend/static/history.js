/**
 * CacauFito Prediction History Page
 */

const CLASS_LABELS_PT = {
  healthy: "Sadia",
  cssvd: "CSSVD",
  anthracnose: "Antracnose",
};

const listEl = document.getElementById("history-list");
const emptyEl = document.getElementById("history-empty");
const loadMoreBtn = document.getElementById("load-more-btn");

const PAGE_SIZE = 20;
let nextOffset = 0;

document.addEventListener("DOMContentLoaded", () => {
  loadPage();
});

loadMoreBtn.addEventListener("click", () => loadPage());

async function loadPage() {
  loadMoreBtn.disabled = true;
  try {
    const response = await fetch(`/history?limit=${PAGE_SIZE}&offset=${nextOffset}`);
    const data = await response.json();

    if (nextOffset === 0 && data.items.length === 0) {
      emptyEl.hidden = false;
      loadMoreBtn.hidden = true;
      return;
    }

    emptyEl.hidden = true;
    data.items.forEach(renderItem);

    if (data.next_offset === null) {
      loadMoreBtn.hidden = true;
    } else {
      nextOffset = data.next_offset;
      loadMoreBtn.hidden = false;
    }
  } catch (err) {
    emptyEl.hidden = false;
    emptyEl.textContent = "Não foi possível carregar o histórico. Tente novamente mais tarde.";
  } finally {
    loadMoreBtn.disabled = false;
  }
}

function renderItem(item) {
  const labelPt = CLASS_LABELS_PT[item.label] || item.label;
  const confidencePct = (item.confidence * 100).toFixed(1);
  const date = new Date(item.created_at * 1000);
  const formattedDate = date.toLocaleString("pt-BR");

  const row = document.createElement("div");
  row.className = "history-item";
  row.innerHTML = `
    <span class="sample-badge badge-${item.label}">${labelPt}</span>
    <span class="history-confidence">${confidencePct}%</span>
    <span class="history-date">${formattedDate}</span>
  `;
  listEl.appendChild(row);
}
