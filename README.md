# 598_EverGreen

## Local Setup Instructions

Follow these steps to set up the project locally.

### Step 1: Activate the Virtual Environment

Ensure that the virtual environment is activated before running the program. Use this command:

```bash
source env/bin/activate
```

### Step 2: Run the Program
Execute the main script using Python 3. Make sure you are in the project directory where main.py is located:

```bash
python3 main.py
```

### Step 3: Runing front end
```bash
cd FrontEnd
cd Public
http-server
```

### Step 4: Hosting Backend 
```bash
cd FrontEnd
node server.js
```


### Step 5: To use cv 
```bash
libcamera-jpeg -o plant.jpg
source myenv/bin/activate
python project_main.py
```


### Additional Notes:

- **Camera Capture**: currently the code is design to capture a photo and save it into the same directory and with timestamp in the file name.
