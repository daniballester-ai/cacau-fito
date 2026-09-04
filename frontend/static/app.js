/**
 * CacauFito Frontend Application
 */

const CLASS_CONFIG = {
  healthy: {
    label: "Sadia",
    icon: "🌱",
    classKey: "healthy",
    description: "Folha saudável sem sinais de patógenos.",
  },
  cssvd: {
    label: "CSSVD (Vírus do Inchaço do Broto)",
    icon: "🍂",
    classKey: "cssvd",
    description: "Cacao Swollen Shoot Virus Disease.",
  },
  anthracnose: {
    label: "Antracnose",
    icon: "🍁",
    classKey: "anthracnose",
    description: "Infecção fúngica (Colletotrichum).",
  },
};

// Auto-determine backend base URL
const API_BASE_URL = (window.location.protocol === "file:" || (window.location.port !== "8000" && window.location.hostname !== "127.0.0.1"))
  ? "http://127.0.0.1:8000"
  : "";

// Elements
const form = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const submitBtn = document.getElementById("submit-btn");
const clearBtn = document.getElementById("clear-btn");
const btnSpinner = submitBtn.querySelector(".btn-spinner");
const btnText = submitBtn.querySelector(".btn-text");

const serviceStatusEl = document.getElementById("service-status");
const resultsCard = document.getElementById("results-card");
const previewWrapper = document.getElementById("preview-wrapper");
const preview = document.getElementById("preview");
const previewMeta = document.getElementById("preview-meta");

const resultEl = document.getElementById("result");
const diagnosisHeader = document.getElementById("diagnosis-header");
const diagnosisBadge = document.getElementById("diagnosis-badge");
const diagnosisTitle = document.getElementById("diagnosis-title");
const diagnosisConfidence = document.getElementById("diagnosis-confidence");
const uncertainBadge = document.getElementById("uncertain-badge");
const probList = document.getElementById("prob-list");

const errorEl = document.getElementById("error");
const errorMessage = document.getElementById("error-message");
const sampleButtons = document.querySelectorAll(".sample-btn");

let currentFile = null;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  setupDragAndDrop();
  setupSampleButtons();
});

// Check API Health
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (res.ok) {
      serviceStatusEl.className = "service-status online";
      serviceStatusEl.querySelector(".status-text").textContent = "API Conectada";
    } else {
      throw new Error();
    }
  } catch {
    serviceStatusEl.className = "service-status offline";
    serviceStatusEl.querySelector(".status-text").textContent = "API Desconectada (inicie na porta 8000)";
  }
}

// Drag and drop setup
function setupDragAndDrop() {
  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add("drag-over");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove("drag-over");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files[0]) {
      handleFileSelect(fileInput.files[0]);
    }
  });
}

function handleFileSelect(file) {
  currentFile = file;
  submitBtn.disabled = false;
  clearBtn.hidden = false;
  resultsCard.hidden = false;
  resultEl.hidden = true;
  errorEl.hidden = true;

  preview.src = URL.createObjectURL(file);
  const sizeKb = (file.size / 1024).toFixed(1);
  previewMeta.textContent = `${file.name} (${sizeKb} KB)`;
}

// Quick Sample Buttons
function setupSampleButtons() {
  sampleButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const sampleFile = btn.dataset.sample;
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE_URL}/samples/${sampleFile}`);
        if (!res.ok) throw new Error("Não foi possível carregar o arquivo de exemplo.");
        const blob = await res.blob();
        const file = new File([blob], sampleFile, { type: blob.type || "image/jpeg" });
        handleFileSelect(file);
        await performPrediction(file);
      } catch (err) {
        showError(err.message || "Erro ao carregar imagem de exemplo.");
      } finally {
        setLoading(false);
      }
    });
  });
}

// Clear button
clearBtn.addEventListener("click", resetForm);

function resetForm() {
  currentFile = null;
  fileInput.value = "";
  submitBtn.disabled = true;
  clearBtn.hidden = true;
  resultsCard.hidden = true;
  resultEl.hidden = true;
  errorEl.hidden = true;
  preview.src = "";
  previewMeta.textContent = "";
}

// Submit Form
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentFile) {
    showError("Por favor, selecione ou arraste uma imagem antes de analisar.");
    return;
  }
  await performPrediction(currentFile);
});

async function performPrediction(file) {
  setLoading(true);
  resultEl.hidden = true;
  errorEl.hidden = true;

  const formData = new FormData();
  formData.append("file", file, file.name);

  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Não foi possível analisar a imagem.");
    }

    showResult(data);
  } catch (err) {
    showError(err.message || "Falha de conexão com a API de inferência.");
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  btnSpinner.hidden = !isLoading;
  btnText.textContent = isLoading ? "Analisando folha..." : "Analisar Folha";
}

function showResult(data) {
  const config = CLASS_CONFIG[data.label] || {
    label: data.label,
    icon: "🔍",
    classKey: "healthy",
  };

  const confidencePct = (data.confidence * 100).toFixed(1);

  // Update Diagnosis Header
  diagnosisHeader.className = `diagnosis-header ${config.classKey}`;
  diagnosisBadge.textContent = config.icon;
  diagnosisTitle.textContent = config.label;
  diagnosisConfidence.textContent = `Nível de Confiança: ${confidencePct}%`;
  uncertainBadge.hidden = !data.is_uncertain;

  // Populate Probabilities Breakdown
  probList.innerHTML = "";
  if (data.probabilities) {
    // Sort probabilities descending
    const entries = Object.entries(data.probabilities).sort((a, b) => b[1] - a[1]);

    entries.forEach(([clsKey, prob]) => {
      const clsConfig = CLASS_CONFIG[clsKey] || { label: clsKey, classKey: clsKey };
      const pct = (prob * 100).toFixed(1);

      const item = document.createElement("div");
      item.className = "prob-item";
      item.innerHTML = `
        <div class="prob-meta">
          <span>${clsConfig.label}</span>
          <span>${pct}%</span>
        </div>
        <div class="prob-bar-container">
          <div class="prob-bar-fill ${clsConfig.classKey}" style="width: 0%"></div>
        </div>
      `;
      probList.appendChild(item);

      // Trigger animation smoothly
      setTimeout(() => {
        const fill = item.querySelector(".prob-bar-fill");
        if (fill) fill.style.width = `${pct}%`;
      }, 50);
    });
  }

  resultsCard.hidden = false;
  resultEl.hidden = false;
}

function showError(message) {
  errorMessage.textContent = message;
  resultsCard.hidden = false;
  errorEl.hidden = false;
}
