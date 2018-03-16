#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "wificonfig.h"

#define mqtt_server "test.mosquitto.org"

/* ================================================== *
 * code to read the temperature out of the thermistor *
 * ================================================== */

#define ARRAY_SIZE(x) (sizeof(x) / sizeof(x[0]))

const float table[][2] = {
{177000,     -30.0},
{130370 ,   -25.0},
{97070  ,   -20.0},
{72929  ,   -15.0},
{55330  ,   -10.0},
{42315  ,   -5.0 },
{32650  ,   0.0  },
{25388  ,   5.0  },
{19900  ,   10.0 },
{15708  ,   15.0 },
{12490  ,   20.0 },
{10000   ,  25.0 },
{8057  ,  30.0 },
{6531  ,  35.0 },
{5327  ,  40.0 },
{4369  ,  45.0 },
{3603  ,  50.0 },
{2986  ,  55.0 },
{2488  ,  60.0 },
{2083  ,  65.0 },
{1752  ,  70.0 },
{1481  ,  75.0 },
{1258  ,  80.0 },
{1072 ,   85.0 },
{917.7  ,   90.0 },
{788.5  ,   95.0 },
{680.0  ,   100.0}
};


const int vcc = 3300;
const int R2 = 10000;

float read_temp() {
  int adc_value, board_mv;
  float r_sensor;
  int i;
  float t, t2, k;
  float t_range, r_range, r_delta, t_delta;

  adc_value = analogRead(A0);
  board_mv = adc_value * vcc / 1024;
  r_sensor = (vcc - board_mv) * R2 / board_mv;

  for (i = 0; i < ARRAY_SIZE(table); i++) {
    float r = table[i][0];
    t = table[i][1];
    if (r_sensor > r) {
      t_range = (t - table[i - 1][1]);
      r_range = (table[i - 1][0] - r);
      r_delta = r_sensor - r;
      k = r_delta / r_range;
      t2 = t - (t_range * k);
      return t2;
    }
  }
  return -1; /* error? */
}


/* ================================================== *
 * wifi, setup and main loop                          *
 * ================================================== */

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(9600);
  while(!Serial)
    ;
  Serial.println("I'm awake.");

  setup_wifi();
  client.setServer(mqtt_server, 1883); 
}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(wifi_ssid);

  WiFi.begin(wifi_ssid, wifi_password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  float temp = read_temp();
  Serial.printf("Temperature 2: %f\n", temp);
  client.publish("/antocuni/fridge", String(temp).c_str(), true);
  client.loop();
  Serial.println("Going into deep sleep for 1 minutes");
  ESP.deepSleep(60*1e6); // in us
  //ESP.deepSleep(60*5*1e6); // in us
  //ESP.deepSleep(5*1e6); // in us
    
}  

