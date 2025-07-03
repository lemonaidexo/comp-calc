import re
import sys
import json
import os

path = '/home/freegeeektc/mysite'
if path not in sys.path:
    sys.path.append(path)

from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

class Processor:
    def __init__(self, kind, model, user_price=None):
        """
        Initializes a Processor object with the given kind, model, and user_price.
        """
        self.kind = kind
        self.model = model
        self.core, self.generation = self.extract_core_and_gen()
        self.user_price = float(user_price) if user_price else 0
    def extract_core_and_gen(self):
        """
        Extracts the core type and generation from the model string.
        Handles cases where the model number includes a letter.
        """
        # Match i3/i5/i7, dash or space, then 4 or more digits, then optional letter(s)
        match = re.match(r'(i[357])[- ]?(\d{4,5})([A-Za-z]*)', self.model)
        if match:
            core = match.group(1)
            model_number = match.group(2)
            # If 5 digits, 10th gen or newer
            if len(model_number) == 5:
                generation = int(model_number[:2])
            # If 4 digits and starts with 10, 11, or 12, treat as 10th/11th/12th gen
            elif len(model_number) == 4 and model_number[:2] in {'10', '11', '12'}:
                generation = int(model_number[:2])
            else:
                generation = int(model_number[0])
            return core, generation
        return None, 0  # Handle the case where the core and generation are not found

    def processor_price(self):
        """
        Calculates the processor price based on the kind, core, and generation.
        """
        if self.kind.lower() == 'amd':
            print(f"AMD Processor selected with user price: {self.user_price}")
            return self.user_price
        if self.kind.lower() == 'intel':
            return self._intel_processor_price()
        
        return 0

    def _intel_processor_price(self):
        """
        Calculates the price for Intel processors based on core and generation.
        """
        price_map = {
            'i3': {2: 35, 3: 35, 4: 35, 5: 50, 6: 60, 7: 75, 8: 90, 9: 90, 10: 100, 11: 115, 12: 130},
            'i5': {2: 35, 3: 35, 4: 35, 5: 55, 6: 65, 7: 80, 8: 110, 9: 115, 10: 130, 11: 160, 12: 185},
            'i7': {2: 35, 3: 35, 4: 35, 5: 60, 6: 75, 7: 90, 8: 130, 9: 140, 10: 160, 11: 200, 12: 240}
        }

        core_prices = price_map.get(self.core.lower(), {})
        return core_prices.get(self.generation, 0)

class Ram:
    def __init__(self, ram_size):
        """
        Initializes a Ram object with the given ram_size.
        """
        self.ram_size = ram_size

    def ram_price(self):
        """
        Calculates the price of the RAM based on its size.
        """
        if self.ram_size == 4:
            return -5
        else:
            return (((self.ram_size - 8) / 4) * 5)


class Storage:
    def __init__(self, storage_size, storage_unit, storage_kind):
        """
        Initializes a Storage object with the given storage_size, storage_unit, and storage_kind.
        """
        self.storage_size = self.parse_storage_size(storage_size, storage_unit)
        self.storage_kind = storage_kind

    def parse_storage_size(self, storage_size, storage_unit):
        """
        Parses the storage size and unit and converts it to GB.
        """
        size = float(storage_size)
        unit = storage_unit.upper()
        if unit == 'TB':
            return size * 1000
        return size

    def storage_price(self):
        """
        Calculates the price of the storage based on its kind and size.
        """
        if self.storage_kind.lower() == 'hdd':
            return round((self.storage_size / 1000) * 5)
        else:
            return round((self.storage_size / 128) * 10)


class Graphics:
    def __init__(self, has_gpu, passmark_score=None):
        """
        Initializes a Graphics object with the given has_gpu and passmark_score.
        """
        self.has_gpu = has_gpu
        self.passmark_score = float(passmark_score) if passmark_score else 0

    def gpu_price(self):
        """
        Calculates the price of the GPU based on its type and passmark score.
        """
        if self.has_gpu:
            return self.passmark_score / 125 
        else:
            return 0


@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/build-sheet')
def build_sheet():
    return render_template('inputs.html')

