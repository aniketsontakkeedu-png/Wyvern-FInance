/**
 * Wyvern Charts Engine - Minimalist Nothing OS Visualizations
 */

let forecastChartInstance = null;
let categoryChartInstance = null;
let sipGrowthChartInstance = null;

// Nothing OS Dark Theme Defaults for Chart.js
function applyChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.color = '#7a7a7a';
  Chart.defaults.font.family = "'DM Mono', monospace";
  Chart.defaults.font.size = 11;
  Chart.defaults.plugins.tooltip.backgroundColor = '#181818';
  Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
  Chart.defaults.plugins.tooltip.bodyColor = '#cccccc';
  Chart.defaults.plugins.tooltip.borderColor = '#333333';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.padding = 10;
}

function renderForecastChart(canvasId, forecastData, currencySymbol = '$') {
  if (typeof Chart === 'undefined') return;
  applyChartDefaults();

  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  if (forecastChartInstance) {
    forecastChartInstance.destroy();
  }

  const labels = forecastData.projections.map(p => p.month);
  const baselineValues = forecastData.projections.map(p => p.projected_savings);
  const upperBounds = forecastData.projections.map(p => p.upper_bound);
  const lowerBounds = forecastData.projections.map(p => p.lower_bound);
  const optimizedValues = forecastData.projections.map(p => p.projected_savings * 1.24);

  forecastChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Wyvern Optimized (+24%)',
          data: optimizedValues,
          borderColor: '#D71921',
          borderWidth: 2,
          pointBackgroundColor: '#D71921',
          pointBorderColor: '#000000',
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.35
        },
        {
          label: 'Baseline Trajectory',
          data: baselineValues,
          borderColor: '#ffffff',
          borderWidth: 2,
          pointBackgroundColor: '#ffffff',
          pointBorderColor: '#000000',
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.35
        },
        {
          label: 'Confidence Upper (p90)',
          data: upperBounds,
          borderColor: 'transparent',
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          fill: '+1',
          pointRadius: 0,
          tension: 0.35
        },
        {
          label: 'Confidence Lower (p10)',
          data: lowerBounds,
          borderColor: 'transparent',
          backgroundColor: 'transparent',
          pointRadius: 0,
          tension: 0.35
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            boxWidth: 10,
            usePointStyle: true,
            filter: function(item) {
              return !item.text.includes('Confidence');
            }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              if (context.dataset.label.includes('Confidence')) return null;
              return `${context.dataset.label}: ${currencySymbol}${context.parsed.y.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: '#1a1a1a',
            drawBorder: false
          }
        },
        y: {
          grid: {
            color: '#1a1a1a',
            drawBorder: false
          },
          ticks: {
            callback: function(val) {
              return currencySymbol + val.toLocaleString();
            }
          }
        }
      }
    }
  });
}

function renderCategoryChart(canvasId, categoryData) {
  if (typeof Chart === 'undefined') return;
  applyChartDefaults();

  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  if (categoryChartInstance) {
    categoryChartInstance.destroy();
  }

  const topCats = categoryData.slice(0, 6);
  const labels = topCats.map(c => c.category);
  const amounts = topCats.map(c => c.amount);

  // Nothing OS monochrome palette with signature red for top expense
  const palette = [
    '#D71921', // Signature red for highest
    '#f0f0f0',
    '#b0b0b0',
    '#757575',
    '#4a4a4a',
    '#292929'
  ];

  categoryChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [
        {
          data: amounts,
          backgroundColor: palette.slice(0, amounts.length),
          borderColor: '#121212',
          borderWidth: 2,
          hoverOffset: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: {
          display: true,
          position: 'right',
          labels: {
            boxWidth: 8,
            usePointStyle: true,
            color: '#9e9e9e',
            font: { size: 10 }
          }
        },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              return ` ${ctx.label}: $${ctx.parsed.toLocaleString()}`;
            }
          }
        }
      }
    }
  });
}

function renderSipGrowthChart(canvasId, milestones, currencySymbol = '$') {
  if (typeof Chart === 'undefined') return;
  applyChartDefaults();

  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  if (sipGrowthChartInstance) {
    sipGrowthChartInstance.destroy();
  }

  const labels = milestones.map(m => `Yr ${m.year}`);
  const invested = milestones.map(m => m.invested);
  const futureValues = milestones.map(m => m.future_value);
  const wealthGained = milestones.map(m => m.wealth_gained);

  sipGrowthChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Total Future Corpus',
          data: futureValues,
          borderColor: '#D71921',
          backgroundColor: 'rgba(215, 25, 33, 0.1)',
          fill: true,
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: '#D71921',
          tension: 0.3
        },
        {
          label: 'Amount Invested',
          data: invested,
          borderColor: '#ffffff',
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [4, 4],
          pointRadius: 2,
          pointBackgroundColor: '#ffffff',
          tension: 0.1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            boxWidth: 10,
            usePointStyle: true
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${currencySymbol}${context.parsed.y.toLocaleString('en-US', {maximumFractionDigits: 0})}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: '#1a1a1a', drawBorder: false }
        },
        y: {
          grid: { color: '#1a1a1a', drawBorder: false },
          ticks: {
            callback: function(val) {
              return currencySymbol + (val >= 1000000 ? (val/1000000).toFixed(1) + 'M' : (val >= 1000 ? (val/1000).toFixed(0) + 'k' : val));
            }
          }
        }
      }
    }
  });
}
