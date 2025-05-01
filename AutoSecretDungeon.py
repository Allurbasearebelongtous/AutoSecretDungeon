from phBot import *
from threading import Thread
from threading import Timer
from threading import Lock
from collections import deque
from enum import Enum
from time import sleep
from datetime import datetime, timedelta
import asyncio
import phBotChat
import time
import threading
import QtBind
import struct
import random
import json
import os
import math
import webbrowser
from binascii import hexlify  # for debugging

pName = 'AutoSecretDungeon'
logPrefix = pName + '-plugin: '
pVersion = '1.0.0'
pUrl = 'https://github.com/Allurbasearebelongtous/AutoSecretDungeon'
pUrlEnglish = 'https://github.com/Allurbasearebelongtous/AutoSecretDungeon/wiki'
pUrlTurkish = 'https://github.com/Allurbasearebelongtous/AutoSecretDungeon/wiki/Bilgiler'
glb_char_data = None
glb_entered_dungeon = False
glb_loaded = False
glb_readyToEnter = False

inject_lock = Lock()
inject_queue = deque()
# Global event to control the stop condition
glb_stop_event = threading.Event()
glb_thread_started = False
glb_thread_lock = threading.Lock()

#______________________________ENUMS________________________________________#

class ChatType(int, Enum):
	CHAT_ALL = 1
	CHAT_PM = 2
	CHAT_ALLGM = 3
	CHAT_PARTY = 4
	CHAT_GUILD = 5
	CHAT_GLOBAL = 6
	CHAT_NOTICE = 7
	CHAT_STALL = 9
	CHAT_UNION = 11
	CHAT_NPC = 13
	CHAT_ACCADEMY = 16

class Command(str, Enum):
	CMD_EnterDungeon = 'enter secret dungeon'

class REGION(Enum):
	BAGDAD_TOWN = 22618
	ALEXS_TOWN = 23088
	ALEXN_TOWN = 23603
	HOTAN_TOWN = 23687
	JANGAN_TOWN = 25000
	DW_TOWN = 26265
	CONST_TOWN = 26959
	SAMARKAND_TOWN = 27244
	UPPER_DUNGEON = -32741
	LOWER_DUNGEON = -32740

# ______________________________ Initializing ______________________________ #
gui = QtBind.init(__name__,pName)
gui_window_padding_x = 30
gui_window_padding_y = 30

gui_label_box_size_height = 20
gui_label_box_size_width = 100

gui_leader_name_label_x = gui_window_padding_x
gui_leader_name_label_y = gui_window_padding_y
gui_leader_name_line_x = gui_leader_name_label_x + 70
gui_leader_name_line_y = gui_leader_name_label_y - 5
QtBind.createLabel(gui, 'Party Leader:', gui_leader_name_label_x, gui_leader_name_label_y)
gui_leaderName = QtBind.createLineEdit(gui,"Party leader",gui_leader_name_line_x,gui_leader_name_line_y,gui_label_box_size_width,gui_label_box_size_height)

gui_party_size_label_x = gui_window_padding_x
gui_party_size_label_y = gui_leader_name_line_y + gui_window_padding_y
gui_party_size_line_x = gui_party_size_label_x + 70
gui_party_size_line_y = gui_party_size_label_y - 5
QtBind.createLabel(gui, 'Party size:', gui_party_size_label_x, gui_party_size_label_y)
gui_partySize = QtBind.createLineEdit(gui,"8",gui_party_size_line_x,gui_party_size_line_y,gui_label_box_size_width,gui_label_box_size_height)
QtBind.createLabel(gui, '(only used by party leader)', gui_party_size_line_x + 110, gui_party_size_line_y)

gui_max_tries_label_x = gui_window_padding_x
gui_max_tries_label_y = gui_party_size_line_y + gui_window_padding_y
gui_max_tries_line_x = gui_max_tries_label_x + 70
gui_max_tries_line_y = gui_max_tries_label_y - 5
QtBind.createLabel(gui, 'Max tries:', gui_max_tries_label_x, gui_max_tries_label_y)
gui_max_tries = QtBind.createLineEdit(gui,"100",gui_max_tries_line_x,gui_max_tries_line_y,gui_label_box_size_width,gui_label_box_size_height)
QtBind.createLabel(gui, '(only used by party leader)', gui_max_tries_line_x + 110, gui_max_tries_line_y)

