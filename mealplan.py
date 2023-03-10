import grequests
from datetime import datetime
import json


def getInfo(idNumbers):
    apiLink = "https://mplan.ashesi.edu.gh/API/api/getSubscriberHistory/"
    urls = []

    today = datetime.now()
    today = "/"+today.strftime("%Y-%m-%d")
    for num in idNumbers:
        urls.append(f"{apiLink}{num}{2*today}")
    
    try:
        response = (grequests.get(u) for u in urls)

        payloads = grequests.map(response)
        payloads = [payload.json() for payload in payloads if len(payload.json()) >0]
        print(f"Made {len(urls)} requests")

        return payloads
    except:
        print("Check your network")
    
    return []


def extractEssentials(payload):
    info = {"costs":[], "names":[], "times":[], "vendors":[]}
    
    for everyJson in payload:
        info["costs"].append(everyJson['cost'])
        info["names"].append(everyJson['name'])
        info["times"].append(int(everyJson['date'].split()[1].split(":")[0]))
        if everyJson['transaction_point'] == "Akorno Services Ltd - Main Cafe":
            info["vendors"].append("Akornor Cafeteria")
        elif everyJson['transaction_point'] == "Akorno Services Ltd - Hakuna Matata":
            info["vendors"].append("Hakuna Services")
        else:
            info["vendors"].append(everyJson['transaction_point'])
        
    return info

                        
def gatherHistory():
    retrievedPayloads = []
    historyData = dict()

    # get payloads of all numbers
    for i in range(3,6):
        numbers = []
        with open(f"c2{i}.txt","r") as f:
            for num in f.readlines():
                numbers.append(str(int(num)))
            receivedPayload = getInfo(numbers)
            if len(receivedPayload) > 1:
                retrievedPayloads.append(receivedPayload)
    print("Payload received")
    
    # for item in retrievedPayloads:
    if len(retrievedPayloads)<1:
        exit()
    #print(f"{retrievedPayloads.count([])}")
   
    # extract necessaryinfo from payloads
    for payloads in retrievedPayloads:
        for payload in payloads:
            extractedInfo = extractEssentials(payload)
            for i,vendor in enumerate(extractedInfo["vendors"]):
                if vendor in historyData:
                    hour = extractedInfo["times"][i]
                    if 0 <= hour < 12:
                        historyData[vendor]["morning"].add(extractedInfo["names"][i])
                    elif 12 <= hour < 18:
                        historyData[vendor]["afternoon"].add(extractedInfo["names"][i])
                    else:
                        historyData[vendor]["evening"].add(extractedInfo["names"][i])
                else:
                    historyData[vendor] = dict()
                    historyData[vendor]["morning"] = set()
                    historyData[vendor]["afternoon"] = set()
                    historyData[vendor]["evening"] = set()

                    # fill in information
                    hour = extractedInfo["times"][i]
                    if 0 <= hour < 12:
                        historyData[vendor]["morning"].add(extractedInfo["names"][i])
                    elif 12 <= hour < 18:
                        historyData[vendor]["afternoon"].add(extractedInfo["names"][i])
                    else:
                        historyData[vendor]["evening"].add(extractedInfo["names"][i])

    # convert sets to lists for json dumping
    for vendor in historyData:
        for category in ["morning","afternoon","evening"]:
            items = []
            for item in historyData[vendor][category]:
                items.append(item)
            historyData[vendor][category] = items

    # store them in json file
    with open("HistoryData.json","w") as new_json_file:
        json.dump(historyData,new_json_file)
    
    print("History received...")
    

gatherHistory()


'''
Frank mssg: I have started to work on the project (smile)

'''



