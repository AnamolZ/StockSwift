async function main() {
    try {
        const loadingElement = document.getElementById('loading');
        loadingElement.style.display = 'block';

        const chartContainer = document.getElementById('stockChart');
        chartContainer.style.display = 'none';

        const socket = new WebSocket('ws://localhost:8000/ws');
        socket.onmessage = async (event) => {
            const stockData = JSON.parse(event.data);

            loadingElement.style.display = 'none';
            chartContainer.style.display = 'block';

            const labels = Object.keys(stockData);
            const prices = labels.map(symbol => stockData[symbol].price);
        
            const data = prices.map(price => parseFloat(price.toFixed(2)));

            console.log(labels);
            console.log(data);

            createOrUpdateChart(labels, data);

            setInterval(() => {
                createOrUpdateChart(labels, data);
            }, 5000);
        };

    } catch (error) {
        console.error('Error in main function:', error);
    }
}