gui_upper_dungeon_profile_label_x = gui_window_padding_x
gui_upper_dungeon_profile_label_y = gui_max_tries_line_y + gui_window_padding_y
gui_upper_dungeon_profile_line_x = gui_upper_dungeon_profile_label_x + 70
gui_upper_dungeon_profile_line_y = gui_upper_dungeon_profile_label_y - 5
QtBind.createLabel(gui, 'Upper profile:', gui_upper_dungeon_profile_label_x, gui_upper_dungeon_profile_label_y)
gui_upper_dungeon_profile = QtBind.createLineEdit(gui,"profile name",gui_upper_dungeon_profile_line_x,gui_upper_dungeon_profile_line_y,gui_label_box_size_width,gui_label_box_size_height)

gui_lower_dungeon_profile_label_x = gui_window_padding_x
gui_lower_dungeon_profile_label_y = gui_upper_dungeon_profile_line_y + gui_window_padding_y
gui_lower_dungeon_profile_line_x = gui_lower_dungeon_profile_label_x + 70
gui_lower_dungeon_profile_line_y = gui_lower_dungeon_profile_label_y - 5
QtBind.createLabel(gui, 'Lower Profile:', gui_lower_dungeon_profile_label_x, gui_lower_dungeon_profile_label_y)
gui_lower_dungeon_profile = QtBind.createLineEdit(gui,"profile name",gui_lower_dungeon_profile_line_x,gui_lower_dungeon_profile_line_y,gui_label_box_size_width,gui_label_box_size_height)


gui_upper_checkbox_label_x = gui_window_padding_x
gui_upper_checkbox_label_y = gui_lower_dungeon_profile_label_y + gui_window_padding_y
gui_upper_checkbox_x = gui_upper_checkbox_label_x + 120
gui_upper_checkbox_y = gui_upper_checkbox_label_y
QtBind.createLabel(gui, 'enter upper dungeon',  gui_upper_checkbox_label_x, gui_upper_checkbox_label_y)
gui_upper_checkbox = QtBind.createCheckBox(gui, 'cbx_upper_clicked','True', gui_upper_checkbox_x, gui_upper_checkbox_y)

gui_lower_checkbox_label_x = gui_window_padding_x
gui_lower_checkbox_label_y = gui_upper_checkbox_label_y + gui_window_padding_y
gui_lower_checkbox_x = gui_lower_checkbox_label_x + 120
gui_lower_checkbox_y = gui_lower_checkbox_label_y
QtBind.createLabel(gui, 'enter lower dungeon',  gui_lower_checkbox_label_x, gui_lower_checkbox_label_y)
gui_lower_checkbox = QtBind.createCheckBox(gui, 'cbx_lower_clicked','True', gui_lower_checkbox_x, gui_lower_checkbox_y)

gui_gatherspot_area_name_label_x = 400
gui_gatherspot_area_name_label_y = gui_window_padding_y
gui_gatherspot_area_name_line_x = gui_gatherspot_area_name_label_x + 150
gui_gatherspot_area_name_line_y = gui_gatherspot_area_name_label_y - 5
QtBind.createLabel(gui, 'Training area (Gather spot):', gui_gatherspot_area_name_label_x, gui_gatherspot_area_name_label_y)
gui_gatherspot_area_name = QtBind.createLineEdit(gui,"Gather",gui_gatherspot_area_name_line_x,gui_gatherspot_area_name_line_y,gui_label_box_size_width,gui_label_box_size_height)

