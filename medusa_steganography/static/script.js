let stegoImageData = null;
let dataLength = 0;
let psnrChart, ssimChart, accuracyChart;

function switchTab(tab, event) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    event.target.closest('.tab-btn').classList.add('active');
    document.getElementById(`${tab}-tab`).classList.add('active');
}

function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 4000);
}

document.getElementById('embed-image').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const preview = document.getElementById('embed-preview');
            preview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
        document.querySelector('#embed-image + .file-label').innerHTML =
            `<i class="fas fa-check-circle"></i> ${file.name}`;
    }
});

document.getElementById('extract-image').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const preview = document.getElementById('extract-preview');
            preview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
        document.querySelector('#extract-image + .file-label').innerHTML =
            `<i class="fas fa-check-circle"></i> ${file.name}`;
    }
});

document.getElementById('compare-image').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const preview = document.getElementById('compare-preview');
            preview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
        document.querySelector('#compare-image + .file-label').innerHTML =
            `<i class="fas fa-check-circle"></i> ${file.name}`;
    }
});

document.getElementById('embed-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData();
    const imageFile = document.getElementById('embed-image').files[0];
    const secretData = document.getElementById('embed-data').value;
    const method = document.querySelector('input[name="embed-method"]:checked').value;

    if (!imageFile) {
        showNotification('Please select an image', 'error');
        return;
    }

    try {
        JSON.parse(secretData);
    } catch (e) {
        showNotification('Invalid JSON format for secret data', 'error');
        return;
    }

    formData.append('image', imageFile);
    formData.append('secret_data', secretData);
    formData.append('method', method);

    showLoading();

    try {
        const response = await fetch('/api/embed', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            stegoImageData = data.stego_image;
            dataLength = data.data_length;

            document.getElementById('embed-psnr').textContent = data.psnr.toFixed(2);
            document.getElementById('embed-ssim').textContent = data.ssim.toFixed(4);
            document.getElementById('embed-accuracy').textContent = data.bit_accuracy.toFixed(2);
            document.getElementById('stego-image').src = 'data:image/png;base64,' + data.stego_image;
            document.getElementById('embed-results').style.display = 'block';

            showNotification('Data embedded successfully!');
        } else {
            showNotification(data.error || 'Embedding failed', 'error');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
});

document.getElementById('extract-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData();
    const imageFile = document.getElementById('extract-image').files[0];
    const method = document.querySelector('input[name="extract-method"]:checked').value;
    const length = document.getElementById('extract-length').value;

    if (!imageFile) {
        showNotification('Please select an image', 'error');
        return;
    }

    if (!length || length <= 0) {
        showNotification('Please enter valid data length', 'error');
        return;
    }

    formData.append('image', imageFile);
    formData.append('method', method);
    formData.append('data_length', length);

    showLoading();

    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            let extractedText = data.extracted_data;

            try {
                const jsonData = JSON.parse(extractedText);
                extractedText = JSON.stringify(jsonData, null, 2);
            } catch (e) {
                // Not JSON, display as is
            }

            document.getElementById('extracted-text').textContent = extractedText;
            document.getElementById('extract-results').style.display = 'block';

            showNotification('Data extracted successfully!');
        } else {
            showNotification(data.error || 'Extraction failed', 'error');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
});

document.getElementById('compare-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData();
    const imageFile = document.getElementById('compare-image').files[0];
    const secretData = document.getElementById('compare-data').value;

    if (!imageFile) {
        showNotification('Please select an image', 'error');
        return;
    }

    try {
        JSON.parse(secretData);
    } catch (e) {
        showNotification('Invalid JSON format for secret data', 'error');
        return;
    }

    formData.append('image', imageFile);
    formData.append('secret_data', secretData);

    showLoading();

    try {
        const response = await fetch('/api/compare', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayComparisonCharts(data.results);
            document.getElementById('compare-results').style.display = 'block';
            showNotification('Comparison completed!');
        } else {
            showNotification(data.error || 'Comparison failed', 'error');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
});

function displayComparisonCharts(results) {
    const methods = results.map(r => r.method);
    const psnrValues = results.map(r => r.psnr);
    const ssimValues = results.map(r => r.ssim);
    const accuracyValues = results.map(r => r.bit_accuracy);

    if (psnrChart) psnrChart.destroy();
    if (ssimChart) ssimChart.destroy();
    if (accuracyChart) accuracyChart.destroy();

    const chartConfig = {
        type: 'bar',
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    };

    psnrChart = new Chart(document.getElementById('psnr-chart'), {
        ...chartConfig,
        data: {
            labels: methods,
            datasets: [{
                label: 'PSNR (dB)',
                data: psnrValues,
                backgroundColor: [
                    'rgba(37, 99, 235, 0.8)',
                    'rgba(8, 145, 178, 0.8)',
                    'rgba(16, 185, 129, 0.8)'
                ],
                borderColor: [
                    'rgba(37, 99, 235, 1)',
                    'rgba(8, 145, 178, 1)',
                    'rgba(16, 185, 129, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            ...chartConfig.options,
            plugins: {
                ...chartConfig.options.plugins,
                title: {
                    display: true,
                    text: 'PSNR Comparison (Higher is Better)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            }
        }
    });

    ssimChart = new Chart(document.getElementById('ssim-chart'), {
        ...chartConfig,
        data: {
            labels: methods,
            datasets: [{
                label: 'SSIM',
                data: ssimValues,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(139, 92, 246, 0.8)'
                ],
                borderColor: [
                    'rgba(239, 68, 68, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(139, 92, 246, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            ...chartConfig.options,
            plugins: {
                ...chartConfig.options.plugins,
                title: {
                    display: true,
                    text: 'SSIM Comparison (Higher is Better)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 0.97,
                    max: 1.0
                }
            }
        }
    });

    accuracyChart = new Chart(document.getElementById('accuracy-chart'), {
        ...chartConfig,
        data: {
            labels: methods,
            datasets: [{
                label: 'Bit Accuracy (%)',
                data: accuracyValues,
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(37, 99, 235, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(37, 99, 235, 1)',
                    'rgba(245, 158, 11, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            ...chartConfig.options,
            plugins: {
                ...chartConfig.options.plugins,
                title: {
                    display: true,
                    text: 'Bit Accuracy Comparison',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 90,
                    max: 100
                }
            }
        }
    });
}

function downloadImage() {
    if (!stegoImageData) {
        showNotification('No image to download', 'error');
        return;
    }

    const link = document.createElement('a');
    link.href = 'data:image/png;base64,' + stegoImageData;
    link.download = 'steganographic_image.png';
    link.click();

    showNotification('Image downloaded!');
}

document.addEventListener('DOMContentLoaded', function() {
    const defaultSecretData = {
        patient_id: "",
        hospital: "",
        diagnosis: "",
        notes: ""
    };

    document.getElementById('embed-data').value = JSON.stringify(defaultSecretData, null, 2);
    document.getElementById('compare-data').value = JSON.stringify(defaultSecretData, null, 2);
});
