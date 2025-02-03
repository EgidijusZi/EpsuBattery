# Dictionary to store test sequences for each battery type
test_sequences = {
    '301-3017': [
        'Step 1: Residual discharge 2A to 5V',
        'Step 2: Charge at 200mA for 16 hours. Voltage <7.8V',
        'Step 3: Capacity test at 4A until voltage exceeds 7.8V for 15 min',
        'Step 4: Rest time for 1 hour',
        'Step 5: Final charge at 200mA for 16 hours. Voltage <7.8V'
    ],
    'AD-301-3017': [
        'Step 1: Residual discharge 2A to 5V',
        'Step 2: Charge at 200mA for 16 hours. Voltage <7.8V',
        'Step 3: Capacity test at 4A until voltage exceeds 7.8V for 15 min',
        'Step 4: Rest time for 1 hour',
        'Step 5: Final charge at 200mA for 16 hours. Voltage <7.8V'
    ],
    'AD-301-3017 AMDT': [
        'Step 1: Residual discharge 2A to 5V',
        'Step 2: Charge at 220mA for 16 hours. Voltage <7.8V',
        'Step 3: Rest time for 1 hour',
        'Step 4: Capacity test at 4A until voltage exceeds 7.8V for 15 min',
        'Step 5: Final charge at 220mA for 16 hours. Voltage <7.8V'
    ],
    '301-3017 AMDT': [
        'Step 1: Residual discharge 2A to 5V',
        'Step 2: Charge at 220mA for 16 hours. Voltage <7.8V',
        'Step 3: Rest time for 1 hour',
        'Step 4: Capacity test at 4A until voltage exceeds 7.8V for 15 min',
        'Step 5: Final charge at 220mA for 16 hours. Voltage <7.8V'
    ],
    '301-2001': [
        'Step 1: Residual discharge 2A to 6V',
        'Step 2: Charge at 200mA for 16 hours. Voltage <9.3V',
        'Step 3: Rest time for 1 hour',
        'Step 4: Capacity test at 4A until voltage exceeds 6V for 15 min',
        'Step 5: Final charge at 200mA for 16 hours. Voltage <9.3V'
    ],
    'AQS-1000': [
        'Step 1: Residual discharge 2A to 6V',
        'Step 2: Charge at 200mA for 16 hours. Voltage <9.3V',
        'Step 3: Rest time for 1 hour',
        'Step 4: Capacity test at 4A until voltage exceeds 6V for 15 min',
        'Step 5: Final charge at 200mA for 16 hours. Voltage <9.3V'
    ],
    '301-2001 AMDT': [
        'Step 1: Residual discharge 2A to 6V',
        'Step 2: Charge at 220mA for 16 hours. Voltage <7.8V',
        'Step 3: Rest time for 1 hour',
        'Step 4: Capacity test at 4A until voltage exceeds 7.8V for 15 min',
        'Step 5: Final charge at 220mA for 16 hours. Voltage <7.8V'
    ],
    '301-1151': [
        'Step 1: Residual discharge 1A to 6V',
        'Step 2: Charge at 100mA for 16 hours. Voltage <9.3V',
        'Step 3: Rest time for 1 hour',
        'Step 4: Capacity test at 2A until voltage exceeds 5.7V for 15 min',
        'Step 5: Final charge at 100mA for 16 hours. Voltage <9.3V'
    ],
    'ABS-3127': [
        'Step 1: Residual discharge 1A to 6V',
        'Step 2: Charge at 100mA for 16 hours. Voltage <9.3V',
        'Step 3: Rest time for 1 hour',
        'Step 4: Capacity test at 2A until voltage exceeds 5.7V for 15 min',
        'Step 5: Final charge at 100mA for 16 hours. Voltage <9.3V'
    ],
    'AD-3127': [
        'Step 1: Residual discharge 1A to 6V',
        'Step 2: Charge at 100mA for 16 hours. Voltage <9.3V',
        'Step 3: Rest time for 1 hour',
        'Step 4: Capacity test at 2A until voltage exceeds 5.7V for 15 min',
        'Step 5: Final charge at 100mA for 16 hours. Voltage <9.3V'
    ],
    '726-0591-01': [
        'Step 1: Residual discharge 3.9 ohms to 8V',
        'Step 2: Charge at 210mA for 16 hours. Voltage <12V',
        'Step 3: Rest time for 1 hour',
        'Step 4: Capacity test at 3.9 ohms until voltage exceeds 8V for 20 min',
        'Step 5: Final charge at 210mA for 16 hours. Voltage <12V'
    ]
}