gui_buffup_area_name_label_x = gui_gatherspot_area_name_label_x
gui_buffup_area_name_label_y = gui_gatherspot_area_name_line_y + gui_window_padding_y
gui_buffup_area_name_line_x = gui_buffup_area_name_label_x + 150
gui_buffup_area_name_line_y = gui_buffup_area_name_label_y - 5
QtBind.createLabel(gui, 'Training area (buffup spot):', gui_buffup_area_name_label_x, gui_buffup_area_name_label_y)
gui_buffspot_area_name = QtBind.createLineEdit(gui,"Buffup",gui_buffup_area_name_line_x,gui_buffup_area_name_line_y,gui_label_box_size_width,gui_label_box_size_height)

gui_hunt_area_name_label_x = gui_buffup_area_name_label_x
gui_hunt_area_name_label_y = gui_buffup_area_name_line_y + gui_window_padding_y
gui_hunt_area_name_line_x = gui_hunt_area_name_label_x + 150
gui_hunt_area_name_line_y = gui_hunt_area_name_label_y - 5
QtBind.createLabel(gui, 'Training area (Hunting spot):', gui_hunt_area_name_label_x, gui_hunt_area_name_label_y)
gui_huntspot_area_name = QtBind.createLineEdit(gui,"Hunt",gui_hunt_area_name_line_x,gui_hunt_area_name_line_y,gui_label_box_size_width,gui_label_box_size_height)

btnLoadConfig = QtBind.createButton(gui,'LoadConfig',"   load config    ",gui_window_padding_x,280)
btnSaveConfig = QtBind.createButton(gui,'SaveConfigIfJoined',"   save config    ",gui_window_padding_x + 100,280)

gui_guideEng = QtBind.createButton(gui,'OpenGuidePageEng',"English!",640,200)
gui_guideTurkish = QtBind.createButton(gui,'OpenGuidePageTurkish',"Turkish",640,170)

versionLabel = QtBind.createLabel(gui, 'version 1.0.0', 650, 300)

#________________________________GUI_methods__________________________#
def cbx_upper_clicked(checked):
	if checked:
		QtBind.setChecked(gui, gui_lower_checkbox, False)
		SaveConfigIfJoined()

def cbx_lower_clicked(checked):
	if checked:
		QtBind.setChecked(gui, gui_upper_checkbox, False)
		SaveConfigIfJoined()
		
def OpenGuidePageEng():
	webbrowser.open(pUrlEnglish)

def OpenGuidePageTurkish():
	webbrowser.open(pUrlTurkish)
# ______________________________ logger ______________________________ #
def LogMsg(logstr):
	log(logPrefix + logstr)

#_______________________________config methods_________________________#
def enable_conditions(conditions, is_enabled):
		for condition in conditions:
			condition["Enabled"] = is_enabled
#_______________________________Async methods__________________________#
async def async_Load_config_when_chardata_ready():
	glb_char_data =  CharInGame()
	max_tries = 5
	tries = 0

	#loop untill the condition is met or tries exceeds the max_tries
	while glb_char_data is None and tries < max_tries:
		CharInGame()
		LogMsg("waiting for char data to become available")
		await async_task_with_sleep(1)
		tries += 1
	
	if(glb_char_data is None):
		LogMsg("❌ its taking too long to retrieve char data! cannot proceed with config load")
	else:
		LoadConfig()
		await async_task_with_sleep(2)
		isUpper = QtBind.isChecked(gui,gui_upper_checkbox)
		if(isUpper):
			success = set_profile(str(QtBind.text(gui,gui_upper_dungeon_profile)))
			if(not success):
				LogMsg(f"❌ profile {gui_upper_dungeon_profile} not found! make sure you assign a valid profile in plugin GUI")
				return 0
		else:
			success = set_profile(str(QtBind.text(gui,gui_lower_dungeon_profile)))
			if(not success):
				LogMsg(f"❌ profile {gui_lower_dungeon_profile} not found! make sure you assign a valid profile in plugin GUI")
				return 0
			
		await async_task_with_sleep(2)
		LogMsg("Change training area to gathering spot")
		success = set_training_area(str(QtBind.text(gui,gui_gatherspot_area_name)))
		if(not success):
			LogMsg(f"❌ training area {gui_gatherspot_area_name} not found! make sure gathering training area name in GUI matches to what is in current profile")
			return 0
		LogMsg("waiting randomly to avoid overheat")
		await async_task_with_sleep(2)

