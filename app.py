from flask import Flask, request, render_template # type: ignore
import re
# testing


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
            generation = int(match.group(2)[0])
            return core, generation
        return None, 0

    def processor_price(self):
        if self.kind.lower() == 'amd':
            return self.user_price

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
                return size * 1000
            return size
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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        kind = request.form.get("kind")
        model = request.form.get("model")
        ram_size = int(request.form.get("ram_size"))
        os = request.form.get("os")
        is_laptop = request.form.get("is_laptop") == "yes"

        processor = Processor(kind, model)
        processor_price = processor.processor_price()

        ram = Ram(ram_size)
        ram_price = ram.ram_price()

        def operating_system():
            if os.lower() in ['windows', 'windows 10', 'windows 11']:
                return 15
            else:
                return 0
        
        os_price = operating_system()

        total_price = processor_price + ram_price + os_price

        if is_laptop:
            total_price += 30
            battery_capacity = int(request.form.get("battery_capacity"))
            if battery_capacity < 50:
                total_price -= 50
            elif battery_capacity < 90:
                total_price -= 5

            has_large_screen = request.form.get("has_large_screen") == "yes"
            has_touch_screen = request.form.get("has_touch_screen") == "yes"

            if has_large_screen:
                total_price += 15
            if has_touch_screen:
                total_price += 15
        else:
            has_wifi = request.form.get("has_wifi") == "yes"
            if has_wifi:
                wifi_kind = request.form.get("wifi_kind")
                if wifi_kind in ['ac', 'n/ac']:
                    total_price += 5
                elif wifi_kind == 'ax':
                    total_price += 10

        has_gpu = request.form.get("has_gpu") == "yes"
        if has_gpu:
            gpu_type = request.form.get("gpu_type")
            if gpu_type in ['discrete', 'amd radeon']:
                passmark_score = int(request.form.get("passmark_score"))
                graphics = Graphics(has_gpu, gpu_type, passmark_score=passmark_score)
            else:
                user_price = int(request.form.get("gpu_price"))
                graphics = Graphics(has_gpu, gpu_type, user_price=user_price)
        else:
            graphics = Graphics(has_gpu)

        gpu_price = graphics.gpu_price()

        num_drives = int(request.form.get("num_drives"))
        if num_drives > 4:
            return "A maximum of 4 drives (2 SSDs and 2 HDDs) are allowed."

        total_storage_price = 0
        ssd_count = 0
        hdd_count = 0

        for i in range(1, num_drives + 1):
            storage_size = request.form.get(f"storage_size_{i}")
            storage_kind = request.form.get(f"storage_kind_{i}")

            if storage_kind.lower() == 'hdd':
                if hdd_count >= 2:
                    continue
                hdd_count += 1
            else:
                if ssd_count >= 2:
                    continue
                ssd_count += 1

            storage = Storage(storage_size, storage_kind)
            total_storage_price += storage.storage_price()

        total_price += total_storage_price + gpu_price
        total_price = round(total_price)

        return render_template(
            "result.html",
            processor_price=processor_price,
            ram_price=ram_price,
            total_storage_price=total_storage_price,
            gpu_price=gpu_price,
            os_price=os_price,
            total_price=total_price,
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
