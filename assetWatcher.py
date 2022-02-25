import os
import json
import requests
from os.path import exists
from threading import Thread

# Use this webhook for new assets notifications
mUrl = "Your-Discord-WebHook-HERE"
# Use this webhook for a muted channel to keep track program execution
mUrl2 = "Your-Discord-WebHook-HERE"
dbName = "watchList.json"
fileExists = exists(dbName)
if not fileExists:
    sendNotifications = False
    data = open(dbName, "w", encoding="utf-8", errors="ignore")
    baseJson = {
        "hackeroneScopes": {},
        "bugcrowdScopes": {},
        "yeswehackScopes": {},
        "intigritiScopes": {},
        "hackenproofScopes": {},
        "federacyScopes": {}
    }
    baseJson = str(baseJson)
    baseJson = baseJson.replace("'", '"')
    data.write(baseJson)
    data.close()
else:
    sendNotifications = True


def saveFile(jsonData):
    Handle = open(dbName, "w+", encoding="utf-8", errors="ignore")
    json.dump(jsonData, Handle)


def DeleteFile(filename):
    try:
        os.remove(filename)
    except:
        pass


def loadFile():
    databaseFile = open(dbName)
    databaseFile = json.load(databaseFile)
    return databaseFile


def sendNotification(domain="", url="", programName = "", newBounty="", assetChanged = 0, bountyChaned = 0, submissionChanged = 0):
    submissionMessage = f"Submission Status Changed For:\nProgram Name: {programName}\nURL: {url}"
    newAssetMessage = f"New Asset Added To Scope:\nAsset: {domain}\nPorgram: {programName}\nURL: {url}"
    bountyStatusMessage = f"Bounty Payout Changed For:\nPorgram: {programName}\nURL: {url}\nAsset: {domain}\nNew Bounty: {newBounty}"
    if sendNotifications:
        if assetChanged:
            data = {"content": newAssetMessage}
            response = requests.post(mUrl, json=data)
        elif submissionChanged:
            data = {"content": submissionMessage}
            response = requests.post(mUrl, json=data)
        elif bountyChaned:
            data = {"content": bountyStatusMessage}
            response = requests.post(mUrl, json=data)


def sendStartupLog(status):
    if status == "start":
        message = f"[+] Watching Started!"
        data = {"content": message}
        response = requests.post(mUrl2, json=data)

    elif status == "end":
        message = f"[+] Watching End!"
        data = {"content": message}
        response = requests.post(mUrl2, json=data)


databaseData = loadFile()


try:
    sendStartupLog(status="start")
except:
    pass


def bugcrowdHandle():
    # Handling bugcrowd status
    print("[+] Handling bugcrowd data.")
    try:
        bugcrowdURL = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/bugcrowd_data.json"
        domainList = requests.get(bugcrowdURL, allow_redirects=True)
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        return 0
    open('bugcrowdProgramList.json', 'wb').write(domainList.content)
    bugcrowdDomainList = open('bugcrowdProgramList.json', encoding="utf-8", errors= "ignore")
    bugcrowdDomainList = json.load(bugcrowdDomainList)
    for scopeData in bugcrowdDomainList:
        programName = scopeData["name"]
        programURL = scopeData["url"]
        bountyPayoutStatus = scopeData["max_payout"]
        dataJson = {"programName": programName, "programURL": programURL, "bountyStatus": bountyPayoutStatus, "programAssets": []}
        keyName = f"{programName} || {programURL}"
        if keyName not in databaseData["bugcrowdScopes"].keys():
            databaseData["bugcrowdScopes"][keyName] = dataJson
        else:
            currentPayoutStatus = databaseData["bugcrowdScopes"][keyName]["bountyStatus"]
            if bountyPayoutStatus != currentPayoutStatus:
                databaseData["bugcrowdScopes"][keyName]["bountyStatus"] = bountyPayoutStatus
                sendNotification(bountyChaned=1, domain="NotProvided", programName=programName, url=programURL, newBounty=bountyPayoutStatus)

        for inscopeItem in scopeData["targets"]["in_scope"]:
            tempDict = {}
            tempDict["type"] = inscopeItem["type"]
            tempDict["target"] = inscopeItem["target"]

            addItem = True
            for num in range(0, len(databaseData["bugcrowdScopes"][keyName]["programAssets"])):
                assets = databaseData["bugcrowdScopes"][keyName]["programAssets"][num]
                if tempDict["target"] == assets["target"]:
                    addItem = False

            if addItem:
                databaseData["bugcrowdScopes"][keyName]["programAssets"].append(tempDict)
                sendNotification(assetChanged=1, domain=tempDict["target"], programName=programName, url=programURL)