async def async_check_stop_event():
    """Async-friendly stop event checker."""
    if glb_stop_event.is_set():
        LogMsg("Background thread interrupted via callback.")
        return True
    return False

async def async_task_with_sleep(duration):
    for i in range(duration):  # Sleep in chunks of 1 second to check periodically
        if await async_check_stop_event():
            return 0
        
        await asyncio.sleep(1)  # Sleep for 1 second (can be adjusted)

async def asynch_random_sleep(min, max):
	LogMsg(f"randomly waiting between {min} and {max} second to avoid overloading")
	delay = int(random.uniform(float(min), float(max)))
	await async_task_with_sleep(int(delay))
	LogMsg("random delay is finished. proceeding to next step...")

async def async_returnTown():
	condition_met = use_return_scroll()
	max_tries = 3
	tries = 0

	try:
		#loop untill the condition is met or tries exceeds the max_tries
		while not condition_met and tries < max_tries:
			LogMsg("trying to use return scroll...")
			condition_met = use_return_scroll()
			await async_task_with_sleep(1)
			tries += 1
	except asyncio.TimeoutError:
		LogMsg("❌ Timeout: failed using return scroll")
		return False
	except Exception as e:
		LogMsg(f"❌  Error in async_stop_bot: {e}")
		return False
	
	if(not condition_met):
		LogMsg("❌ cannot return town! make sure there are return scrolls in player's inventory")

	return condition_met

async def async_leave_party():
	condition_met = not get_party()
	if(condition_met):
		LogMsg("not in party!")
	max_tries = 3
	tries = 0

	try:
		#loop untill the condition is met or tries exceeds the max_tries
		while not condition_met and tries < max_tries:
			print("trying to leave party...")
			leave_party()
			await async_task_with_sleep(1)
			condition_met = not get_party()
			if(condition_met):
				LogMsg("succesfully left party")
			tries += 1
		
		return condition_met
	except asyncio.TimeoutError:
		LogMsg("❌ Timeout: leaving party task took too long")
		return False
	except Exception as e:
		LogMsg(f"❌ Error in async_leave_party: {e}")
		return False		

async def async_stop_bot():
	condition_met = False
	max_tries = 3
	tries = 0

	try:
		#loop untill the condition is met or tries exceeds the max_tries
		while not condition_met and tries < max_tries:
			LogMsg("Waiting for bot to stop...")
			condition_met = stop_bot()
			await async_task_with_sleep(1)
			tries += 1
		return condition_met
	except asyncio.TimeoutError:
		LogMsg("❌ Timeout: Bot stop task took too long")
		return False
	except Exception as e:
		LogMsg(f"❌ Error in async_stop_bot: {e}")
		return False		

async def async_start_bot():
	condition_met = start_bot()
	max_tries = 3
	tries = 0

	try:
		#loop untill the condition is met or tries exceeds the max_tries
		while not condition_met and tries < max_tries:
			LogMsg("Waiting for bot to start...")
			condition_met = start_bot()
			await async_task_with_sleep(2)
			tries += 1
		return condition_met
	except asyncio.TimeoutError:
		LogMsg("❌ Timeout: Bot start task took too long")
		return False
	except Exception as e:
		LogMsg(f"❌ Error in async_start_bot: {e}")
		return False

async def async_waitPartyMembers():
	condition_met = PreliminaryCheck()
	if(condition_met):
		LogMsg("all members here!")
	max_tries = 200
	tries = 0

	try:
		#loop untill the condition is met or tries exceeds the max_tries
		while not condition_met and tries < max_tries:
			print("preliminary check...")
			await async_task_with_sleep(10)
			condition_met = PreliminaryCheck()
			if(condition_met):
				LogMsg("preliminary check succesfull")
			tries += 1
		
		return condition_met
	except asyncio.TimeoutError:
		LogMsg("❌ Timeout: leaving party task took too long")
		return False
	except Exception as e:
		LogMsg(f"❌ Error in async_leave_party: {e}")
		return False		

