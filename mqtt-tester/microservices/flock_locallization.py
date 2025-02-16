# Callback per la ricezione dei messaggi
def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode("utf-8"))
    message_descriptor = MessageDescriptor(**payload)

    print(f"📥 Received message on {message.topic}: {payload}")

    # Salvataggio dati
    if "gps" in message.topic:
        gps_data[message.topic] = message_descriptor.value
    elif "image_processing" in message.topic:
        image_processing_data[message.topic] = message_descriptor.value

    # Se ho tutti i dati, calcolo la posizione del gregge
    if len(gps_data) == 3 and len(image_processing_data) == 3:
        # Passa il timestamp a calculate_flock_position
        timestamp = payload.get("timestamp", None)
        calculate_flock_position(timestamp)

# **Calcolo della posizione del gregge**
def calculate_flock_position(timestamp):
    global gps_data, image_processing_data

    # Estraggo le coordinate GPS in lat/lon
    lat_lon_positions = np.array([
        [gps_data[gps_topics[0]]["latitude"], gps_data[gps_topics[0]]["longitude"]],
        [gps_data[gps_topics[1]]["latitude"], gps_data[gps_topics[1]]["longitude"]],
        [gps_data[gps_topics[2]]["latitude"], gps_data[gps_topics[2]]["longitude"]]
    ])

    # Prendo il primo drone come riferimento
    lat_ref, lon_ref = lat_lon_positions[0]

    # Converto GPS → (x, y)
    gps_positions = np.array([
        gps_to_cartesian(lat_lon_positions[i][0], lat_lon_positions[i][1], lat_ref, lon_ref)
        for i in range(3)
    ])

    # Estraggo le distanze dal centro del gregge (fornite dall'image processing)
    distances = np.array([
        image_processing_data[image_processing_topics[0]]["distance"],
        image_processing_data[image_processing_topics[1]]["distance"],
        image_processing_data[image_processing_topics[2]]["distance"]
    ])

    # **Trilaterazione (media pesata)**
    weights = 1 / distances
    flock_x = np.sum(gps_positions[:, 0] * weights) / np.sum(weights)
    flock_y = np.sum(gps_positions[:, 1] * weights) / np.sum(weights)
    flock_z = 0  # Il gregge è sempre a terra

    flock_position = {
        "x": flock_x,
        "y": flock_y,
        "z": flock_z
    }

    # Debugging: stampo il risultato prima di pubblicarlo
    print(f"📌 Calculated flock position: {flock_position}")

    # **Pubblica la posizione del gregge**
    if timestamp is not None:
        payload_string_flock = MessageDescriptor(
            int(timestamp), "FLOCK_POSITION", flock_position
        ).to_json()
    
        mqtt_client.publish("device/flock/position", payload_string_flock)
        print(f"📤 Published to 'device/flock/position': {payload_string_flock}")
    else:
        print("⚠️ Missing timestamp, unable to publish flock position.")

    # Svuota i dati per il prossimo ciclo
    gps_data.clear()
    image_processing_data.clear()
