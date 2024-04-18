import asyncio
from bleak import BleakScanner
from bleak import BleakClient

# ---- Device discovery ----
async def discover_devices():
    """Asynchronous BLE device discovery. Returns a list of found devices (name, address)."""
    try:
        devices = await BleakScanner.discover()
        return [(d.name, d.address) for d in devices if d.name]
    except Exception as e:
        print(f"Error discovering devices: {e}")
        return []
    
# ---- Device connection ----
async def connect_to_device(address):
    """Connect to a BLE device with the given address."""
    client = BleakClient(address)
    try:
        await client.connect()
        if client.is_connected:
            print(f"Connected to {address}")
            return client
        else:
            print(f"Failed to connect to {address}")
            return None
    except Exception as e:
        print(f"Error connecting to {address}: {e}")
        return None


# ---- Device disconnection ----
async def disconnect_from_device(client):
    """Disconnect from a BLE device."""
    try:
        await client.disconnect()
        print("Disconnected.")
    except Exception as e:
        print(f"Error disconnecting: {e}")


# test
async def run(client, address, motor_direction, motor_enable, motor_speed, angle_delta, UUID):
    # Generate a random integer
    data = bytearray([motor_direction, motor_enable, motor_speed])
    data += angle_delta.to_bytes(2, byteorder='big')

    # Convert integer to bytes and write to the characteristic
    await client.write_gatt_char(UUID, data)
    print("Write completed.")