async def async_secret_dungeon_prepare():
	
	if(glb_char_data['name'] == str(QtBind.text(gui,gui_leaderName))):
		LogMsg("waiting for party members")
		await async_waitPartyMembers()
		LogMsg("waiting complete")
	return 0

async def async_secret_dungeon_enter(isUpper):
	NpcID = GetNPCUniqueID('Ancient History Scholar')
	if NpcID == 0:
		LogMsg('⚠️ Plugin: "Ancient History Scholar" is not near. Be sure to use the script command near to the NPC')
		return False
	else:
		LogMsg("handling entry packages to dungeon")
		p = bytearray(struct.pack('<H', NpcID))
		p += b'\x00\x00'
		SelectAncientHistoryScholarNPC(p)
		await async_task_with_sleep(4)
		SelectSecretDungeon(isUpper)
		await async_task_with_sleep(4)
		sendDungeonEntry()
		await async_task_with_sleep(1)
		return True

async def async_secret_dungeon_hunt():
	LogMsg("Change training area to buffing spot")
	success = set_training_area(str(QtBind.text(gui,gui_buffspot_area_name)))
	if(not success):
		LogMsg(f"❌ training area {gui_gatherspot_area_name} not found! make sure buff up spot training area name in GUI matches to what is in current profile")
		return 0	
	await async_task_with_sleep(1)
	await async_start_bot()
	await async_task_with_sleep(15)
	LogMsg("waiting 15 second to buffs to complete")
	await async_stop_bot()
	LogMsg("setting the training area to hunting and starting the bot")
	success = set_training_area(str(QtBind.text(gui,gui_huntspot_area_name)))
	if(not success):
		LogMsg(f"❌ training area {gui_gatherspot_area_name} not found! make sure hunting spot training area name in GUI matches to what is in current profile")
		return 0
	await async_task_with_sleep(4)
	await async_start_bot()
	await async_task_with_sleep(1)
	return 0

async def async_secret_dungeon_complete():
	await asynch_random_sleep(1, 10)
	disconnect()
	return 0
#__________________________________methods___________________________#
# Wrapper to run the coroutine in a thread
def async_auto_secret_dungeon(arguments):
	prepare = "Prepare" in arguments
	Enter = "Enter" in arguments
	Hunt = "Hunt" in arguments
	Complete = "Complete" in arguments
	load = "Load" in arguments
	global glb_thread_started
	if(load):
		try:
			asyncio.run(async_Load_config_when_chardata_ready())
		except Exception as e:
			LogMsg(f"Error in async_Load_config_when_chardata_ready: {e}")
		finally:
			LogMsg("LOAD task finished")
			with glb_thread_lock:
				glb_thread_started = False
	elif(prepare):
		try:
			asyncio.run(async_secret_dungeon_prepare())
		except Exception as e:
			LogMsg(f"Error in async_secret_dungeon_prepare: {e}")
		finally:
			LogMsg("PREPARE task finished")
			with glb_thread_lock:
				glb_thread_started = False
				if(glb_readyToEnter and glb_char_data['name'] == glb_char_data['name'] == str(QtBind.text(gui,gui_leaderName))):
					Timer(1.0,RequestDungeonEntry).start()
	elif(Enter):
		try:
			isUpper = isUpper = QtBind.isChecked(gui,gui_upper_checkbox)
			asyncio.run(async_secret_dungeon_enter(isUpper))
		except Exception as e:
			LogMsg(f"Error in async_secret_dungeon_enter: {e}")
		finally:
			LogMsg("ENTER task finished")
			with glb_thread_lock:
				glb_thread_started = False
	elif(Hunt):
		try:
			asyncio.run(async_secret_dungeon_hunt())
		except Exception as e:
			LogMsg(f"Error in async_secret_dungeon_hunt: {e}")
		finally:
			LogMsg("HUNT task finished")
			with glb_thread_lock:
				glb_thread_started = False
	elif(Complete):
		try:
			asyncio.run(async_secret_dungeon_complete())
		except Exception as e:
			LogMsg(f"Error in async_secret_dungeon_complete: {e}")
		finally:
			LogMsg("COMPLETE task finished")
			with glb_thread_lock:
				glb_thread_started = False

	else:
		LogMsg("argument is not recognised! exiting without doing anything")
	
	return 0

