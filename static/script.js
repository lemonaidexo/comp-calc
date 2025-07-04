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
        screen_size: formData.get('screen_size') || '15.6',
        is_laptop: formData.get('is_laptop') === 'yes',
        battery_capacity: parseFloat(formData.get('battery_capacity') || 0),
        has_large_screen: formData.get('has_large_screen') === 'yes',
        has_touch_screen: formData.get('has_touch_screen') === 'yes',
        wifi_kind: formData.get('wifi_kind'),
        has_gpu: formData.get('has_gpu') === 'yes',
        gpu_type: formData.get('gpu_type') || '',
        passmark_score: parseFloat(formData.get('passmark_score') || 0),
        custom_build: formData.get('custom_build') === 'yes',
        desktop_bluetooth: formData.get('desktop_bluetooth') === 'yes',
        screen_over_60hz: formData.get('screen_over_60hz') === 'yes',
        screen_resolution: formData.get('screen_resolution')
    };

    const response = await fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    let resultHTML = data.is_laptop ? '<h4>Laptop:</h4>' : '<h4>Desktop:</h4>';

    // Helper function to format storage prices
    const formatStoragePrices = (storage, result) => {
        let storageHTML = '<div style="margin-left: 20px;">';
        let totalStoragePrice = 0;
        
        // Make sure storage_prices array exists in the result
        const storagePrices = result.storage_prices || [];
        
        storage.forEach((drive, index) => {
            // Get the specific price for this drive from the array
            const price = storagePrices[index] || 0;
            totalStoragePrice += price;
            storageHTML += `<p>Drive ${index + 1} (${drive.size}${drive.unit} ${drive.kind}): $${price}</p>`;
        });
        
        storageHTML += `<p><strong>Total Storage Price: $${totalStoragePrice}</strong></p>`;
        storageHTML += '</div>';
        return storageHTML;
    };

    // Common components
    resultHTML += `<p>Processor (${data.kind} ${data.model}): $${result.processor_price || 0}</p>`;
    resultHTML += `<p>RAM (${data.ram_size}GB): $${result.ram_price || 0}</p>`;
    resultHTML += `<p>OS (${data.os}): $${result.os_price || 0}</p>`;
    resultHTML += '<p>Storage:</p>';
    resultHTML += formatStoragePrices(data.storage, result);

    // Device-specific components
    if (data.is_laptop) {
        resultHTML += `<p>Laptop Price: $${result.laptop_base_price || 0}</p>`;
        resultHTML += '<div style="margin-left: 20px;">';
        if (result.battery_discount) {
            resultHTML += `<p>Battery Discount: -($${Math.abs(result.battery_discount)})</p>`;
        }
        if (result.large_screen_price) {
            resultHTML += `<p>Large Screen Price: $${result.large_screen_price}</p>`;
        }
        if (result.touch_screen_price) {
            resultHTML += `<p>Touch Screen: $${result.touch_screen_price}</p>`;
        }
        if (result.hz_price) {
            resultHTML += `<p>60hz+ Screen: $${result.hz_price}</p>`;
        }
        if (result.resolution_price) {
            resultHTML += `<p>Screen Resolution: $${result.resolution_price}</p>`;
        }
        resultHTML += '</div>';
    } else {
        resultHTML += `<p>WiFi Price (${data.wifi_kind || 'None'}): $${result.wifi_price || 0}</p>`;
        resultHTML += `<p>Custom Build: $${result.custom_build_price || 0}</p>`;
        resultHTML += `<p>Bluetooth: $${result.bluetooth_price || 0}</p>`;
    }

    // GPU price and total
    resultHTML += result.gpu_price ? `<p>GPU Price: $${result.gpu_price}</p>` : '';
    resultHTML += `<h3>Total Price: $${result.total_price}</h3>`;

    document.getElementById('result').innerHTML = resultHTML;
    document.getElementById('transferToBuildSheet').style.display = 'inline-block';

    // Add event listener for transfer button
    document.getElementById('transferToBuildSheet').addEventListener('click', function() {
        const formData = new FormData(document.getElementById('priceCalcForm'));
        const osMapping = {
            'windows11': 'Windows 11',
            'linux': 'Linux Mint'
        };

        const wifiKindMapping = {
            '802.11-bgn': '802-bgn',
            'Dual Band': 'dual-band',
            'ac': 'ac',
            'ax': 'ax',
            'none': 'none-wireless'
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
            cpu: `${formData.get('kind') === 'intel' ? 'Intel' : 'AMD'} ${formData.get('model')}`,
            ram: formData.get('ram_size'),
            OS: osMapping[formData.get('os')] || formData.get('os'),
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
            is_laptop: formData.get('is_laptop') === 'yes',
            battery_capacity: formData.get('is_laptop') === 'yes' ? formData.get('battery_capacity') : '',
            diagonal_screen: formData.get('is_laptop') === 'yes' ? (formData.get('screen_size') || '') : '',
            wifi_kind: formData.get('wifi_kind'),
            bluetooth: formData.get('desktop_bluetooth') === 'yes' ? 'bluetooth-true' : 'bluetooth-false',
            touch_screen: formData.get('has_touch_screen') === 'yes' ? 'touch-screen-true' : 'touch-screen-false'
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
    document.getElementById('desktop-extra-options').style.display = isLaptop ? 'none' : 'block';
}

function toggleGpuOptions() {
    const hasGpu = document.getElementById('has_gpu').value === 'yes';
    document.getElementById('gpu-options').style.display = hasGpu ? '' : 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    toggleLaptopOptions(); 
});