#include <painlessMesh.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <WiFiManager.h>
#include <ESPAsyncWebServer.h>
#include <WiFi.h>
#include <time.h>

#define MESH_PREFIX "ESP32Mesh"
#define MESH_PASSWORD "meshPassword"
#define MESH_PORT 5555
#define THINGSPEAK_SERVER "api.thingspeak.com"

// Map node IDs to ThingSpeak Write API Keys
const uint32_t ROOT_NODE_ID = 3814450389; // Replace with actual root node ID from Serial Monitor
const uint32_t NON_ROOT_ESP32_ID = 4182051057; // Replace with non-root ESP32 ID
const uint32_t ESP8266_ID = 2829282566; // Replace with ESP8266 ID
const char* API_KEYS[] = {
  "NWMLJPCEIE93YXBV", // Root ESP32 Write API Key
  "594EERCK06RPW73A", // Non-root ESP32 Write API Key
  "JKQBSZ5YJ862N7UH" // ESP8266 Write API Key
};

#define DHT_PIN 27      // Digital pin for DHT11
#define WATER_PIN 35    // Digital pin for water sensor
#define DHT_TYPE DHT11  // DHT11 sensor type

painlessMesh mesh;
AsyncWebServer server(80);
DHT dht(DHT_PIN, DHT_TYPE);
HTTPClient http;
WiFiManager wifiManager;
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
  int value = digitalRead(WATER_PIN); // HIGH (1) = water detected
  Serial.printf("DEBUG: Water sensor raw value: %d\n", value);
  return value;
}

void sendToThingSpeak(uint32_t nodeId, float temperature, float humidity, int waterPresence, String timestamp) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("DEBUG: WiFi not connected, skipping ThingSpeak POST");
    return;
  }

  const char* apiKey = nullptr;
  if (nodeId == ROOT_NODE_ID) apiKey = API_KEYS[0];
  else if (nodeId == NON_ROOT_ESP32_ID) apiKey = API_KEYS[1];
  else if (nodeId == ESP8266_ID) apiKey = API_KEYS[2];
  else {
    Serial.println("DEBUG: Unknown node ID: " + String(nodeId));
    return;
  }

  Serial.println("DEBUG: Root node, WiFi connected, sending data to ThingSpeak for node " + String(nodeId));
  String url = String("http://") + THINGSPEAK_SERVER + "/update";
  Serial.println("DEBUG: HTTP begin URL: " + url);
  http.begin(url);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  String postData = "api_key=" + String(apiKey) +
                    "&field1=" + String(temperature, 1) +
                    "&field2=" + String(humidity, 1) +
                    "&field6=" + String(waterPresence) +
                    "&field4=" + timestamp;
  Serial.println("DEBUG: Sending POST for node " + String(nodeId) + ": " + postData);
  int httpCode = http.POST(postData);
  if (httpCode <= 0) {
    Serial.println("DEBUG: HTTP POST failed for node " + String(nodeId) + ", error: " + http.errorToString(httpCode));
  }
  Serial.printf("DEBUG: ThingSpeak HTTP for node %u: %d\n", nodeId, httpCode);
  http.end();
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

  DynamicJsonDocument doc(256);
  doc["nodeId"] = mesh.getNodeId();
  doc["humidity"] = humidity;
  doc["temperature"] = temperature;
  doc["waterPresence"] = waterPresence;
  doc["timestamp"] = timestamp;
  String json;
  serializeJson(doc, json);

  Serial.println("DEBUG: Broadcasting JSON: " + json);
  mesh.sendBroadcast(json);

  if (mesh.isRoot()) {
    sendToThingSpeak(mesh.getNodeId(), temperature, humidity, waterPresence, timestamp);
  }
  Serial.println("DEBUG: Exiting sendSensorData()");
}

void receivedCallback(uint32_t from, String &msg) {
  Serial.printf("DEBUG: Received from %u: %s\n", from, msg.c_str());
  if (!mesh.isRoot()) return;

  DynamicJsonDocument doc(256);
  DeserializationError error = deserializeJson(doc, msg);
  if (error) {
    Serial.println("DEBUG: Failed to parse received JSON: " + String(error.c_str()));
    return;
  }

  uint32_t nodeId = doc["nodeId"] | 0;
  float temperature = doc["temperature"] | -1;
  float humidity = doc["humidity"] | -1;
  int waterPresence = doc["waterPresence"] | 0;
  String timestamp = doc["timestamp"] | "";

  Serial.printf("DEBUG: Parsed data from %u: Temp=%.1f°C, Hum=%.1f%%, Water=%d, Timestamp=%s\n",
                nodeId, temperature, humidity, waterPresence, timestamp.c_str());

  sendToThingSpeak(nodeId, temperature, humidity, waterPresence, timestamp);
}

Task taskSendData(TASK_SECOND * 60, TASK_FOREVER, &sendSensorData); // 60 seconds

void setup() {
  Serial.begin(115200);
  pinMode(WATER_PIN, INPUT);
  dht.begin();
  delay(2000); // Allow DHT11 to stabilize
  
  Serial.println("DEBUG: Connecting to WiFi");
  wifiManager.autoConnect("ESP32ConfigAP");
  Serial.println("DEBUG: Connected to WiFi");
  Serial.print("DEBUG: IP Address: ");
  Serial.println(WiFi.localIP());

  initTime();
  Serial.println("DEBUG: Waiting for NTP sync...");
  delay(5000);

  mesh.setDebugMsgTypes(ERROR | STARTUP);
  mesh.init(MESH_PREFIX, MESH_PASSWORD, &userScheduler, MESH_PORT);
  mesh.setRoot(true); // Root node

  mesh.onReceive(&receivedCallback);

  server.on("/topology", HTTP_GET, [](AsyncWebServerRequest *request) {
    Serial.println("DEBUG: Handling /topology request");
    DynamicJsonDocument doc(256);
    doc["nodeId"] = mesh.getNodeId();
    doc["humidity"] = dht.readHumidity();
    doc["temperature"] = dht.readTemperature();
    doc["waterPresence"] = readWaterSensor();
    doc["timestamp"] = readWaterSensor() ? getTimestamp() : "";
    String json;
    serializeJson(doc, json);
    request->send(200, "application/json", json);
  });
  server.begin();

  userScheduler.addTask(taskSendData);
  taskSendData.enable();
  Serial.println("DEBUG: sendSensorData task enabled");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("DEBUG: WiFi disconnected, reconnecting...");
    WiFi.reconnect();
    delay(5000);
  }
  mesh.update();
  userScheduler.execute();
}