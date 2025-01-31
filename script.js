document.getElementById('automated-btn').addEventListener('click', async () => {
    const response = await fetch('/automated', { method: 'POST' });
    const data = await response.json();
    if (data.error) {
        document.getElementById('automated-result').innerText = data.error;
    } else {
        document.getElementById('automated-result').innerText = JSON.stringify(data, null, 2);
    }
});

document.getElementById('semi-automated-btn').addEventListener('click', async () => {
    const temperature = document.getElementById('temperature').value;
    const rh = document.getElementById('rh').value;
    const response = await fetch('/semi-automated', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ temperature, rh })
    });
    const data = await response.json();
    if (data.error) {
        document.getElementById('semi-automated-result').innerText = data.error;
    } else {
        document.getElementById('semi-automated-result').innerText = JSON.stringify(data, null, 2);
    }
});

document.getElementById('manual-btn').addEventListener('click', async () => {
    const cropName = document.getElementById('crop-name').value;
    const standardWeek = document.getElementById('standard-week').value;
    const maxTemp = document.getElementById('max-temp').value;
    const minTemp = document.getElementById('min-temp').value;
    const rh1 = document.getElementById('rh1').value;
    const rh2 = document.getElementById('rh2').value;
    const rainfall = document.getElementById('rainfall').value;
    const response = await fetch('/manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            crop_name: cropName,
            standard_week: standardWeek,
            max_temp: maxTemp,
            min_temp: minTemp,
            rh1: rh1,
            rh2: rh2,
            rainfall: rainfall
        })
    });
    const data = await response.json();
    if (data.error) {
        document.getElementById('manual-result').innerText = data.error;
    } else {
        document.getElementById('manual-result').innerText = `Predicted Pest: ${data.predicted_pest}`;
    }
});