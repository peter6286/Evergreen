document.addEventListener('DOMContentLoaded', fetchData); // Fetch data when the document is fully loaded

        async function fetchData() {
            const apiUrl = 'https://brmdysr4f8.execute-api.us-east-2.amazonaws.com/initial/sensordata';
            try {
                const response = await fetch(apiUrl);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                console.log(data)
                
                displayData(data);
            } catch (error) {
                console.error('Fetch error:', error);
                document.getElementById('dataDisplay').innerHTML = `Error: ${error.message}`;
            }
        }
        function displayData(data) {
            const display = document.getElementById('dataDisplay');
            display.innerHTML = '<h2>Current Data</h2>'; // Add a title
        
            // Assuming data is an array and data[0] exists and contains the payload
            const payload = data[0].payload.M;
        
            // Define the data points to extract
            const dataPoints = {
                temperature: { value: payload.temperature.N, unit: '°C' },
                humidity: { value: payload.humidity.N, unit: '%' },
                light_level: { value: payload.light_level.N, unit: 'lux' },
                timestamp: { value: payload.timestamp.S, unit: '' } // No unit for timestamp
            };
        
            // Create a bubble for each data point
            for (const [key, { value, unit }] of Object.entries(dataPoints)) {
                const bubble = document.createElement('div');
                bubble.className = 'data-bubble';
                bubble.innerHTML = `
                    <div class="data-title">${capitalizeFirstLetter(key.replace('_', ' '))}</div>
                    <div class="data-value">${value}${unit}</div>
                `;
                display.appendChild(bubble);
            }
        }
        
        // Helper function to capitalize the first letter of a string
        function capitalizeFirstLetter(string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
        }
        
        function updateScheduleTime() {
            const now = new Date();
            const nextSchedule = new Date(now.getTime() + 6 * 60 * 60 * 1000); // Adding 6 hours
            const formattedTime = nextSchedule.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
        
            document.getElementById('nextScheduleTime').textContent = formattedTime;
        }

        document.getElementById('triggerButton').addEventListener('click', function() {
            console.log('button clicked!')
            fetch('http://127.0.0.1:8080/trigger-device-function')
                .then(response => response.text())
                .then(data => alert(data))
                .catch(error => console.error('Error:', error));
        });
        

        // Initial call
        updateScheduleTime();
        
        // Update the time every minute in case the page is left open
        setInterval(updateScheduleTime, 60 * 1000);
        