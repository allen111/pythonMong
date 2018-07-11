#!/usr/bin/python
import pymongo,sys
# from pprint import pprint

client=pymongo.MongoClient()
db=client.rpg
items=db.items
rooms=db.rooms
playerst=db.playerstats
# playerDef=playerst.find_one({"name":"allen"}) adesso ci sono i salvataggi con save_id crescente vedi load and save
#esempi
# sword={
# 	"name":"old sword",
# 	"desc":"an old and rusty sword",
# 	"atk":2,
# 	"slot":0,
# 	"cost":10,
# 	"tags":["weapon","sword","common"]
# }

#items.insert_one(sword)

# queryVendor={
# 	"$or":[
# 		{"tags":"weapon"},{"tags":"food"}
# 	]
# }

#if result == None print all

def printItemsName(result): 

	if result is not None:
		for doc in result:
			print(doc)
	else:
		for doc in items.find():
			print(doc.get("name"))



def printDetailItem(itemName):			
	item=items.find_one({"name":itemName})
	for k,v in item.items():
		print(k+": "+str(v))
	
	

roomMap=[[]]
oldTile=7

def printActiveRoom():
	for x in roomMap:
		print (x)
def updateMap(): #da fare all load e prima e dopo il movimento
	global roomMap
	global oldTile
	x,y=player.get("x"),player.get("y")
	oldTile,roomMap[y][x]=roomMap[y][x],oldTile



def doorPosition(doorLoc,roomSize):
	pos={
	"nord":(roomSize//2,0),
	"sud":(roomSize//2,roomSize-1),
	"est":(roomSize-1,roomSize//2),
	"ovest":(0,roomSize//2),

	}
	return pos[doorLoc]


def isTaken(item):
	

	for it in player["inventory"]:
		if it["id_spawn"]==item["id_spawn"]:
			return True

	return False


doorList={}
def initializeRoom():
	global activeRoom
	
	size=activeRoom.get("size")
	w,h=size, size
	global roomMap
	roomMap=[[0 for x in range(w)] for y in range(h)]

	for item in activeRoom.get("items"):
		if not isTaken(item):
			roomMap[item.get("x")][item.get("y")]=1

	for door in activeRoom.get("doors"):
		nextRoomId=door.get(door.keys()[0])
		roomName=door.keys()[0]
		nextRoom=rooms.find_one(nextRoomId)
		if nextRoom is not None:
			roomX,roomY=doorPosition(roomName,activeRoom.get("size"))
			print(roomX,roomY)
			roomMap[roomY][roomX]=2
			global doorList

		else:
			roomX,roomY=doorPosition(roomName,activeRoom.get("size"))
			roomMap[roomY][roomX]=3


def openPort(x,y):
	global activeRoom
	global oldTile
	roomSize=activeRoom["size"]
	pos={
		(roomSize//2,0):"nord",
		(roomSize//2,roomSize-1):"sud",
		(roomSize-1,roomSize//2):"est",
		(0,roomSize//2):"ovest",
	}
	nextRoomName=pos.get((x,y))
	doorsList=activeRoom["doors"]
	matches=[obj for obj in doorsList if (obj.keys()[0]==nextRoomName)]
	if matches:
		door=matches.pop()
		doorid=door.get(nextRoomName)
		activeRoom=rooms.find_one({"_id":doorid})
		initializeRoom()
		oldTile=7
		reverse={
			"nord":"sud",
			"sud":"nord",
			"est":"ovest",
			"ovest":"est",
		}
		newDoor=reverse[nextRoomName]
		newX,newY=doorPosition(newDoor,activeRoom["size"])
		player.update({"x":newX})
		player.update({"y":newY})
		player.update({"room":activeRoom["name"]})
		updateMap()
		printActiveRoom()


def getItem(x,y):
	global activeRoom
	global oldTile
	if oldTile==2:
		openPort(x,y)
	else:
		res=activeRoom.get("items")
		matches = [obj for obj in res if (obj.get("y")==x and obj.get("x")==y)]
		if matches and oldTile!=0:
			itemOnFloor=matches.pop()
			activeRoom["items"].remove(itemOnFloor)
			itemOnFloorId=itemOnFloor.get("item_id")
			itemName=items.find_one({"_id":itemOnFloorId})["name"]
			itemDict={
				"name":itemName,
				"id":itemOnFloorId,
            	"id_spawn":itemOnFloor.get("id_spawn")

			}
			player["inventory"].append(itemDict)
			printInventory()
			oldTile=0


def printInventory():
	if not player["inventory"]:
		print("il tuo zaino e' vuoto")
	else:
		for item in player["inventory"]:
			itemId=item["id"]
			tmpItem=items.find_one({"_id":itemId})
			print(tmpItem["name"]+": "+tmpItem["desc"])





def exitWithoutSave():
	exit(0)
def savePlayerState(): 
	state=player
	state.pop("_id")
	newSave=state.get("save_id")
	newSave=newSave +1
	state.update({"save_id" : newSave})
	playerst.insert_one(player)
	print("goodbye")
	exit(0)

def loadState(): 
	p= playerst.find().sort("save_id",pymongo.DESCENDING).limit(1)[0]
	x,y=p.get("x"),p.get("y")
	global activeRoom
	activeRoom=rooms.find_one({"name":p["room"]})
	return p


def checkRoomPosition(x,y,m_activeRoom):
	size=m_activeRoom.get("size")
	if x>=0 and x<size and y>=0 and y<size:
		return True
	else:
		return False

def movePlayerNew(x,y,m_activeRoom):
	if checkRoomPosition(x,y,m_activeRoom):
		updateMap()
		player.update({"x":x})
		player.update({"y":y})
		updateMap()
		print(x,y)
	else:
		print("muroo\n")
	printActiveRoom()



# xy
# 00 10 20 30
# 01 11 21 31
# 02 12 22 32
def error11():
	print("sorry, where?")


inpt={
	"w":"nord",
	"s":"sud",
	"d":"est",
	"a":"ovest",
	"q":"quit",
	"x":"close",
	"e":"use",
	"i":"listInventory",
	"none":"none",
}


def manageInput(command):
	x=player.get("x")
	y=player.get("y")

	fun={
	"nord":[movePlayerNew,(x,y-1,activeRoom)],
	"sud":[movePlayerNew,(x,y+1,activeRoom)],
	"est":[movePlayerNew,(x+1,y,activeRoom)],
	"ovest":[movePlayerNew,(x-1,y,activeRoom)],
	"quit":[savePlayerState,()],
	"close":[exitWithoutSave,()],
	"use":[getItem,(x,y)],
	"listInventory":[printInventory,()],
	"none":[error11,()]

	}
	print("Called: "+str(fun[command][0].__name__)) #DEBUG
	fun[command][0](*fun[command][1])





	

	
activeRoomName="ingresso"
activeRoom=rooms.find_one({"name":activeRoomName})


player=loadState()
print(player) #DEBUG
initializeRoom()
updateMap()
printActiveRoom()
while True:
	directionKey=raw_input('Enter your input:')
	manageInput(inpt.get(directionKey,"none"))
