import re

from flask import Flask, request, render_template, jsonify, redirect, url_for

app = Flask(__name__)

class Processor:
    def __init__(self, kind, model, user_price=None):
        """
        Initializes a Processor object with the given kind, model, and user_price.
        """
        self.kind = kind
        self.model = model
        self.core, self.generation = self.extract_core_and_gen()
        self.user_price = float(user_price) if user_price else 0  # Default to 0 if not provided

    def extract_core_and_gen(self):
        """
        Extracts the core type and generation from the model string.
        Handles cases where the model number includes a letter.
        """
        # Updated regex to capture the letter if it exists
        match = re.match(r'(i[357])[- ]?(\d{4,5}[A-Za-z]?)', self.model)
        if match:
            core = match.group(1)
            generation_str = match.group(2)

            # Extract generation based on the length of the model string
            if len(generation_str) == 4:  # No letter, older generation
                generation = int(generation_str[0])  # First digit as generation for 9th gen and below
            elif len(generation_str) == 5 and generation_str[-1].isalpha():
                generation = int(generation_str[:2])  # First two digits as generation for 10th gen and above
            else:
                generation = int(generation_str[:2])  # Handle regular cases without letters

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
            'i3': {2: 35, 3: 35, 4: 35, 5: 50, 6: 60, 7: 75, 8: 90, 9: 90, 10: 100, 11: 115, 12: 130},
            'i5': {2: 35, 3: 35, 4: 35, 5: 55, 6: 65, 7: 80, 8: 110, 9: 115, 10: 130, 11: 160, 12: 185},
            'i7': {2: 35, 3: 35, 4: 35, 5: 60, 6: 75, 7: 90, 8: 130, 9: 140, 10: 160, 11: 200, 12: 240}
        }

        core_prices = price_map.get(self.core.lower(), {})
        return core_prices.get(self.generation, 0)  # Default to 0 for unknown price


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
            return size * 1000  # Convert TB to GB
        return size  # Already in GB

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
        self.passmark_score = float(passmark_score) if passmark_score else 0  # Convert to float and default to 0

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
    """
    Renders the landing.html template.
    """
    return render_template('landing.html')

@app.route('/calculator')
def calculator():
    """
    Renders the calculator.html template for the calculator.
    """
    return render_template('calculator.html')

@app.route('/build-sheet')
def build_sheet():
    """
    Renders the PC inputs page without database context.
    """
    return render_template('inputs.html')

@app.route('/build-sheet/inputs')
def build_sheet_inputs():
    """
    Renders the inputs page for the build sheet.
    """
    return render_template('inputs.html')

@app.route('/build-sheet/results')
def build_sheet_results():
    """
    Renders the results page for the build sheet.
    """
    return render_template('results.html')

@app.route('/build-sheet/print', methods=['GET', 'POST'])
def build_sheet_print():
    """
    Renders the print page for the build sheet with form data.
    """
    if request.method == 'POST':
        form_data = request.form
        return render_template('print.html', 
                             database='pc',
                             results=form_data)
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
    user_price = float(data.get('amd_price', 0))  # Ensure user_price is a float

    processor = Processor(kind, model, user_price)
    processor_price = processor.processor_price()

    ram = Ram(ram_size)
    ram_price = ram.ram_price()

    total_storage_price = 0
    for storage in storage_details:
        storage_obj = Storage(storage['size'], storage['unit'], storage['kind'])
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

    itemized_prices = {
        'processor_price': processor_price,
        'ram_price': ram_price,
        'storage_price': total_storage_price,
        'os_price': os_price,
    }

    total_price = processor_price + ram_price + os_price + total_storage_price

    # Laptop-specific pricing
    if is_laptop:
        laptop_price = 30
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

        has_large_screen = data['has_large_screen']
        large_screen_price = 15 if has_large_screen else 0

        has_touch_screen = data['has_touch_screen']
        touch_screen_price = 15 if has_touch_screen else 0

        itemized_prices.update({
            'laptop_base_price': laptop_price,
            'battery_discount': battery_discount,
            'large_screen_price': large_screen_price,
            'touch_screen_price': touch_screen_price
        })

        total_price += laptop_price + battery_discount + large_screen_price + touch_screen_price

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
    gpu_type = data.get('gpu_type')
    passmark_score = float(data.get('passmark_score', 0))  # Ensure passmark_score is a float
    graphics = Graphics(has_gpu, passmark_score)
    gpu_price = round(graphics.gpu_price())

    itemized_prices['gpu_price'] = gpu_price
    total_price += gpu_price

    # RAM discount for 4GB
    if ram_size == 4:
        ram_discount = -5
        itemized_prices['ram_discount'] = ram_discount
        total_price += ram_discount

    # Custom build charge
    custom_build_price = 20 if data['custom_build'] else 0
    itemized_prices['custom_build_price'] = custom_build_price
    total_price += custom_build_price

    # Final rounding and returning the result
    total_price = round(total_price)
    itemized_prices['total_price'] = total_price

    return jsonify(itemized_prices)

@app.route('/save', methods=['POST'])
def save():
    """
    Handles form submission for saving the build sheet.
    """
    # Process the form data here
    form_data = request.form
    # Save the data to a database or perform other actions
    return jsonify({"message": "Build sheet saved successfully!"})

@app.errorhandler(500)
def internal_error(error):
    """
    Handles 500 internal server errors.
    """
    return render_template('error_500.html'), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
