async function main() {
    try {
        // Retrieve the loading element and set its display to 'block'
        const loadingElement = document.getElementById('loading');
        loadingElement.style.display = 'block';
        // Retrieve the stock chart container and initially hide it
        const chartContainer = document.getElementById('stockChart');
        chartContainer.style.display = 'none';
        // Establish a WebSocket connection to receive real-time stock data
        const socket = new WebSocket('ws://localhost:8000/ws');
        // Handle incoming messages from the WebSocket
        socket.onmessage = async (event) => {
            const stockData = JSON.parse(event.data);
            // Hide the loading element and display the stock chart container
            loadingElement.style.display = 'none';
            chartContainer.style.display = 'block';

            const labels = Object.keys(stockData);
            const prices = labels.map(symbol => stockData[symbol].price);
            const data = prices.map(price => parseFloat(price.toFixed(2)));

            createOrUpdateChart(labels, data);
            // Schedule periodic updates of the stock chart every 5 seconds
            setInterval(() => {
                createOrUpdateChart(labels, data);
            }, 5000);
        };
    } catch (error) {
        console.error('Error in main function:', error);
    }
}

function createOrUpdateChart(labels, data) {
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
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
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
                        beginAtZero: true,
                        max: 500,
                        ticks: { color: 'white' }
                    },
                    x: { ticks: { color: 'white' } }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });            
    }
}

main();