import paho.mqtt.client as mqtt

# Define the callback function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    if msg.topic == "moot/mode":
        mode = msg.payload.decode()


# MQTT setup
mqtt_broker = "localhost"
mqtt_topic = ["moot/mode"]

client = mqtt.Client()
client.on_message = on_message

client.connect(mqtt_broker, 1883, 60)
for t in mqtt_topic:
    client.subscribe(t)

# Start the MQTT client loop
print("loading complete, looping forever")
client.loop_forever()
