from flask import Flask, request, render_template, jsonify # type: ignore
import re

app = Flask(__name__)

class Processor:
    def __init__(self, kind, model):
        self.kind = kind
        self.model = model
        self.core, self.generation = self.extract_core_and_gen()

        if kind.lower() == 'amd':
            self.user_price = int(input("Enter the price of the AMD processor here: "))
        else:
            self.user_price = None

    def extract_core_and_gen(self):
        match = re.match(r'(i[357])[- ]?(\d{4})', self.model)
        if match:
            core = match.group(1)
            generation = int(match.group(2)[0]) #Extract the first digit as generation
            return core, generation
        return None, 0 #Handle the case where the core and generation are not found

    def processor_price(self):
        if self.kind.lower() == 'amd':
            return self.user_price
        #Calculates the price of the intel cpu based on the core and then generation of that core
        if self.kind.lower() == 'intel':
            if self.core.lower() == 'i3':
                if self.generation in [4, 5]:
                    return 40
                elif self.generation in [6, 7]:
                    return 55
                elif self.generation in [8, 9]:
                    return 90
                elif self.generation in [10, 11]:
                    return 130
                elif self.generation in [12, 13]:
                    return int(input("Enter the processor price: "))
            elif self.core.lower() == 'i5':
                if self.generation == 3:
                    return 35
                elif self.generation in [4, 5]:
                    return 50
                elif self.generation in [6, 7]:
                    return 75
                elif self.generation in [8, 9]:
                    return 110
                elif self.generation in [10, 11]:
                    return 160
                elif self.generation in [12, 13]:
                    return int(input("Enter the processor price: "))
            elif self.core.lower() == 'i7':
                if self.generation == 1:
                    return 25
                elif self.generation in [2, 3]:
                    return 45
                elif self.generation in [4, 5]:
                    return 65
                elif self.generation in [6, 7]:
                    return 100
                elif self.generation in [8, 9]:
                    return 130
                elif self.generation in [10, 11]:
                    return 200
                elif self.generation in [12, 13]:
                    return int(input("Enter the processor price: "))
        return 0

class Ram:
    def __init__(self, ram_size):
        self.ram_size = ram_size
    #Calculates the price of the ram based on if the ram is more than 4 GB
    def ram_price(self):
        if self.ram_size == 4:
            return -10
        else:
            return (((self.ram_size - 8) / 4) * 5)

class Storage:
    def __init__(self, storage_size_str, storage_kind):
        self.storage_size = self.parse_storage_size(storage_size_str)
        self.storage_kind = storage_kind

    def parse_storage_size(self, storage_size_str):
        match = re.match(r'(\d+)\s*(GB|TB)', storage_size_str, re.IGNORECASE)
        if match:
            size = int(match.group(1))
            unit = match.group(2).upper()
            if unit == 'TB':
                return size * 1000 # Convert TB to GB
            return size # Already in GB
        else:
            raise ValueError("Invalid storage size format. Use '500 GB' or '2 TB'.")

    def storage_price(self):
        if self.storage_kind.lower() == 'hdd':
            return round((self.storage_size / 1000) * 5)
        else:
            return round((self.storage_size / 128) * 10)

class Graphics:
    def __init__(self, has_gpu, gpu_type=None, passmark_score=None, user_price=None):
        self.has_gpu = has_gpu
        self.gpu_type = gpu_type
        self.passmark_score = passmark_score
        self.user_price = user_price

    def gpu_price(self):
        if not self.has_gpu:
            return 0
        if self.gpu_type.lower() == 'discrete' or self.gpu_type.lower() == 'amd radeon' or self.gpu_type.lower() == 'amd':
            return self.passmark_score / 125
        else:
            return self.user_price

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

    processor = Processor(kind, model)
    processor_price = processor.processor_price()

    ram = Ram(ram_size)
    ram_price = ram.ram_price()

    total_storage_price = 0
    for storage in storage_details:
        storage_obj = Storage(storage['size'], storage['kind'])
        total_storage_price += storage_obj.storage_price()

    def operating_system():
        if os.lower() in ['windows', 'windows 10', 'windows 11']:
            return 15
        else:
            return 0
        
    os_price = operating_system()

    total_price = processor_price + ram_price + os_price + total_storage_price

    if is_laptop:
        total_price += 30
        battery_capacity = int(data['battery_capacity'])
        if battery_capacity < 50:
            total_price -= 50
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
    passmark_score = data.get('passmark_score')
    graphics = Graphics(has_gpu, gpu_type, passmark_score)
    gpu_price = graphics.gpu_price()

    total_price += gpu_price

    if ram_size == 4:
        total_price -= 10

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