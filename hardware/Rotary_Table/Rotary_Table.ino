#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <Stepper.h>

// stepper setup
#define IN1 33 // GPIO33
#define IN2 25 // GPIO
#define IN3 26
#define IN4 27
int stepper_steps = 2048; // 28byj-48
int drive_gear_teeth = 10;
int ring_gear_teeth = 80;
float gear_ratio = ring_gear_teeth / drive_gear_teeth;
float steps_per_rev = stepper_steps * gear_ratio;

Stepper mainStepper(stepper_steps, IN1, IN3, IN2, IN4);

// UUIDs for BLE service and characteristic
#define SERVICE_UUID        "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "abcdef01-2345-6789-1234-56789abcdef0"

BLECharacteristic *pCharacteristic;

uint8_t motorDirection = 0;
uint8_t motorOnOff = 1;
uint8_t motorSpeed = 0;
uint16_t angleDelta = 0;

int maxMotorSpeed = 15;
int minMotorSpeed = 1;

class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
      std::string value = pCharacteristic->getValue();

      if (value.length() >= 5) {
        Serial.println("*********");
        Serial.println("Received Data:");

        // Parsing the bytes
        motorDirection = value[0];
        motorOnOff = value[1];
        motorSpeed = value[2];
        // Combine the 4th and 5th bytes into a 16-bit unsigned integer
        angleDelta = (uint8_t)value[3] << 8 | (uint8_t)value[4];

        // Print the parsed values to the Serial Monitor
        Serial.print("Motor Direction: "); Serial.println(motorDirection ? "CCW" : "CW");
        Serial.print("Motor On/Off: "); Serial.println(motorOnOff ? "On" : "Off");
        Serial.print("Motor Speed: "); Serial.println(motorSpeed);
        Serial.print("Angle Delta: "); Serial.println(angleDelta);
        Serial.println();
        Serial.println("*********");
      }
    }
};

class ServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      Serial.println("Client connected");
    };

    void onDisconnect(BLEServer* pServer) {
      Serial.println("Client disconnected, restarting advertising");
      BLEDevice::startAdvertising(); // Ensure we're advertising so another client can connect
    }
};

void setup() {
  Serial.begin(115200);
  BLEDevice::init("Rotary_Table");

  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_WRITE
                    );

  pCharacteristic->setCallbacks(new MyCallbacks());
  pCharacteristic->setValue("Hello World");
  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  
  pServer->setCallbacks(new ServerCallbacks());

  Serial.println("Characteristic defined! Ready to receive data.");

  // STEPPER setup
  mainStepper.setSpeed(15);
}

void loop() {
  int speed = scale_speed(motorSpeed);
  setTableSpeed(speed);

  int dir_val;
  if (motorDirection == 0) {
    dir_val = 1;
  } else {
    dir_val = -1;
  }

  if (motorOnOff == 1) {
    if (angleDelta > 0) {
      if (angleDelta > 1) {
        mainStepper.step(dir_val * 90);
        angleDelta -= 2;
      } else {
        mainStepper.step(dir_val * 45);
        angleDelta -= 1;
      }
      if (angleDelta == 0) {
        motorOnOff = 0;
      }
    } else if (motorSpeed > 0) {
      mainStepper.step(dir_val * 100); 
    }
  } else {
    delay(10);
  }
}

void setTableSpeed(int i) {
  mainStepper.setSpeed(i);
}

int scale_speed(uint8_t speed) {
  float frac = float(speed) / 100;
  float diff = float(maxMotorSpeed - minMotorSpeed);
  return int( diff * frac + minMotorSpeed);
}
