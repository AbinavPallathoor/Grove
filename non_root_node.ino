#include <painlessMesh.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <time.h>

#if defined(ESP32)
  #include <WiFi.h>
  #define DHT_PIN 27    // ESP32: GPIO 27
  #define WATER_PIN 35  // ESP32: GPIO 35
#else
  #include <ESP8266WiFi.h>
  #define DHT_PIN 14    // ESP8266: GPIO 14 (D5)
  #define WATER_PIN A0  // ESP8266: A0
#endif

#define MESH_PREFIX "ESP32Mesh"
#define MESH_PASSWORD "meshPassword"
#define MESH_PORT 5555
#define DHT_TYPE DHT11  // DHT11 sensor type

painlessMesh mesh;
DHT dht(DHT_PIN, DHT_TYPE);
Scheduler userScheduler;

void initTime() {
  Serial.println("DEBUG: Initializing NTP");
  configTime(0, 0, "pool.ntp.org");
  setenv("TZ", "IST-5:30", 1); // India Standard Time (UTC+5:30)
  tzset();
}

String getTimestamp() {
  Serial.println("DEBUG: Getting timestamp");
  time_t now;
  struct tm timeinfo;
  time(&now);
  localtime_r(&now, &timeinfo);
  char buf[20];
  strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &timeinfo);
  return String(buf);
}

int readWaterSensor() {
  Serial.println("DEBUG: Reading water sensor");
  #if defined(ESP32)
    int value = digitalRead(WATER_PIN); // HIGH (1) = water detected
    Serial.printf("DEBUG: Water sensor raw value: %d\n", value);
    return value;
  #else
    int adcValue = analogRead(WATER_PIN); // 0-1023
    int value = (adcValue > 512) ? 1 : 0; // Threshold at ~0.5V
    Serial.printf("DEBUG: Water sensor raw value: %d, processed: %d\n", adcValue, value);
    return value;
  #endif
}

void sendSensorData() {
  Serial.println("DEBUG: Entering sendSensorData()");
  Serial.printf("DEBUG: Free Heap: %d\n", ESP.getFreeHeap());

  Serial.println("DEBUG: Reading DHT11");
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  Serial.printf("DEBUG: Raw Temp=%.1f°C, Raw Hum=%.1f%%\n", temperature, humidity);

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("DEBUG: Invalid DHT11 readings, retrying...");
    delay(1000);
    humidity = dht.readHumidity();
    temperature = dht.readTemperature();
    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("DEBUG: Invalid DHT11 readings, setting to -1");
      humidity = -1;
      temperature = -1;
    }
  }

  int waterPresence = readWaterSensor();
  String timestamp = waterPresence ? getTimestamp() : "";
  Serial.printf("DEBUG: Temp=%.1f°C, Hum=%.1f%%, Water=%d, Timestamp=%s\n",
                temperature, humidity, waterPresence, timestamp.c_str());

  DynamicJsonDocument doc(200); // Reduced from 256
  doc["nodeId"] = mesh.getNodeId();
  doc["humidity"] = humidity;
  doc["temperature"] = temperature;
  doc["waterPresence"] = waterPresence;
  doc["timestamp"] = timestamp;
  String json;
  serializeJson(doc, json);

  Serial.println("DEBUG: Broadcasting JSON: " + json);
  mesh.sendBroadcast(json);
  Serial.println("DEBUG: Exiting sendSensorData()");
}

Task taskSendData(TASK_SECOND * 60, TASK_FOREVER, &sendSensorData); // 60 seconds

void setup() {
  Serial.begin(115200);
  #if defined(ESP32)
    pinMode(WATER_PIN, INPUT);
  #endif
  dht.begin();
  delay(2000); // Allow DHT11 to stabilize

  initTime();
  Serial.println("DEBUG: Waiting for NTP sync...");
  delay(5000);

  mesh.setDebugMsgTypes(ERROR | STARTUP);
  mesh.init(MESH_PREFIX, MESH_PASSWORD, &userScheduler, MESH_PORT);
  mesh.setRoot(false); // Non-root node

  mesh.onReceive([](uint32_t from, String &msg) {
    Serial.printf("DEBUG: Received from %u: %s\n", from, msg.c_str());
  });

  userScheduler.addTask(taskSendData);
  taskSendData.enable();
  Serial.println("DEBUG: sendSensorData task enabled");
}

void loop() {
  mesh.update();
  userScheduler.execute();
}