def secret_dungeon_prepare(arguments):
	global glb_thread_started
	with glb_thread_lock:
		if (glb_thread_started):
			return 0
		glb_thread_started = True

	LogMsg("PREPERATION task started")
	arguments = ["Prepare"]
	thread = Thread(target=async_auto_secret_dungeon, args=(arguments,))
	thread.daemon = False  # Non-daemon thread
	thread.start()
	LogMsg("PREPERATION task running in background")
	return 0

def secret_dungeon_enter():
	global glb_thread_started
	with glb_thread_lock:
		if (glb_thread_started):
			return 0
		glb_thread_started = True

	LogMsg("ENTER task started")
	arguments = ["Enter"]
	thread = Thread(target=async_auto_secret_dungeon, args=(arguments,))
	thread.daemon = False  # Non-daemon thread
	thread.start()

	LogMsg("ENTER task running in background")
	return 0

def secret_dungeon_hunt():
	global glb_thread_started
	with glb_thread_lock:
		if (glb_thread_started):
			return 0
		glb_thread_started = True

	LogMsg("HUNT task started")
	arguments = ["Hunt"]
	thread = Thread(target=async_auto_secret_dungeon, args=(arguments,))
	thread.daemon = False  # Non-daemon thread
	thread.start()
	LogMsg("HUNT task running in background")
	return 0

def secret_dungeon_complete():
	global glb_thread_started
	with glb_thread_lock:
		if (glb_thread_started):
			return 0
		glb_thread_started = True

	LogMsg("COMPLETION task started")
	arguments = ["Complete"]
	thread = Thread(target= async_auto_secret_dungeon, args=(arguments,))
	thread.daemon = False  # Non-daemon thread
	thread.start()
	LogMsg("COMPLETION task running in backgroun")

def load_char_data_inbackground():
	global glb_thread_started
	with glb_thread_lock:
		if (glb_thread_started):
			return 0
		glb_thread_started = True
	arguments = ["Load"]
	LogMsg("LOAD CONFIG task started")
	thread = Thread(target=async_auto_secret_dungeon, args=(arguments,))
	thread.daemon = False  # Non-daemon thread
	thread.start()
	LogMsg("LOAD CONFIG task running in background")

def UnequipItem(item):
	# find an empty slot
	slot = GetEmptySlot()
	if slot == -1:
		LogMsg('⚠️ ignored unequipping job item. No empty slot available')
	elif item['slot'] != 8:
		LogMsg('⚠️ ignored unequipping job item. No equipped job item is found!')
	else:
		Inject_InventoryMovement(0,item['slot'],slot,item['name'])

def PreliminaryCheck():
	global glb_readyToEnter
	if glb_readyToEnter == False and glb_char_data['name'] == str(QtBind.text(gui, gui_leaderName)):
		players = get_party()
		numberOfMembers = len(players)
		requiredmembers = 8
		try:
			requiredmembers = int(QtBind.text(gui, gui_partySize))
		except ValueError:
			LogMsg('⚠️ party size not recognised as number. make sure you entered only numbers in party size line!')

		if (numberOfMembers < requiredmembers):
			LogMsg(f"Waiting for {requiredmembers} members to join party. Current members: {numberOfMembers}/{requiredmembers}")
			return False
		else:
			trainingArea = get_training_area()
			char_data = get_character_data()
			areaXY = [int(trainingArea['x']), int(trainingArea['y'])]
			LogMsg(f"Training area: {str(areaXY)}")

            # First check if current player is in the training area
			currentPlayerXY = [int(char_data['x']), int(char_data['y'])]
			LogMsg(f"Player location: {str(currentPlayerXY)}")
			currentPlayerDistance = math.dist(currentPlayerXY, areaXY)
			if currentPlayerDistance > 3:
				LogMsg(f"Player {char_data['name']} is too far from training area (distance: {currentPlayerDistance})")
				return False
			
			if players:
				for key, player in players.items():
					if player['player_id'] <= 0:
						LogMsg(f"Player {player['name']} doesn't have a valid unique player ID.")
						return False
					else:
						playerXY = [int(player['x']), int(player['y'])]
						distance = math.dist(playerXY, areaXY)
						if distance > 3:
							LogMsg(f"Player {player['name']} is too far from training area (distance: {distance})")
							return False

			glb_readyToEnter = True
			LogMsg("Preliminary checks succeeded! We can enter the dungeon.")
			return True
	return False


