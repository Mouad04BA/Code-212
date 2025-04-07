document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    
    // Responsive design for charts
    window.addEventListener('resize', function() {
        if (window.Chart) {
            Chart.instances.forEach(chart => {
                chart.resize();
            });
        }
    });
});

function initializeCharts() {
    // Revenue and Expense Chart
    const revenueExpenseChart = document.getElementById('revenue-expense-chart');
    if (revenueExpenseChart) {
        // Get the chart configuration
        fetchChartData('monthly_revenue_expense').then(data => {
            createBarChart(revenueExpenseChart, data);
        });
    }
    
    // Assets and Liabilities Chart
    const assetsLiabilitiesChart = document.getElementById('assets-liabilities-chart');
    if (assetsLiabilitiesChart) {
        // Get the chart configuration
        fetchChartData('assets_liabilities').then(data => {
            createPieChart(assetsLiabilitiesChart, data);
        });
    }
    
    // Expense Breakdown Chart
    const expenseBreakdownChart = document.getElementById('expense-breakdown-chart');
    if (expenseBreakdownChart) {
        // Get the chart configuration
        fetchChartData('expense_breakdown').then(data => {
            createDoughnutChart(expenseBreakdownChart, data);
        });
    }
}

function fetchChartData(chartType) {
    return fetch(`/reports/charts/data?type=${chartType}`)
        .then(response => response.json())
        .catch(error => {
            console.error('Error fetching chart data:', error);
            return {
                labels: [],
                datasets: []
            };
        });
}

function createBarChart(canvas, data) {
    const ctx = canvas.getContext('2d');
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#eee' : '#333';
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    backgroundColor: isDarkMode ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.7)',
                    titleColor: isDarkMode ? '#fff' : '#000',
                    bodyColor: isDarkMode ? '#fff' : '#000',
                    borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('fr-MA', { 
                                    style: 'currency', 
                                    currency: 'MAD',
                                    minimumFractionDigits: 2
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
    
    // Store the chart instance for theme updates
    canvas._chart = chart;
}

function createPieChart(canvas, data) {
    const ctx = canvas.getContext('2d');
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#eee' : '#333';
    
    const chart = new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    backgroundColor: isDarkMode ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.7)',
                    titleColor: isDarkMode ? '#fff' : '#000',
                    bodyColor: isDarkMode ? '#fff' : '#000',
                    borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += new Intl.NumberFormat('fr-MA', { 
                                    style: 'currency', 
                                    currency: 'MAD',
                                    minimumFractionDigits: 2
                                }).format(context.parsed);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
    
    // Store the chart instance for theme updates
    canvas._chart = chart;
}

function createDoughnutChart(canvas, data) {
    const ctx = canvas.getContext('2d');
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#eee' : '#333';
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    backgroundColor: isDarkMode ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.7)',
                    titleColor: isDarkMode ? '#fff' : '#000',
                    bodyColor: isDarkMode ? '#fff' : '#000',
                    borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += new Intl.NumberFormat('fr-MA', { 
                                    style: 'currency', 
                                    currency: 'MAD',
                                    minimumFractionDigits: 2
                                }).format(context.parsed);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
    
    // Store the chart instance for theme updates
    canvas._chart = chart;
}

function updateChartsTheme() {
    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? '#eee' : '#333';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    if (window.Chart) {
        Chart.instances.forEach(chart => {
            // Update legend colors
            if (chart.options.plugins.legend) {
                chart.options.plugins.legend.labels.color = textColor;
            }
            
            // Update tooltip colors
            if (chart.options.plugins.tooltip) {
                chart.options.plugins.tooltip.backgroundColor = isDarkMode ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.7)';
                chart.options.plugins.tooltip.titleColor = isDarkMode ? '#fff' : '#000';
                chart.options.plugins.tooltip.bodyColor = isDarkMode ? '#fff' : '#000';
                chart.options.plugins.tooltip.borderColor = isDarkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)';
            }
            
            // Update scales if it's a bar/line chart
            if (chart.options.scales) {
                if (chart.options.scales.y) {
                    chart.options.scales.y.ticks.color = textColor;
                    chart.options.scales.y.grid.color = gridColor;
                }
                
                if (chart.options.scales.x) {
                    chart.options.scales.x.ticks.color = textColor;
                    chart.options.scales.x.grid.color = gridColor;
                }
            }
            
            chart.update();
        });
    }
}
