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
    let resultHTML = '<h4>Results:</h4>';
    if (result.processor_price) resultHTML += `<p>Processor Price: $${result.processor_price}</p>`;
    if (result.ram_price) resultHTML += `<p>RAM Price: $${result.ram_price}</p>`;
    if (result.storage_price) resultHTML += `<p>Storage Price: $${result.storage_price}</p>`;
    if (result.os_price) resultHTML += `<p>OS Price: $${result.os_price}</p>`;
    if (result.gpu_price) resultHTML += `<p>GPU Price: $${result.gpu_price}</p>`;
    
    // Add laptop-specific prices if the computer is a laptop
    if (data.is_laptop) {
        if (result.laptop_base_price) resultHTML += `<p>Laptop Price: $${result.laptop_base_price}</p>`;
        if (result.battery_discount) resultHTML += `<p>Battery Discount: $${result.battery_discount}</p>`;
        if (result.large_screen_price) resultHTML += `<p>Large Screen Price: $${result.large_screen_price}</p>`;
        if (result.touch_screen_price) resultHTML += `<p>Touch Screen Price: $${result.touch_screen_price}</p>`;
    }

    // Add desktop-specific prices if the computer is a desktop
    if (!data.is_laptop) {
        if (result.wifi_price) resultHTML += `<p>Wi-Fi Price: $${result.wifi_price}</p>`;
        if (result.bluetooth_price) resultHTML += `<p>Bluetooth Price: $${result.bluetooth_price}</p>`;
    }

    if (result.ram_discount) resultHTML += `<p>RAM Discount: $${result.ram_discount}</p>`;
    if (result.custom_build_price) resultHTML += `<p>Custom Build Price: $${result.custom_build_price}</p>`;

    resultHTML += `<h3>Total Price: $${result.total_price}</h3>`;

    document.getElementById('result').innerHTML = resultHTML;
    document.getElementById('transferToBuildSheet').style.display = 'inline-block';

    // Add event listener for transfer button
    document.getElementById('transferToBuildSheet').addEventListener('click', function() {
        const formData = new FormData(document.getElementById('priceCalcForm'));
        const osMapping = {
            'windows11': 'Windows 11',
            'windows10': 'Windows 10',
            'linux': 'Linux Mint'
        };

        const storage = [];

        // Get all storage devices
        const sizes = formData.getAll('storage_size');
        const kinds = formData.getAll('storage_kind');
        const units = formData.getAll('storage_unit');
        
        // Group storage devices by type
        const ssdDevices = [];
        const hddDevices = [];

        for (let i = 0; i < sizes.length; i++) {
            const device = {
                size: sizes[i],
                kind: kinds[i],
                unit: units[i]
            };
            
            if (kinds[i].toLowerCase() === 'hdd') {
                hddDevices.push(device);
            } else {
                ssdDevices.push(device);
            }
        }

        
        const calculatorData = {
            price: result.total_price,
            manufacturer: formData.get('kind') === 'intel' ? 'Intel' : 'AMD',
            model: formData.get('model'),
            ram: formData.get('ram_size'),
            OS: osMapping[formData.get('os')] || formData.get('os'),
            // Storage data
            ssd1_storage: ssdDevices[0]?.size || '',
            ssd1_storage_unit: ssdDevices[0]?.unit || 'GB',
            ssd1_type: ssdDevices[0]?.kind === 'NvME' ? 'NVMe' : 'SATA',
            ssd2_storage: ssdDevices[1]?.size || '',
            ssd2_storage_unit: ssdDevices[1]?.unit || 'GB',
            ssd2_type: ssdDevices[1]?.kind === 'NvME' ? 'NVMe' : 'SATA',
            hdd1_storage: hddDevices[0]?.size || '',
            hdd1_storage_unit: hddDevices[0]?.unit || 'GB',
            hdd2_storage: hddDevices[1]?.size || '',
            hdd2_storage_unit: hddDevices[1]?.unit || 'GB',
            is_laptop: formData.get('is_laptop') === 'yes'
        };
        
        // Store data in sessionStorage
        sessionStorage.setItem('calculatorData', JSON.stringify(calculatorData));
        
        // Redirect to build sheet page
        window.location.href = '/build-sheet';
    });
});


function addStorage() {
    const container = document.getElementById('storage-container');
    if (container.querySelectorAll('.storage-item').length >= 4) return;

    const storageItem = document.createElement('div');
    storageItem.className = 'form-group storage-item';
    storageItem.innerHTML = `
        <label>Storage Device</label>
        <div class="input-group mb-3">
            <input type="number" class="form-control" name="storage_size" placeholder="e.g., 500" step="any" required>
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