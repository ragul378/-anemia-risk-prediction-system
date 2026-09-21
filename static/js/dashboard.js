/**
 * Dashboard Risk Trend Chart using Chart.js
 * Visualizes real user assessment history over time.
 */

document.addEventListener('DOMContentLoaded', () => {
    const chartCanvas = document.getElementById('riskTrendChart');
    if (!chartCanvas) return;

    // Fetch trend data via API or read data attributes
    fetch('/api/user/trends')
        .then(response => response.json())
        .then(res => {
            if (!res.labels || res.labels.length === 0) {
                const container = chartCanvas.parentElement;
                container.innerHTML = `
                    <div class="text-center py-5 text-muted">
                        <i class="bi bi-graph-up-arrow fs-1 d-block mb-3 opacity-50"></i>
                        <p class="mb-1 fw-semibold">No assessment history available yet.</p>
                        <small>Take your first AI screening assessment to visualize your trend line.</small>
                    </div>
                `;
                return;
            }

            const ctx = chartCanvas.getContext('2d');

            // Gradient fill under the line
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(139, 30, 63, 0.25)');
            gradient.addColorStop(1, 'rgba(139, 30, 63, 0.01)');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: res.labels,
                    datasets: [{
                        label: 'Estimated Risk Probability (%)',
                        data: res.data,
                        borderColor: '#8b1e3f',
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#8b1e3f',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                font: {
                                    family: "'Plus Jakarta Sans', sans-serif",
                                    weight: 600
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: '#23272a',
                            titleFont: { family: "'Plus Jakarta Sans', sans-serif" },
                            bodyFont: { family: "'Plus Jakarta Sans', sans-serif" },
                            callbacks: {
                                label: function(context) {
                                    return ` Risk Probability: ${context.parsed.y}%`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(err => {
            console.error("Error loading risk trend chart data:", err);
        });
});