def hackeroneHandle():
    print("[+] Handling hackerone data.")
    # Handling hackerone status
    try:
        hackeroneURL = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/hackerone_data.json"
        domainList = requests.get(hackeroneURL, allow_redirects=True)
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        return 0
    open('hackeroneProgramList.json', 'wb').write(domainList.content)
    hackeroneDomainList = open('hackeroneProgramList.json', encoding="utf-8", errors="ignore")
    hackeroneDomainList = json.load(hackeroneDomainList)
    for scopeData in hackeroneDomainList:
        programName = scopeData["name"]
        programURL = scopeData["url"]
        dataJson = {"programName": programName, "programURL": programURL, "programAssets": []}
        keyName = f"{programName} || {programURL}"
        if keyName not in databaseData["hackeroneScopes"].keys():
            databaseData["hackeroneScopes"][keyName] = dataJson

        for inscopeItem in scopeData["targets"]["in_scope"]:
            tempDict = {}
            tempDict["type"] = inscopeItem["asset_type"]
            tempDict["target"] = inscopeItem["asset_identifier"]
            tempDict["bountyStatus"] = inscopeItem["eligible_for_bounty"]
            tempDict["submissionStatus"] = inscopeItem["eligible_for_submission"]
            addItem = True

            for num in range(0, len(databaseData["hackeroneScopes"][keyName]["programAssets"])):
                assets = databaseData["hackeroneScopes"][keyName]["programAssets"][num]
                if tempDict["target"] == assets["target"]:
                    addItem = False
                    if tempDict["bountyStatus"] != assets["bountyStatus"]:
                        databaseData["hackeroneScopes"][keyName]["programAssets"][num]["bountyStatus"] = tempDict["bountyStatus"]
                        sendNotification(bountyChaned=1, domain="NotProvided", programName=programName, url=programURL,
                                         newBounty=tempDict["bountyStatus"])

                    if tempDict["submissionStatus"] != assets["submissionStatus"]:
                        sendNotification(submissionChanged=1, programName=programName, url=programURL)
                        databaseData["hackeroneScopes"][keyName]["programAssets"][num]["submissionStatus"] = tempDict[
                            "submissionStatus"]

            if addItem:
                databaseData["hackeroneScopes"][keyName]["programAssets"].append(tempDict)
                sendNotification(assetChanged=1, domain=tempDict["target"], programName=programName, url=programURL)


