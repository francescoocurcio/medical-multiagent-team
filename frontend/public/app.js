const BACKEND_URL = 'http://localhost:8000';

const form = document.getElementById('triage-form');
const submitBtn = document.getElementById('submit-btn');
const btnText = document.getElementById('btn-text');
const btnSpinner = document.getElementById('btn-spinner');
const symptomsContent = document.getElementById('symptoms-content');
const reportContent = document.getElementById('report-content');

let eventSource = null;
let agent1Buffer = '';
let reportBuffer = '';

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
            setLoading(false);
            eventSource.close();
            return;
        }

        const { node, text } = payload;

        if (node === 'Agent_1_extract_symptoms') {
            agent1Buffer += text;
            tryRenderSymptoms(agent1Buffer);
        } else if (node === 'Agent_3_synthesize_diagnose') {
            setLoading(false);
            reportBuffer += text;
            reportContent.classList.remove('placeholder');
            reportContent.innerHTML = marked.parse(reportBuffer);
        }
    };

    eventSource.onerror = () => {
        setLoading(false);
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
        }
    } catch {
        // Buffer not yet complete JSON — keep accumulating
    }
}

function resetUI() {
    agent1Buffer = '';
    reportBuffer = '';
    symptomsContent.innerHTML = 'Awaiting analysis...';
    symptomsContent.classList.add('placeholder');
    reportContent.innerHTML = 'Awaiting analysis...';
    reportContent.classList.add('placeholder');
}

function setLoading(active) {
    submitBtn.disabled = active;
    btnText.textContent = active ? 'Analyzing...' : 'Run Triage Analysis';
    btnSpinner.classList.toggle('hidden', !active);
}
