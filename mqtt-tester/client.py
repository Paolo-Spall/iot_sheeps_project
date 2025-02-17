#!/usr/bin/python3

import requests

gateway_url = "http://127.0.0.1:7072/"
gateway_control_url = "http://127.0.0.1:7072/gateway/controls/mission-points"



response = requests.get(gateway_url)

response = requests.put(gateway_control_url, 
                        json={"mission_type": "grazing",
                            "mission_points": [[0,0,0], [1,2,3]]},)

print()
print("Response status code:", response.status_code)
print(response.content)
print()

# uuid = input("Enter the id to get that agent:")

# response = requests.get(url_prefix+f"/agents/{uuid}")

# print()
# print("Response status code:", response.status_code)
# print(response.content)
# print()

# input("Press enter to add an agent")

# agent = {"uuid" : "0002",
#          "name" : "Dobby",
#          "agent_type" : "robotic-wolf",
#          "sensors" : "smell-sensor"}

# response = requests.post(url_prefix+"/agents", json=agent)

# print()
# print("Response status code:", response.status_code)
# print(response.content)
# if response.status_code == 201:
#     print(response.headers['Location'])

# input("\nPress enter to get agents list ")

# response = requests.get(url_prefix+"/agents")

# print()
# print("Response status code:", response.status_code)
# print(response.content)
# print()

# uuid = input("Enter the id to DELETE that agent:")

# response = requests.delete(url_prefix+f"/agents/{uuid}")

# print()
# print("Response status code:", response.status_code)
# print(response.content)
# print()

# agent = {"uuid" : "0003",
#          "name" : "Pluto",
#          "agent_type" : "phantasy-robotic-dog",
#          "sensors" : "sound-sensor"}

# uuid = input("Enter the id to UPDATE that agent:")

# response = requests.put(url_prefix+f"/agents/{uuid}", json=agent)

# print()
# print("Response status code:", response.status_code)
# print(response.content)
# print()