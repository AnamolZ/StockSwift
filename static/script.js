document.addEventListener('DOMContentLoaded', function () {
    const eventSource = new EventSource("/stock_data_generator");
    const loadingElement = document.getElementById('loading');
    const chartContainer = document.getElementById('stockChart');

    loadingElement.style.display = 'block';
    chartContainer.style.display = 'none';

    eventSource.onmessage = function (event) {
        const stockData = JSON.parse(event.data);
        loadingElement.style.display = 'none';
        chartContainer.style.display = 'block';

        const labels = Object.keys(stockData);
        const data = Object.values(stockData);
        const colors = generateRandomColors(data.length);

        createOrUpdateChart(labels, data, colors);

        setInterval(() => {
            createOrUpdateChart(labels, data, colors);
        }, 5000);
    };

    function createOrUpdateChart(labels, data, colors) {
        const ctx = document.getElementById('stockChart').getContext('2d');

        if (window.myChart) {
            window.myChart.data.labels = labels;
            window.myChart.data.datasets[0].data = data;
            window.myChart.data.datasets[1].data = data;
            window.myChart.update();
        } else {
            window.myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: 'Stock Prices (Bar)',
                        data,
                        backgroundColor: colors.map(color => `rgba(${color.join(',')}, 0.2)`),
                        borderColor: colors.map(color => `rgba(${color.join(',')}, 1)`),
                        borderWidth: 1,
                    }, {
                        label: 'Stock Prices (Line)',
                        data,
                        borderColor: 'white',
                        borderWidth: 2,
                        fill: false,
                        type: 'line',
                    }]
                },
                options: {
                    scales: {
                        y: {
                            display: true,
                            beginAtZero: true,
                            max: 500,
                            ticks: { color: 'white' },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)',
                                borderColor: 'rgba(255, 255, 255, 0.1)',
                                borderWidth: 1
                            }
                        },
                        x: { ticks: { color: 'white' } }
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        }
    }

    function generateRandomColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push([Math.floor(Math.random() * 256), Math.floor(Math.random() * 256), Math.floor(Math.random() * 256)]);
        }
        return colors;
    }
});