@app.route('/build-sheet/print', methods=['GET', 'POST'])
def build_sheet_print():
    if request.method == 'POST':
        form_data = request.form
        return render_template('print.html', results=form_data)
    return render_template('print.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """
    Calculates the total price based on the user input and provides an itemized breakdown.
    """
    data = request.json

    kind = data['kind']
    model = data['model']
    ram_size = int(data['ram_size'])
    os = data['os']
    storage_details = data['storage']
    is_laptop = data['is_laptop']
    user_price = float(data.get('amd_price', 0))

    processor = Processor(kind, model, user_price)
    processor_price = processor.processor_price()

    ram = Ram(ram_size)
    ram_price = ram.ram_price()

    # Calculate storage prices
    total_storage_price = 0
    storage_prices = []
    for storage in storage_details:
        storage_obj = Storage(storage['size'], storage['unit'], storage['kind'])
        storage_price = storage_obj.storage_price()
        storage_prices.append(storage_price)
        total_storage_price += storage_price
        
    os_price = 15 if os.lower() == 'windows11' else 0

    itemized_prices = {
        'processor_price': processor_price,
        'ram_price': ram_price,
        'storage_price': total_storage_price,
        'storage_prices': storage_prices,
        'os_price': os_price,
    }

    total_price = processor_price + ram_price + os_price + total_storage_price

    # Laptop-specific pricing
    if is_laptop:
        battery_capacity = int(data['battery_capacity'])
        battery_discount = 0
        if battery_capacity < 20:
            battery_discount = -50
        elif battery_capacity < 40:
            battery_discount = -25
        elif battery_capacity < 60:
            battery_discount = -10
        elif battery_capacity < 90:
            battery_discount = -5

        # Fix screen size pricing
        screen_size_raw = data.get('screen_size', '').strip()
        if screen_size_raw:
            try:
                screen_size = float(screen_size_raw)
                large_screen_price = 15 if screen_size > 15.6 else 0
            except (ValueError, TypeError):
                screen_size = ''
                large_screen_price = 0
        else:
            screen_size = ''
            large_screen_price = 0

        has_touch_screen = data.get('has_touch_screen')
        if isinstance(has_touch_screen, bool):
            has_touch_screen = has_touch_screen
        else:
            has_touch_screen = str(has_touch_screen).lower() == 'yes'
        touch_screen_price = 15 if has_touch_screen else 0

        # Screen over 60hz
        screen_over_60hz = data.get('screen_over_60hz', False)
        if isinstance(screen_over_60hz, bool):
            screen_over_60hz = screen_over_60hz
        else:
            screen_over_60hz = str(screen_over_60hz).lower() == 'yes'
        hz_price = 20 if screen_over_60hz else 0

        # New: Screen resolution pricing
        screen_resolution = data.get('screen_resolution', 'below_1440')
        if screen_resolution == 'above_1440':
            resolution_price = 15
        elif screen_resolution == '4k':
            resolution_price = 20
        else:
            resolution_price = 0

        # Add to laptop add-ons total
        laptop_addon_total = (
            battery_discount +
            large_screen_price +
            touch_screen_price +
            hz_price +
            resolution_price
        )

        itemized_prices.update({
            'laptop_base_price': laptop_addon_total,
            'battery_discount': battery_discount,
            'large_screen_price': large_screen_price,
            'touch_screen_price': touch_screen_price,
            'hz_price': hz_price,
            'resolution_price': resolution_price
        })

        total_price += battery_discount + large_screen_price + touch_screen_price + hz_price + resolution_price

    # Desktop-specific pricing
    else:
        wifi_kind = data['wifi_kind']
        wifi_price = 0
        if wifi_kind:
            if wifi_kind.lower() == 'ac':
                wifi_price = 5
            elif wifi_kind.lower() == 'ax':
                wifi_price = 15

        desktop_bluetooth = data.get('desktop_bluetooth', False)
        bluetooth_price = 10 if desktop_bluetooth else 0

        itemized_prices.update({
            'wifi_price': wifi_price,
            'bluetooth_price': bluetooth_price
        })

        total_price += wifi_price + bluetooth_price

    # GPU Price
    has_gpu = data['has_gpu']
    passmark_score = float(data.get('passmark_score', 0))
    graphics = Graphics(has_gpu, passmark_score)
    gpu_price = round(graphics.gpu_price())

    itemized_prices['gpu_price'] = gpu_price
    total_price += gpu_price

    # Custom build charge
    custom_build_price = 20 if data['custom_build'] else 0
    itemized_prices['custom_build_price'] = custom_build_price
    total_price += custom_build_price

    # Final rounding and returning the result
    total_price = round(total_price)
    itemized_prices['total_price'] = total_price

    return jsonify(itemized_prices)

@app.route('/cpu-specs')
def cpu_specs():
    model = request.args.get('model', '').strip().lower().replace(' ', '').replace('_', '')
    json_path = os.path.join(app.root_path, 'intel_cpus.json')
    with open(json_path) as f:
        cpus = json.load(f)
    # Try exact match first
    for cpu in cpus:
        cpu_model = cpu.get('Model', '').strip().lower().replace(' ', '').replace('_', '')
        if cpu_model == model:
            return jsonify({
                "base_ghz": cpu.get("Base GHz"),
                "cores": cpu.get("Cores"),
                "threads": cpu.get("Threads")
            })
    # Try partial match if exact not found
    for cpu in cpus:
        cpu_model = cpu.get('Model', '').strip().lower().replace(' ', '').replace('_', '')
        if model in cpu_model:
            return jsonify({
                "base_ghz": cpu.get("Base GHz"),
                "cores": cpu.get("Cores"),
                "threads": cpu.get("Threads")
            })
    return jsonify({}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handles 500 internal server errors.
    """
    return render_template('error_500.html'), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)