def yeswehackHandle():
    print("[+] Handling yeswehack data.")
    # Handling yesWeHack status
    try:
        yeswehackURL = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/yeswehack_data.json"
        domainList = requests.get(yeswehackURL, allow_redirects=True)
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        return 0
    open('yeswehackProgramList.json', 'wb').write(domainList.content)
    yeswehackDomainList = open('yeswehackProgramList.json', encoding="utf-8", errors= "ignore")
    yeswehackDomainList = json.load(yeswehackDomainList)
    for scopeData in yeswehackDomainList:
        programName = scopeData["name"]
        programURL = scopeData["id"]
        programSubmissionStatus = scopeData["disabled"]
        bountyPayoutStatus = scopeData["max_bounty"]
        dataJson = {"programName": programName, "programURL": programURL, "bountyStatus": bountyPayoutStatus, "programSubmissionStatus":programSubmissionStatus, "programAssets": []}
        keyName = f"{programName} || {programURL}"
        if keyName not in databaseData["yeswehackScopes"].keys():
            databaseData["yeswehackScopes"][keyName] = dataJson
        else:
            currentPayoutStatus = databaseData["yeswehackScopes"][keyName]["bountyStatus"]
            currentSubmissionStatus = databaseData["yeswehackScopes"][keyName]["programSubmissionStatus"]
            if bountyPayoutStatus != currentPayoutStatus:
                databaseData["yeswehackScopes"][keyName]["bountyStatus"] = bountyPayoutStatus
                sendNotification(bountyChaned=1, domain="NotProvided", programName=programName, url=programURL,
                                 newBounty=bountyPayoutStatus)

            if programSubmissionStatus != currentSubmissionStatus:
                sendNotification(submissionChanged=1, programName=programName, url=programURL)
                databaseData["yeswehackScopes"][keyName]["programSubmissionStatus"] = programSubmissionStatus

        for inscopeItem in scopeData["targets"]["in_scope"]:
            tempDict = {}
            tempDict["type"] = inscopeItem["type"]
            tempDict["target"] = inscopeItem["target"]

            addItem = True
            for num in range(0, len(databaseData["yeswehackScopes"][keyName]["programAssets"])):
                assets = databaseData["yeswehackScopes"][keyName]["programAssets"][num]
                if tempDict["target"] == assets["target"]:
                    addItem = False

            if addItem:
                databaseData["yeswehackScopes"][keyName]["programAssets"].append(tempDict)
                sendNotification(assetChanged=1, domain=tempDict["target"], programName=programName, url=programURL)


def intigrityHandle():
    print("[+] Handling intigrity data.")
    # Handling intigriti status
    try:
        intigritiURL = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/intigriti_data.json"
        domainList = requests.get(intigritiURL, allow_redirects=True)
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        return 0
    open('intigritiProgramList.json', 'wb').write(domainList.content)
    intigritiDomainList = open('intigritiProgramList.json', encoding="utf-8", errors= "ignore")
    intigritiDomainList = json.load(intigritiDomainList)
    for scopeData in intigritiDomainList:
        programName = scopeData["name"]
        programURL = scopeData["url"]
        bountyPayoutStatus = scopeData["max_bounty"]["value"]
        programSubmissionStatus = scopeData["status"]

        dataJson = {"programName": programName, "programURL": programURL, "bountyStatus": bountyPayoutStatus, "programSubmissionStatus": programSubmissionStatus, "programAssets": []}
        keyName = f"{programName} || {programURL}"
        if keyName not in databaseData["intigritiScopes"].keys():
            databaseData["intigritiScopes"][keyName] = dataJson
        else:
            currentPayoutStatus = databaseData["intigritiScopes"][keyName]["bountyStatus"]
            currentSubmissionStatus = databaseData["intigritiScopes"][keyName]["programSubmissionStatus"]
            if bountyPayoutStatus != currentPayoutStatus:
                sendNotification(bountyChaned=1, domain="NotProvided", programName=programName, url=programURL, newBounty=bountyPayoutStatus)
                databaseData["intigritiScopes"][keyName]["bountyStatus"] = bountyPayoutStatus
            if programSubmissionStatus != currentSubmissionStatus:
                sendNotification(submissionChanged=1, programName=programName, url=programURL)
                databaseData["intigritiScopes"][keyName]["programSubmissionStatus"] = programSubmissionStatus

        for inscopeItem in scopeData["targets"]["in_scope"]:
            tempDict = {}
            tempDict["type"] = inscopeItem["type"]
            tempDict["target"] = inscopeItem["endpoint"]

            addItem = True
            for num in range(0, len(databaseData["intigritiScopes"][keyName]["programAssets"])):
                assets = databaseData["intigritiScopes"][keyName]["programAssets"][num]
                if tempDict["target"] == assets["target"]:
                    addItem = False

            if addItem:
                databaseData["intigritiScopes"][keyName]["programAssets"].append(tempDict)
                sendNotification(assetChanged=1, domain=tempDict["target"], programName=programName, url=programURL)


