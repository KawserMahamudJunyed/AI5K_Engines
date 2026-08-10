// State
let radarChartInstance = null;
let gaugeChartInstance = null;

// Elements
const form = document.getElementById('analyze-form');
const loader = document.getElementById('loader');
const loaderText = document.getElementById('loader-text');
const resultsSection = document.getElementById('results-section');
const scoreValue = document.getElementById('score-value');
const genTitle = document.getElementById('gen-title');
const genOverview = document.getElementById('gen-overview');
const genSkills = document.getElementById('gen-skills');
const blockersContainer = document.getElementById('blockers-container');

// Event Listener
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const niche = document.getElementById('niche').value;
  const version = document.getElementById('version').value;
  const rate = parseFloat(document.getElementById('rate').value) || null;
  const cvText = document.getElementById('cv').value;

  // Show loader
  loader.classList.remove('hidden');
  resultsSection.classList.add('hidden');
  
  try {
    // Determine base URL (handles local dev vs production)
    const baseUrl = window.location.hostname === 'localhost' && window.location.port === '5173' 
      ? 'http://127.0.0.1:8000' 
      : '';

    // 1. Submit job
    loaderText.innerText = 'Extracting Claims...';
    
    const formData = new FormData();
    const cvFile = document.getElementById('cv_file').files[0];
    const githubUrl = document.getElementById('github_url').value;
    const upworkUrl = document.getElementById('upwork_url').value;
    const cvText = document.getElementById('cv').value;

    if (cvFile) formData.append('cv_file', cvFile);
    if (githubUrl) formData.append('github_url', githubUrl);
    if (upworkUrl) formData.append('upwork_url', upworkUrl);
    if (cvText) formData.append('cv_text', cvText);
    if (rate) formData.append('rate_desired', rate);

    const res = await fetch(`${baseUrl}/analyze?niche=${encodeURIComponent(niche)}&version=${encodeURIComponent(version)}`, {
      method: 'POST',
      body: formData
    });
    
    // Because it followed redirect, the response URL is now the status URL!
    let statusUrl = res.url;
    let runId = statusUrl.split('/analyze/')[1].split('/')[0];
    const resultUrl = `${baseUrl}/analyze/${runId}/result`;

    // 2. Poll Status
    let finished = false;
    while (!finished) {
      const statRes = await fetch(statusUrl);
      const statData = await statRes.json();
      
      loaderText.innerText = `Stage: ${statData.stage} (${statData.progress_pct.toFixed(0)}%)`;
      
      if (statData.finished_at) {
        if (statData.error) {
          throw new Error(statData.error);
        }
        finished = true;
      } else {
        await new Promise(r => setTimeout(r, 1000));
      }
    }

    // 3. Fetch Final Result
    loaderText.innerText = 'Rendering Results...';
    const resultRes = await fetch(resultUrl);
    const resultData = await resultRes.json();

    // 4. Update UI
    renderResults(resultData);

  } catch (error) {
    alert(`Pipeline Error: ${error.message}`);
  } finally {
    loader.classList.add('hidden');
  }
});

function renderResults(data) {
  resultsSection.classList.remove('hidden');

  // Text Data
  genTitle.innerText = data.generated_assets.title || 'N/A';
  genTitle.className = '';
  
  genOverview.innerText = data.generated_assets.overview || 'Overview generation blocked due to lack of verifiable evidence.';
  genOverview.className = '';

  genSkills.innerHTML = '';
  data.generated_assets.skill_highlights.forEach(skill => {
    const span = document.createElement('span');
    span.className = 'skill-tag';
    span.innerText = skill;
    genSkills.appendChild(span);
  });

  // Blockers
  if (data.blocking_items && data.blocking_items.length > 0) {
    blockersContainer.classList.remove('hidden');
    blockersContainer.innerHTML = '<strong>Critical Blockers:</strong><br>' + data.blocking_items.join('<br>');
  } else {
    blockersContainer.classList.add('hidden');
  }

  // Animate Number
  animateValue(scoreValue, 0, data.readiness_score, 1500);

  // Render Charts
  renderGauge(data.readiness_score);
  renderRadar(data.dimension_scores);
}

function animateValue(obj, start, end, duration) {
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    obj.innerHTML = Math.floor(progress * (end - start) + start);
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}

function renderGauge(score) {
  const ctx = document.getElementById('gaugeChart');
  if (gaugeChartInstance) gaugeChartInstance.destroy();

  const color = score >= 80 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';

  gaugeChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [score, 100 - score],
        backgroundColor: [color, 'rgba(255,255,255,0.05)'],
        borderWidth: 0,
        circumference: 180,
        rotation: 270,
        cutout: '80%'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { tooltip: { enabled: false }, legend: { display: false } }
    }
  });
}

function renderRadar(dimensions) {
  const ctx = document.getElementById('radarChart');
  if (radarChartInstance) radarChartInstance.destroy();

  const labels = Object.keys(dimensions).map(k => k.replace('_', ' ').toUpperCase());
  const data = Object.values(dimensions);

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Dimension Score',
        data: data,
        backgroundColor: 'rgba(139, 92, 246, 0.2)',
        borderColor: '#8b5cf6',
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#3b82f6'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' },
          pointLabels: { color: '#9ca3af', font: { size: 10, family: 'Inter' } },
          ticks: { display: false, min: 0, max: 100 }
        }
      },
      plugins: { legend: { display: false } }
    }
  });
}
