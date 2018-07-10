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
	
# printDetailItem("old sword")
roomNames=[]
def listRooms():
	for room in rooms.find():
		roomNames.append(room.get("name"))
		print(room.get("name"))
	print("\n**--**--**\n")
		

roomMap=[[]]
oldTile=8

def printActiveRoom():
	for x in roomMap:
		print (x)
def updateMap(): #da fare all load e prima e dopo il movimento
	global roomMap
	global oldTile
	x,y=player.get("x"),player.get("y")
	oldTile,roomMap[y][x]=roomMap[y][x],oldTile


def describeRoom(roomName): #diventera' initializeRoom()

	# rooms=db.rooms
	m_Room_query={
		"name":roomName
	}
	m_Room=rooms.find_one(m_Room_query)

	#print("\n"+m_Room.get("name"))
	size=m_Room.get("size")
	w,h=size, size
	global roomMap
	roomMap=[[0 for x in range(w)] for y in range(h)]
	

	for item in m_Room.get("items"):
		itemId=item.get("item_id")
		quer={"_id":itemId}
		res=items.find_one(quer)
		#print(res.get("name")+": "+res.get("desc")+".")
		#print(item.get("x"),item.get("y"))
		roomMap[item.get("x")][item.get("y")]=1


		

	# for door in m_Room.get("doors"):

	# 	nextRoomId=door.get(door.keys()[0])
	# 	roomName=door.keys()[0]
	# 	nextRoom=rooms.find_one(nextRoomId)
	# 	if nextRoom is not None:
	# 		print(roomName+": "+nextRoom.get("name"))
	# 	else:
	# 		print(roomName+": locked")
		

# listRooms()
# for r in roomNames:
# 	describeRoom(r)
	

#print(player)

activeRoom=rooms.find_one({"name":"ingresso"})
describeRoom("ingresso")



# for k,v in player.items():
# 	print(k,v)

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
	"none":[error11,()]

	}
	print("Called: "+fun[command][0].__name__)
	fun[command][0](*fun[command][1])




def loadState():
	p= playerst.find().sort("save_id",pymongo.DESCENDING).limit(1)[0]
	x,y=p.get("x"),p.get("y")
	return p
	

	


player=loadState()
print(player)
updateMap()
printActiveRoom()
while True:
	directionKey=raw_input('Enter your input:')
	manageInput(inpt.get(directionKey,"none"))
