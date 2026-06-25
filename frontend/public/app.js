const BACKEND_URL = 'http://localhost:8000';

const form = document.getElementById('triage-form');
const submitBtn = document.getElementById('submit-btn');
const btnText = document.getElementById('btn-text');
const btnSpinner = document.getElementById('btn-spinner');
const symptomsContent = document.getElementById('symptoms-content');
const reportContent = document.getElementById('report-content');
const pipelineStatus = document.getElementById('pipeline-status');
const psStep1 = document.getElementById('ps-step1');
const psStep2 = document.getElementById('ps-step2');
const psStep3 = document.getElementById('ps-step3');

let eventSource = null;
let agent1Buffer = '';
let reportBuffer = '';
let pipelinePhase = 0; // 0=idle, 1=agent1, 2=retriever, 3=agent3

form.addEventListener('submit', (e) => {
    e.preventDefault();

    const patientInput = document.getElementById('patient-input').value.trim();
    if (!patientInput) return;

    resetUI();
    setLoading(true);

    if (eventSource) eventSource.close();

    const url = `${BACKEND_URL}/api/triage/stream?patient_input=${encodeURIComponent(patientInput)}`;
    eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
        const payload = JSON.parse(event.data);

        if (payload.type === 'done') {
            // Final attempt to parse Agent 1 buffer if not yet rendered
            if (agent1Buffer && symptomsContent.classList.contains('placeholder')) {
                tryRenderSymptoms(agent1Buffer);
            }
            finishLoading();
            eventSource.close();
            return;
        }

        const { node, text } = payload;

        if (node === 'Agent_1_extract_symptoms') {
            agent1Buffer += text;
            tryRenderSymptoms(agent1Buffer);
        } else if (node === 'Agent_3_synthesize_diagnose') {
            if (pipelinePhase < 3) setPipelineStep(3);
            reportBuffer += text;
            reportContent.classList.remove('placeholder');
            reportContent.innerHTML = marked.parse(reportBuffer);
        }
    };

    eventSource.onerror = () => {
        finishLoading();
        reportContent.classList.remove('placeholder');
        reportContent.textContent = 'Connection error. Make sure the backend is running on port 8000.';
        eventSource.close();
    };
});

function tryRenderSymptoms(buffer) {
    try {
        const parsed = JSON.parse(buffer);
        if (parsed.symptoms && parsed.symptoms.length > 0) {
            symptomsContent.classList.remove('placeholder');
            symptomsContent.innerHTML = parsed.symptoms
                .map(s => `<div class="symptom-tag">${s}</div>`)
                .join('');
            if (pipelinePhase < 2) setPipelineStep(2);
        }
    } catch {
        // Buffer not yet complete JSON — keep accumulating
    }
}

function setPipelineStep(step) {
    pipelinePhase = step;
    [psStep1, psStep2, psStep3].forEach((el, i) => {
        el.classList.toggle('ps-active', i + 1 === step);
    });
}

function resetUI() {
    agent1Buffer = '';
    reportBuffer = '';
    pipelinePhase = 0;
    symptomsContent.innerHTML = 'Awaiting analysis...';
    symptomsContent.classList.add('placeholder');
    reportContent.innerHTML = 'Awaiting analysis...';
    reportContent.classList.add('placeholder');
}

function setLoading(active) {
    submitBtn.disabled = active;
    btnText.textContent = active ? 'Analyzing...' : 'Run Triage Analysis';
    btnSpinner.classList.toggle('hidden', !active);
    if (active) {
        pipelineStatus.classList.remove('hidden');
        setPipelineStep(1);
    }
}

function finishLoading() {
    submitBtn.disabled = false;
    btnText.textContent = 'Run Triage Analysis';
    btnSpinner.classList.add('hidden');
    pipelineStatus.classList.add('hidden');
    pipelinePhase = 0;
}
