// Global Chart Defaults
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(10, 10, 15, 0.9)';
Chart.defaults.plugins.tooltip.titleColor = '#fff';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initCharts();
    initMatchEngine();
});

// Navigation Logic
function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.view-section');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active state
            navBtns.forEach(b => b.classList.remove('active'));
            sections.forEach(s => s.classList.add('hidden'));

            // Set active state
            btn.classList.add('active');
            document.getElementById(btn.dataset.target).classList.remove('hidden');
        });
    });
}

// Chart Initializations
function initCharts() {
    // 1. Readiness Gauge (180 Doughnut)
    const ctxReadiness = document.getElementById('readinessChart').getContext('2d');
    new Chart(ctxReadiness, {
        type: 'doughnut',
        data: {
            labels: ['Ready', 'Remaining'],
            datasets: [{
                data: [84, 16],
                backgroundColor: ['#00f0ff', 'rgba(255, 255, 255, 0.05)'],
                borderWidth: 0,
                cutout: '80%',
                circumference: 180,
                rotation: 270
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });

    // 2. 7-Dimension Radar
    const ctxRadar = document.getElementById('radarChart').getContext('2d');
    new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: ['Positioning', 'Evidence Q.', 'Keyword Cov.', 'Portfolio', 'Completeness', 'Conversion', 'Pricing'],
            datasets: [{
                label: 'Current Profile',
                data: [85, 92, 78, 88, 95, 70, 80],
                backgroundColor: 'rgba(112, 0, 255, 0.2)',
                borderColor: '#7000ff',
                pointBackgroundColor: '#00f0ff',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#00f0ff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    pointLabels: { color: '#94a3b8', font: { size: 11, family: "'Space Mono', monospace" } },
                    ticks: { display: false, max: 100, min: 0 }
                }
            },
            plugins: { legend: { display: false } }
        }
    });

    // 3. Claim Stacked Bar
    const ctxBar = document.getElementById('claimBarChart').getContext('2d');
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Total Claims'],
            datasets: [
                {
                    label: 'Verified (T1-T4)',
                    data: [42],
                    backgroundColor: '#00ff66',
                    barThickness: 30
                },
                {
                    label: 'Unverified (T5-T8)',
                    data: [15],
                    backgroundColor: 'rgba(0, 240, 255, 0.3)',
                    barThickness: 30
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: { stacked: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { stacked: true, grid: { display: false } }
            },
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12 } }
            }
        }
    });

    // 4. Gap Action Scatter
    const ctxScatter = document.getElementById('scatterChart').getContext('2d');
    new Chart(ctxScatter, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Skill Actions',
                data: [
                    { x: 5, y: 15 }, // High points, low hours (Quick win)
                    { x: 10, y: 8 },
                    { x: 25, y: 30 }, // High hours, high points
                    { x: 40, y: 12 }, // High hours, low points
                ],
                backgroundColor: '#ffb800',
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'Est. Hours to Verify' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'Score Gain' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            },
            plugins: { legend: { display: false } }
        }
    });

    // 5. 5-Factor Polar Area (Opp Matcher)
    const ctxPolar = document.getElementById('polarChart').getContext('2d');
    new Chart(ctxPolar, {
        type: 'polarArea',
        data: {
            labels: ['Skill Match', 'Evidence Quality', 'Vertical Align', 'Timezone', 'Budget'],
            datasets: [{
                data: [95, 80, 100, 50, 90],
                backgroundColor: [
                    'rgba(0, 240, 255, 0.6)',
                    'rgba(0, 255, 102, 0.6)',
                    'rgba(112, 0, 255, 0.6)',
                    'rgba(255, 184, 0, 0.6)',
                    'rgba(255, 0, 60, 0.6)'
                ],
                borderWidth: 1,
                borderColor: '#14141e'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { position: 'right', labels: { color: '#94a3b8', font: { family: "'Space Mono', monospace", size: 10 } } }
            }
        }
    });
}

// Matching Engine & Proposal Workbench Logic
function initMatchEngine() {
    const triggerBtn = document.getElementById('triggerMatchBtn');
    const editor = document.getElementById('proposalEditor');
    const exportBtn = document.getElementById('exportBtn');
    
    // Mock Raw XML from backend
    const rawProposalXML = `
        We are perfectly positioned to build your backend infrastructure. 
        <verified claim_id="123e4567-e89b-12d3-a456-426614174000">Our lead architect successfully scaled a FastAPI microservices cluster to handle 10k requests/second with zero downtime</verified>.
        For data storage, <verified claim_id="987fcdeb-51a2-43d7-9012-345678901234">we deployed Postgres clustered with pgvector for sub-millisecond semantic search</verified>.
        
        Regarding deployment, <gap skill="Docker Swarm">[Requires verified proof for Skill: Docker Swarm]</gap> we will need to onboard a DevOps engineer or use our existing Kubernetes capabilities instead.
    `;

    triggerBtn.addEventListener('click', () => {
        // Animate match radial
        triggerBtn.innerText = "Computing...";
        triggerBtn.disabled = true;
        
        setTimeout(() => {
            triggerBtn.innerText = "Recompute Match";
            triggerBtn.disabled = false;
            
            // Render XML
            renderWorkbench(rawProposalXML, editor, exportBtn);
        }, 800);
    });
}

function renderWorkbench(xmlStr, editorContainer, exportBtn) {
    // 1. Convert <verified> to spans
    let html = xmlStr.replace(
        /<verified claim_id="([^"]+)">([^<]+)<\/verified>/g, 
        '<span class="verified-claim" data-claim-id="$1">$2</span>'
    );
    
    // 2. Convert <gap> to spans
    html = html.replace(
        /<gap skill="([^"]+)">([^<]+)<\/gap>/g, 
        '<span class="gap-pill" title="Missing $1">$2</span>'
    );

    editorContainer.innerHTML = `<p class="whitespace-pre-line">${html}</p>`;
    
    // Disable export if gaps exist
    if (html.includes('gap-pill')) {
        exportBtn.disabled = true;
        exportBtn.innerText = "Fix Gaps to Export";
        exportBtn.classList.remove('bg-cyber-primary', 'text-black', 'hover:bg-cyan-300');
        exportBtn.classList.add('bg-gray-700', 'text-gray-400');
    } else {
        exportBtn.disabled = false;
        exportBtn.innerText = "Export PDF";
        exportBtn.classList.add('bg-cyber-primary', 'text-black', 'hover:bg-cyan-300');
        exportBtn.classList.remove('bg-gray-700', 'text-gray-400');
    }

    attachPopoverEvents();
}

function attachPopoverEvents() {
    const claims = document.querySelectorAll('.verified-claim');
    const popover = document.getElementById('provenancePopover');
    const content = document.getElementById('popoverContent');

    claims.forEach(claim => {
        claim.addEventListener('mouseenter', (e) => {
            // Mock API Fetch
            const claimId = claim.dataset.claimId;
            content.innerHTML = `<span class="opacity-50">Fetching literal from DB for ${claimId.substring(0,8)}...</span><br/>"Architected and deployed high-performance Python/FastAPI microservices (10k req/s). Authored 142 PRs in core repo."`;
            
            const rect = claim.getBoundingClientRect();
            popover.style.left = `${rect.left}px`;
            popover.style.top = `${rect.bottom + 10}px`;
            popover.classList.remove('hidden');
            
            // Trigger animation
            setTimeout(() => popover.classList.remove('opacity-0'), 10);
        });

        claim.addEventListener('mouseleave', () => {
            popover.classList.add('opacity-0');
            setTimeout(() => popover.classList.add('hidden'), 200);
        });
    });
}
