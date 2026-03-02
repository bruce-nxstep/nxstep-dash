/**
 * main.js — NXSTEP ATS CV Generator UI Logic
 */

// ── DOM refs ──────────────────────────────────────────────
const form = document.getElementById('cv-form');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('cv-file');
const dropContent = document.getElementById('drop-content');
const fileSelected = document.getElementById('file-selected');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const fileRemove = document.getElementById('file-remove');
const submitBtn = document.getElementById('submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoading = submitBtn.querySelector('.btn-loading');
const errorBanner = document.getElementById('error-banner');
const errorText = document.getElementById('error-text');
const progressOverlay = document.getElementById('progress-overlay');
const progressStep = document.getElementById('progress-step');
const progressEmoji = document.getElementById('progress-emoji');
const ringFill = document.getElementById('ring-fill');
const toggleKey = document.getElementById('toggle-key');
const apiKeyInput = document.getElementById('api_key');

// Steps
const step1 = document.getElementById('step-1');
const step2 = document.getElementById('step-2');
const step3 = document.getElementById('step-3');

// ── API key toggle ─────────────────────────────────────────
toggleKey.addEventListener('click', () => {
    apiKeyInput.type = apiKeyInput.type === 'password' ? 'text' : 'password';
});

// ── File drag & drop ───────────────────────────────────────
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
});

fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFileSelect(fileInput.files[0]);
});

fileRemove.addEventListener('click', (e) => {
    e.stopPropagation();
    clearFile();
});

function handleFileSelect(file) {
    const allowed = ['application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const ext = file.name.split('.').pop().toLowerCase();

    if (!['pdf', 'docx'].includes(ext)) {
        showError('Format non supporté. Veuillez utiliser un fichier PDF ou DOCX.');
        return;
    }

    // Show file info
    dropContent.style.display = 'none';
    fileSelected.style.display = 'flex';
    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);
    dropZone.classList.add('has-file');
    hideError();
}

function clearFile() {
    fileInput.value = '';
    dropContent.style.display = 'block';
    fileSelected.style.display = 'none';
    dropZone.classList.remove('has-file');
}

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ── Progress animation ─────────────────────────────────────
const PROGRESS_STEPS = [
    { pct: 15, emoji: '🔍', text: 'Extraction du texte du CV…' },
    { pct: 40, emoji: '🤖', text: 'Analyse par GPT-4o…' },
    { pct: 65, emoji: '✍️', text: 'Restructuration ATS…' },
    { pct: 85, emoji: '📦', text: 'Génération PDF + DOCX…' },
    { pct: 95, emoji: '⚡', text: 'Compression ZIP…' },
];

const CIRCUMFERENCE = 2 * Math.PI * 34; // r=34

function setProgress(pct) {
    const offset = CIRCUMFERENCE * (1 - pct / 100);
    ringFill.style.strokeDashoffset = offset;
}

let progressTimer = null;

function startProgress() {
    let stepIdx = 0;
    setProgress(0);
    progressOverlay.style.display = 'flex';

    function advance() {
        if (stepIdx >= PROGRESS_STEPS.length) return;
        const s = PROGRESS_STEPS[stepIdx];
        setProgress(s.pct);
        progressEmoji.textContent = s.emoji;
        progressStep.textContent = s.text;
        stepIdx++;
        // slower at beginning, faster in middle
        const delay = stepIdx <= 2 ? 3200 : 2000;
        progressTimer = setTimeout(advance, delay);
    }
    advance();
}

function stopProgress() {
    clearTimeout(progressTimer);
    setProgress(100);
    progressEmoji.textContent = '✅';
    progressStep.textContent = 'CV généré avec succès !';
    setTimeout(() => {
        progressOverlay.style.display = 'none';
    }, 1200);
}

// ── Steps indicator ────────────────────────────────────────
function setStepActive(n) {
    [step1, step2, step3].forEach((s, i) => {
        s.classList.remove('active', 'done');
        if (i < n - 1) s.classList.add('done');
        else if (i === n - 1) s.classList.add('active');
    });
}

// ── Error helpers ─────────────────────────────────────────
function showError(msg) {
    errorText.textContent = msg;
    errorBanner.style.display = 'flex';
}
function hideError() {
    errorBanner.style.display = 'none';
}

// ── Form submit ───────────────────────────────────────────
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    if (!fileInput.files[0]) {
        showError('Veuillez sélectionner un fichier CV (PDF ou DOCX).');
        return;
    }

    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
        showError('Veuillez entrer votre clé API OpenAI (sk-...)');
        return;
    }

    // UI: loading state
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'flex';
    setStepActive(2);
    startProgress();

    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('api_key', apiKey);

        const response = await fetch('/generate', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || `Erreur serveur (${response.status})`);
        }

        // Check content type — expect ZIP
        const ct = response.headers.get('Content-Type');
        if (!ct || !ct.includes('application/zip')) {
            let err = { error: 'Réponse inattendue du serveur.' };
            try { err = await response.json(); } catch (_) { }
            throw new Error(err.error);
        }

        // Download the ZIP
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');

        // Try to get filename from Content-Disposition
        const cd = response.headers.get('Content-Disposition');
        let dlName = 'CV_ATS_NXSTEP.zip';
        if (cd && cd.includes('filename=')) {
            dlName = cd.split('filename=')[1].replace(/"/g, '').trim();
        }

        a.href = url;
        a.download = dlName;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);

        stopProgress();
        setStepActive(3);

    } catch (err) {
        clearTimeout(progressTimer);
        progressOverlay.style.display = 'none';
        showError(err.message);
        setStepActive(1);
    } finally {
        submitBtn.disabled = false;
        btnText.style.display = 'flex';
        btnLoading.style.display = 'none';
    }
});