def hackenproofHandle():
    print("[+] Handling hackenproof data.")
    # Handling hackenproof status
    try:
        hackenproofURL = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/hackenproof_data.json"
        domainList = requests.get(hackenproofURL, allow_redirects=True)
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        return 0
    open('hackenproofProgramList.json', 'wb').write(domainList.content)
    hackenproofDomainList = open('hackenproofProgramList.json', encoding="utf-8", errors="ignore")
    hackenproofDomainList = json.load(hackenproofDomainList)
    for scopeData in hackenproofDomainList:
        programName = scopeData["name"]
        programURL = scopeData["url"]
        programSubmissionStatus = scopeData["archived"]

        dataJson = {"programName": programName, "programURL": programURL, "programSubmissionStatus": programSubmissionStatus, "programAssets": []}
        keyName = f"{programName} || {programURL}"
        if keyName not in databaseData["hackenproofScopes"].keys():
            databaseData["hackenproofScopes"][keyName] = dataJson
        else:
            currentSubmissionStatus = databaseData["hackenproofScopes"][keyName]["programSubmissionStatus"]
            if programSubmissionStatus != currentSubmissionStatus:
                sendNotification(submissionChanged=1, programName=programName, url=programURL)
                databaseData["hackenproofScopes"][keyName]["programSubmissionStatus"] = programSubmissionStatus

        for inscopeItem in scopeData["targets"]["in_scope"]:
            tempDict = {}
            tempDict["type"] = inscopeItem["type"]
            tempDict["target"] = inscopeItem["target"]
            tempDict["bountyStatus"] = inscopeItem["reward"]
            addItem = True

            for num in range(0, len(databaseData["hackenproofScopes"][keyName]["programAssets"])):
                assets = databaseData["hackenproofScopes"][keyName]["programAssets"][num]
                if tempDict["target"] == assets["target"]:
                    addItem = False
                    if tempDict["bountyStatus"] != assets["bountyStatus"]:
                        databaseData["hackenproofScopes"][keyName]["programAssets"][num]["bountyStatus"] = tempDict["bountyStatus"]
                        sendNotification(bountyChaned=1, domain="NotProvided", programName=programName, url=programURL,
                                         newBounty=tempDict["bountyStatus"])

            if addItem:
                databaseData["hackenproofScopes"][keyName]["programAssets"].append(tempDict)
                sendNotification(assetChanged=1, domain=tempDict["target"], programName=programName, url=programURL)


def federacyHandle():
    # Handling federacy status
    try:
        federacyURL = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/federacy_data.json"
        domainList = requests.get(federacyURL, allow_redirects=True)
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        return 0
    open('federacyProgramList.json', 'wb').write(domainList.content)
    federacyDomainList = open('federacyProgramList.json', encoding="utf-8", errors= "ignore")
    federacyDomainList = json.load(federacyDomainList)
    for scopeData in federacyDomainList:
        programName = scopeData["name"]
        programURL = scopeData["url"]
        dataJson = {"programName": programName, "programURL": programURL, "programAssets": []}
        keyName = f"{programName} || {programURL}"
        if keyName not in databaseData["federacyScopes"].keys():
            databaseData["federacyScopes"][keyName] = dataJson

        for inscopeItem in scopeData["targets"]["in_scope"]:
            tempDict = {}
            tempDict["type"] = inscopeItem["type"]
            tempDict["target"] = inscopeItem["target"]

            addItem = True
            for num in range(0, len(databaseData["federacyScopes"][keyName]["programAssets"])):
                assets = databaseData["federacyScopes"][keyName]["programAssets"][num]
                if tempDict["target"] == assets["target"]:
                    addItem = False

            if addItem:
                databaseData["federacyScopes"][keyName]["programAssets"].append(tempDict)
                sendNotification(assetChanged=1, domain=tempDict["target"], programName=programName, url=programURL)


thread_list = [Thread(target=bugcrowdHandle), Thread(target=hackeroneHandle), Thread(target=yeswehackHandle),
               Thread(target=intigrityHandle), Thread(target=hackenproofHandle), Thread(target=federacyHandle)]

for thread in thread_list:
    thread.start()

for thread in thread_list:
    thread.join()

DeleteFile("bugcrowdProgramList.json")
DeleteFile("hackenproofProgramList.json")
DeleteFile("hackeroneProgramList.json")
DeleteFile("intigritiProgramList.json")
DeleteFile("yeswehackProgramList.json")
DeleteFile("federacyProgramList.json")

saveFile(databaseData)
try:
    sendStartupLog(status="end")
except:
    pass