def RequestDungeonEntry():
	LogMsg("request party mebers to enter dungeon")
	phBotChat.Party(Command.CMD_EnterDungeon)

def handle_chat(t,player,msg):
	if(t != ChatType.CHAT_PARTY.value):
		return  #only care about party chat.
	if(player !=  str(QtBind.text(gui,gui_leaderName))): 
		LogMsg("not leader")
		return #only care about what leader says.
	if (Command.CMD_EnterDungeon.value in msg.lower()):
		LogMsg(f"charname {glb_char_data['name']} and leader name is {str(QtBind.text(gui,gui_leaderName))}")
		if(glb_char_data['name'] == str(QtBind.text(gui,gui_leaderName))):
			LogMsg("start dungeon for leader")
			Timer(0.5, secret_dungeon_enter, ()).start()
		else:
			Timer(4.0, secret_dungeon_enter, ()).start()

def GetItemByExpression(_lambda, start=0, end=0):
    inventory = get_inventory()
    items = inventory['items']
    
    if end == 0:
        end = inventory['size']
    
    for slot, item in enumerate(items):
        if start <= slot <= end:
            if item and _lambda(item['servername']):
                item['slot'] = slot
                return item
    return None

def SelectAncientHistoryScholarNPC(p):
	LogMsg("Selecting ancient history scholar")
	# = b'\x77\x01\x00\x00'
	opcode = 0x7045 #target opcode
	LogMsg(f'[{__name__}] └ data: {hexlify(p)}')
	inject_joymax(opcode, p, False)

def SelectSecretDungeon(isUpper):
	LogMsg("selecting the secret dungeon option")
	p = b'\xbd\x05\x00\x00\x02\x63\x01\x00\x00'
	if(not isUpper):
		p = b'\xbd\x05\x00\x00\x02\x64\x01\x00\x00'

	opcode = 0x705A
	LogMsg(f'[{__name__}] └ data: {hexlify(p)}')
	inject_joymax(opcode, p, False)

def sendDungeonEntry():
	LogMsg("entry to dungeon")
	p = b'\x01\x01'
	opcode = 0x3080
	LogMsg(f'[{__name__}] └ data: {hexlify(p)}')
	inject_joymax(opcode, p, False)

def GetNPCUniqueID(name):
	NPCs = get_npcs()
	if NPCs:
		name = name.lower()
		for UniqueID, NPC in NPCs.items():
			NPCName = NPC['name'].lower()
			if name in NPCName:
				return UniqueID
	return 0
# ______________________________ Events ______________________________ #
def joined_game():
	LogMsg("waiting for char data in background thread")
	load_char_data_inbackground() #this will ensure char data gets loaded even if the char_data is not available at the moment.
	
def teleported():
	LogMsg("getting player's current region")
	character_data = get_character_data()	
	region = character_data['region']
	global glb_entered_dungeon
	if(not glb_entered_dungeon): #check on each teleportation to see if we are in dungeon region.
		try:
			region_enum = REGION(region)
			if region_enum  in {REGION.UPPER_DUNGEON, REGION.LOWER_DUNGEON}:
				secret_dungeon_hunt
				LogMsg("secret dungeon region detected! more likely we are in the dungeon world!")
				region_enum = True
				Timer(1.0, secret_dungeon_hunt).start()
				glb_entered_dungeon = True
		except ValueError:
			LogMsg(f"While waiting for dungeon, unknown dungeon or town region ID {region} detected during teleport!")

	else: #check on each teleportation to see if we are out of dungeon region.
		try:
			region_enum = REGION(region)
			if region_enum not in {REGION.UPPER_DUNGEON, REGION.LOWER_DUNGEON}:
				stop_bot()
				Timer(1.0,secret_dungeon_complete).start()
				#Timerupperdungeon_complete() #we are out! secret dungeon must be complete
				glb_entered_dungeon = False
		except ValueError:
			stop_bot()
			Timer(1.0,secret_dungeon_complete).start()

