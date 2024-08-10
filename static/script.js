document.getElementById('priceCalcForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const storage = [];

    for (let i = 0; i < formData.getAll('storage_size').length; i++) {
        storage.push({
            size: formData.getAll('storage_size')[i],
            kind: formData.getAll('storage_kind')[i],
            unit: formData.getAll('storage_unit')[i] 
        });
    }

    const data = {
        kind: formData.get('kind'),
        model: formData.get('model'),
        amd_price: parseFloat(formData.get('amd_price') || 0),
        ram_size: parseFloat(formData.get('ram_size')),
        os: formData.get('os'),
        storage: storage,
        is_laptop: formData.get('is_laptop') === 'yes',
        battery_capacity: parseFloat(formData.get('battery_capacity') || 0),
        has_large_screen: formData.get('has_large_screen') === 'yes',
        has_touch_screen: formData.get('has_touch_screen') === 'yes',
        wifi_kind: formData.get('wifi_kind'),
        has_gpu: formData.get('has_gpu') === 'yes',
        gpu_type: formData.get('gpu_type') || '',
        passmark_score: parseFloat(formData.get('passmark_score') || 0),
        custom_build: formData.get('custom_build') === 'yes',
        desktop_bluetooth: formData.get('desktop_bluetooth') === 'yes'
    };

    const response = await fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    document.getElementById('result').innerHTML = `
        <h4>Results:</h4>
        <p>Processor Price: $${result.processor_price}</p>
        <p>RAM Price: $${result.ram_price}</p>
        <p>Storage Price: $${result.storage_price}</p>
        <p>OS Price: $${result.os_price}</p>
        <p>GPU Price: $${result.gpu_price}</p>
        <h3>Total Price: $${result.total_price}</h3>
    `;
});

function addStorage() {
    const container = document.getElementById('storage-container');
    if (container.querySelectorAll('.storage-item').length >= 4) return;

    const storageItem = document.createElement('div');
    storageItem.className = 'form-group storage-item';
    storageItem.innerHTML = `
        <label>Storage Device</label>
        <div class="input-group mb-3">
            <input type="number" class="form-control" name="storage_size" placeholder="e.g., 500" required>
            <select class="form-control" name="storage_unit" required>
                <option value="GB">GB</option>
                <option value="TB">TB</option>
            </select>
            <select class="form-control" name="storage_kind" required>
                <option value="HDD">HDD</option>
                <option value="SATA">SATA</option>
                <option value="NvME">NvME</option>
            </select>
            <div class="input-group-append">
                <button class="btn btn-danger" type="button" onclick="removeStorage(this)">Remove</button>
            </div>
        </div>
    `;
    container.appendChild(storageItem);
}

function removeStorage(button) {
    button.closest('.storage-item').remove();
}

function toggleProcessorOptions() {
    const kind = document.getElementById('kind').value;
    const amdPriceContainer = document.getElementById('amd-price-container');
    
    if (kind.toLowerCase() === 'amd') {
        amdPriceContainer.style.display = '';
    } else {
        amdPriceContainer.style.display = 'none';
    }
}

function toggleLaptopOptions() {
    const isLaptop = document.getElementById('is_laptop').value === 'yes';
    document.getElementById('laptop-options').style.display = isLaptop ? 'block' : 'none';
    document.getElementById('desktop-options').style.display = isLaptop ? 'none' : 'block';
}

function toggleGpuOptions() {
    const hasGpu = document.getElementById('has_gpu').value === 'yes';
    document.getElementById('gpu-options').style.display = hasGpu ? '' : 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    toggleLaptopOptions(); // Ensure correct initial state
});