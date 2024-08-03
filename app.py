from flask import Flask, request, render_template, jsonify  # type: ignore
import re

app = Flask(__name__)

class Processor:
    def __init__(self, kind, model, user_price=None):
        self.kind = kind
        self.model = model
        self.core, self.generation = self.extract_core_and_gen()
        self.user_price = float(user_price) if user_price else 0  # Default to 0 if not provided

    def extract_core_and_gen(self):
        """
        Extracts the core type and generation from the model string.
        """
        match = re.match(r'(i[357])[- ]?(\d{4,5})', self.model)
        if match:
            core = match.group(1)
            generation_str = match.group(2)
            if len(generation_str) == 4:
                generation = int(generation_str[0])  # Extract the first digit as generation for 9th gen and below
            else:
                generation = int(generation_str[:2])  # Extract the first two digits as generation for 10th gen and above
            return core, generation
        return None, 0  # Handle the case where the core and generation are not found

    def processor_price(self):
        """
        Calculates the processor price based on the kind, core, and generation.
        """
        if self.kind.lower() == 'amd':
            print(f"AMD Processor selected with user price: {self.user_price}")
            return self.user_price  # Return the user price directly

        if self.kind.lower() == 'intel':
            return self._intel_processor_price()
        
        return 0  # Default to 0 for unknown kind

    def _intel_processor_price(self):
        """
        Calculates the price for Intel processors based on core and generation.
        """
        price_map = {
            'i3': {3: 25, 4: 40, 5: 40, 6: 55, 7: 55, 8: 90, 9: 90, 10: 130, 11: 130, 12: 0, 13: 0},
            'i5': {3: 35, 4: 50, 5: 50, 6: 75, 7: 75, 8: 110, 9: 110, 10: 160, 11: 160, 12: 0, 13: 0},
            'i7': {1: 25, 2: 45, 3: 45, 4: 65, 5: 65, 6: 100, 7: 100, 8: 130, 9: 130, 10: 200, 11: 200, 12: 0, 13: 0}
        }

        core_prices = price_map.get(self.core.lower(), {})
        return core_prices.get(self.generation, 0)  # Default to 0 for unknown price


class Ram:
    def __init__(self, ram_size):
        self.ram_size = ram_size

    def ram_price(self):
        """
        Calculates the price of the RAM based on its size.
        """
        if self.ram_size == 4:
            return -10
        else:
            return (((self.ram_size - 8) / 4) * 5)


class Storage:
    def __init__(self, storage_size_str, storage_kind):
        self.storage_size = self.parse_storage_size(storage_size_str)
        self.storage_kind = storage_kind

    def parse_storage_size(self, storage_size_str):
        """
        Parses the storage size string and converts it to GB.
        """
        match = re.match(r'(\d+)\s*(GB|TB)', storage_size_str, re.IGNORECASE)
        if match:
            size = int(match.group(1))
            unit = match.group(2).upper()
            if unit == 'TB':
                return size * 1000  # Convert TB to GB
            return size  # Already in GB
        else:
            raise ValueError("Invalid storage size format. Use '500 GB' or '2 TB'.")

    def storage_price(self):
        """
        Calculates the price of the storage based on its kind and size.
        """
        if self.storage_kind.lower() == 'hdd':
            return round((self.storage_size / 1000) * 5)
        else:
            return round((self.storage_size / 128) * 10)


class Graphics:
    def __init__(self, has_gpu, gpu_type=None, passmark_score=None, user_price=None):
        self.has_gpu = has_gpu
        self.gpu_type = gpu_type
        self.passmark_score = float(passmark_score) if passmark_score else 0  # Convert to float
        self.user_price = user_price

    def gpu_price(self):
        """
        Calculates the price of the GPU based on its type and passmark score.
        """
        if not self.has_gpu:
            return 0
        if self.gpu_type.lower() in ['discrete', 'amd radeon', 'amd']:
            return self.passmark_score / 125
        else:
            return self.user_price if self.user_price else 0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json

    kind = data['kind']
    model = data['model']
    ram_size = int(data['ram_size'])
    os = data['os']
    storage_details = data['storage']
    is_laptop = data['is_laptop']
    user_price = float(data.get('amd_price', 0))  # Ensure user_price is a float

    processor = Processor(kind, model, user_price)
    processor_price = processor.processor_price()

    ram = Ram(ram_size)
    ram_price = ram.ram_price()

    total_storage_price = 0
    for storage in storage_details:
        storage_obj = Storage(storage['size'], storage['kind'])
        total_storage_price += storage_obj.storage_price()

    def operating_system():
        """
        Determines the price of the operating system.
        """
        if os.lower() == 'windows':
            return 15
        else:
            return 0
        
    os_price = operating_system()

    total_price = processor_price + ram_price + os_price + total_storage_price

    if is_laptop:
        total_price += 30
        battery_capacity = int(data['battery_capacity'])
        if battery_capacity < 20:
            total_price -= 50
        elif battery_capacity < 40:
            total_price -= 25
        elif battery_capacity < 60:
            total_price -= 10
        elif battery_capacity < 90:
            total_price -= 5

        has_large_screen = data['has_large_screen']
        has_touch_screen = data['has_touch_screen']

        if has_large_screen:
            total_price += 15
        if has_touch_screen:
            total_price += 15
    else:
        desktop_wifi = data.get('desktop_wifi', False)
        if desktop_wifi:
            wifi_kind = data['wifi_kind']
            if wifi_kind.lower() in ['ac', 'n/ac']:
                total_price += 5
            if wifi_kind.lower() == 'ax':
                total_price += 10

    has_gpu = data['has_gpu']
    gpu_type = data.get('gpu_type')
    passmark_score = float(data.get('passmark_score', 0))  # Ensure passmark_score is a float
    graphics = Graphics(has_gpu, gpu_type, passmark_score)
    gpu_price = round(graphics.gpu_price())

    total_price += gpu_price

    if ram_size == 4:
        total_price -= 5

    if data['custom_build']:
        total_price += 20  # Add custom build charge

    total_price = round(total_price)

    return jsonify({
        'processor_price': processor_price,
        'ram_price': ram_price,
        'storage_price': total_storage_price,
        'os_price': os_price,
        'gpu_price': gpu_price,
        'total_price': total_price
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)