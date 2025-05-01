- To make changes to the program, use the following steps.

# How to Change Price Calculations in the Computer Calculator

This guide will help you update how prices are calculated for Intel processors, RAM, GPU, and storage. You will be editing the file `app.py`.

---

## 1. Open the Code

1. Open the project folder in Visual Studio Code (VS Code).
2. In the file list, find and open `app.py`.

---

## 2. Change Intel Processor Price

- **Where to look:**  
  Search for `class Processor` in `app.py`.
- **What to change:**  
  The Intel processor prices are set in a table called `price_map` inside the `_intel_processor_price` method.

**Example:**
```python
def _intel_processor_price(self):
    price_map = {
        'i3': {2: 35, 3: 35, 4: 35, 5: 50, ...},
        'i5': {2: 35, 3: 35, 4: 35, 5: 55, ...},
        'i7': {2: 35, 3: 35, 4: 35, 5: 60, ...}
    }
    ...
```

- **How to change:**  
  Change the numbers in the `price_map` to your desired prices.  
  For example, to make 10th gen i5 $150:
  ```python
  'i5': {10: 150, ...}
  ```
  
---

## 3. Change RAM Price

- **Where to look:**  
  Search for `class Ram` in `app.py`.
- **What to change:**  
  The method `ram_price` sets the price based on RAM size.

**Example:**
```python
def ram_price(self):
    if self.ram_size == 4:
        return -5
    else:
        return (((self.ram_size - 8) / 4) * 5)
```

- **How to change:**  
  - Change `-5` to adjust the discount for 4GB RAM.
  - Change the formula to adjust how other RAM sizes are priced.

---

## 4. Change GPU Price

- **Where to look:**  
  Search for `class Graphics` in `app.py`.
- **What to change:**  
  The method `gpu_price` sets the price based on Passmark score.

**Example:**
```python
def gpu_price(self):
    if self.has_gpu:
        return self.passmark_score / 125 
    else:
        return 0
```

- **How to change:**  
  - Change `125` to a different number to make GPUs more or less expensive.
  - You can also add more logic if you want to price by GPU type.

---

## 5. Change Storage Price

- **Where to look:**  
  Search for `class Storage` in `app.py`.
- **What to change:**  
  The method `storage_price` sets the price based on size and type.

**Example:**
```python
def storage_price(self):
    if self.storage_kind.lower() == 'hdd':
        return round((self.storage_size / 1000) * 5)
    else:
        return round((self.storage_size / 128) * 10)
```

- **How to change:**  
  - Change `5` to adjust the price per 1TB HDD.
  - Change `10` to adjust the price per 128GB SSD/NVMe.

---

## 6. Save and Rebuild

1. **Save** your changes in VS Code.
2. **Rebuild** the project.  
   In your terminal, run:
   ```sh
   ./rebuild.sh
   ```
   Or use the `rebuild` command as described in the [README.md](README.md).

---

## 7. Test Your Changes

- Go to the calculator in your browser.
- Enter specs and check if the prices are calculated as you expect.

---