def finished():
	LogMsg("#signal the background thread to finish.")
	glb_stop_event.set()

#______________________________Config_________________________________#
def CharInGame():
	global glb_char_data
	character_data = get_character_data()
	if character_data and "name" in character_data and character_data["name"]:
		LogMsg("char data is available")
		glb_char_data = character_data
	else:
		glb_char_data = None
		LogMsg("char data doesn't exist! trying to retrieve from bot")
	return character_data

def getPath():
	return get_config_dir() + pName + "/"

# Return character configs path (JSON)
def getConfig():
	global glb_char_data
	if(glb_char_data is None):
		glb_char_data = get_character_data()
	
	path = getPath() + pName + '_' + glb_char_data['server'] + '_' + glb_char_data['name'] + '.json'
	LogMsg(f"getConfig(): {path}")
	return path

# Load config if exists
def LoadConfig():
	if(CharInGame()):
		if not os.path.exists(getPath()):
			os.makedirs(getPath())
			LogMsg(f'Plugin: {pName} folder has been created')
		else:
			config = getConfig()
			LogMsg(str(config))
			if(os.path.exists(config)):
				data = {}
				with open(config,"r") as f:
					data = json.load(f)
				# Basic fields
				if "PartyLeader" in data:
					QtBind.setText(gui, gui_leaderName, data['PartyLeader'])
				if "PartySize" in data:
					QtBind.setText(gui, gui_partySize, data['PartySize'])
				if "MaxTries" in data:
					QtBind.setText(gui, gui_max_tries, data['MaxTries'])
				if "UpperProfile" in data:
					QtBind.setText(gui, gui_upper_dungeon_profile, data['UpperProfile'])
				if "LowerProfile" in data:
					QtBind.setText(gui, gui_lower_dungeon_profile, data['LowerProfile'])
				if "GatherSpot" in data:
					QtBind.setText(gui, gui_gatherspot_area_name, data['GatherSpot'])
				if "BuffSpot" in data:
					QtBind.setText(gui, gui_buffspot_area_name, data['BuffSpot'])
				if "HuntSpot" in data:
					QtBind.setText(gui, gui_huntspot_area_name, data['HuntSpot'])

				QtBind.setChecked(gui, gui_upper_checkbox, data.get('Upperchkbox', True))
				QtBind.setChecked(gui, gui_lower_checkbox, data.get('Lowerchkbox', False))

def SaveConfigIfJoined():
	if CharInGame():
		data = {
    		'PartyLeader': str(QtBind.text(gui,gui_leaderName)),
    		'PartySize': str(QtBind.text(gui,gui_partySize)),
			'MaxTries': str(QtBind.text(gui,gui_max_tries)),
			'UpperProfile': str(QtBind.text(gui,gui_upper_dungeon_profile)),
			'LowerProfile': str(QtBind.text(gui,gui_lower_dungeon_profile)),
			'GatherSpot': str(QtBind.text(gui,gui_gatherspot_area_name)),
			'BuffSpot': str(QtBind.text(gui,gui_buffspot_area_name)),
			'HuntSpot': str(QtBind.text(gui,gui_huntspot_area_name)),
			'Upperchkbox': QtBind.isChecked(gui,gui_upper_checkbox),
			'Lowerchkbox': QtBind.isChecked(gui,gui_lower_checkbox),
				}
		# Override
		with open(getConfig(),"w") as f:
			f.write(json.dumps(data, indent=4, sort_keys=True))
	else:
		LogMsg("test")

# Plugin loaded
LogMsg(f'Plugin: {pName} v{pVersion} succesfully loaded')
LoadConfig() #makes sure the plugin interface gets updated when refresh is pressed in plugins section of the bot