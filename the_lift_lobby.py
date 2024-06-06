import os
import time
import random
import logging
import argparse
import pygame, sys
from pygame.locals import *
from threading import Thread

M_NO_OF_FLOORS = 20
M_NO_OF_ELEVATORS = 5

class RunTimeInformation:
	def __init__(self):
		self.run_time_info_dict = {
		'no_of_floors': 8,
		'no_of_elevators': 3,
		'quit_called': False,
		'building_x0': 10,
		'building_y0': 10,
		'building_x1': 800,
		'building_y1': 600,
		'floor_data': [],
		'floor_length': 10,
		'elevator_data': [],
		'elevator_next_floors': [],
		}

	def get_rtm_data(self, key):
		value = self.run_time_info_dict[key]
		log.debug(f'get_rtm_data --> key: {key}, value: {value}')
		return value

	def set_rtm_data(self, key, value):
		log.debug(f'set_rtm_data --> key: {key}, value: {value}')
		self.run_time_info_dict[key] = value

class TheAvLiftLobby:
	def __init__(self):
		self.no_of_floors = M_NO_OF_FLOORS
		self.no_of_elevators = M_NO_OF_ELEVATORS
		self.rtm = RunTimeInformation()
		self.rtm.set_rtm_data('no_of_floors', self.no_of_floors)
		self.rtm.set_rtm_data('no_of_elevators', self.no_of_elevators)
		self.init_screen_size_for_animation()
		self.init_floor_data()
		self.init_elevator_data()
		self.animator = AvLiftLobbyAnimator(self.rtm)

	def main_run(self):
		log.info('Start the Elevators')
		self.animator.run_the_animation_launcher()
		elevator_next_floors = self.rtm.get_rtm_data('elevator_next_floors')
		log.info(f'elevator_next_floors: {elevator_next_floors}')
		for i in range(self.no_of_elevators):
			Thread(target = self.elevator_handler, args = (i+1,)).start()
		while(self.rtm.get_rtm_data('quit_called') == False):
			time.sleep(0.016)
			time.sleep(random.randint(1, 5))
			log.info('Start adding floors to go to')
			for i in range(len(elevator_next_floors)):
				if(len(elevator_next_floors[i]) > 4):
					log.info(f'Elevator {i+1} already has 4 in queue, skip adding floors')
					continue
				e = random.randint(1, 100)
				log.info(f'For elevator {i+1}, e: {e}')
				if(e > 60):
					random_floor = random.randint(1, self.no_of_floors)
					log.info(f'Add floor {random_floor} to elevator {i+1} list: {elevator_next_floors[i]}')
					elevator_next_floors[i].append(random_floor)

	def elevator_handler(self, elevator_no):
		log.info(f'Elevator handler for {elevator_no}')
		while(self.rtm.get_rtm_data('quit_called') == False):
			time.sleep(1)
			elevator_next_floors = self.rtm.get_rtm_data('elevator_next_floors')[elevator_no-1]
			log.info(f'elevator {elevator_no} next floors: {elevator_next_floors}')
			if(len(elevator_next_floors) < 1):
				time.sleep(1)
				continue
			log.info(f'Move elevator {elevator_no} to floor {elevator_next_floors[0]}')
			self.move_elevator(elevator_no = elevator_no, to_floor = elevator_next_floors[0])
			elevator_next_floors = elevator_next_floors[1:]
			raw_data = self.rtm.get_rtm_data('elevator_next_floors')
			raw_data[elevator_no-1] = elevator_next_floors
			self.rtm.set_rtm_data('elevator_next_floors', raw_data)

	def move_elevator(self, elevator_no, to_floor):
		floor_data = self.rtm.get_rtm_data('floor_data')
		elevator_data = self.rtm.get_rtm_data('elevator_data')
		target_y = floor_data[to_floor-1][1]
		current_y = elevator_data[elevator_no-1][2]

		if(target_y > current_y):
			incrementer = 1
		elif(target_y == current_y):
			incrementer = 0
			time.sleep(1)
			return
		else:
			incrementer = -1
		while True:
			time.sleep(0.005)
			current_y += incrementer
			elevator_data[elevator_no-1][2] = current_y
			self.rtm.set_rtm_data('elevator_data', elevator_data)
			if(target_y == current_y):
				time.sleep(1)
				return

	def init_screen_size_for_animation(self):
		w, h = pygame.display.set_mode((0, 0), pygame.FULLSCREEN).get_size()
		self.rtm.set_rtm_data('building_x0', 0)
		self.rtm.set_rtm_data('building_y0', 0)
		self.rtm.set_rtm_data('building_x1', w)
		self.rtm.set_rtm_data('building_y1', h)

	def init_floor_data(self):
		h = self.rtm.get_rtm_data('building_y1')
		floor_length = int(h/self.no_of_floors)
		floor_data = []
		for i in range(self.no_of_floors):
			floor_y_coordinate = floor_length*i
			floor_no = i+1
			temp_list = []
			temp_list.append(floor_no)
			temp_list.append(floor_y_coordinate)
			floor_data.append(temp_list)
		log.info(f'no_of_floors: {self.no_of_floors}')
		log.debug(f'building_y1: {h}')
		log.debug(f'floor_length: {floor_length}')
		self.rtm.set_rtm_data('floor_data', floor_data)
		self.rtm.set_rtm_data('floor_length', floor_length)
		for m in floor_data:
			print(f'floor_data: {m}')

	def init_elevator_data(self):
		screen_width = self.rtm.get_rtm_data('building_x1')
		elevator_temp_list = []
		elevator_next_floor_list = []
		for i in range(self.no_of_elevators):
			temp_list = []
			temp_list.append(i+1)
			w = int(self.rtm.get_rtm_data('floor_length')/2)
			h = self.rtm.get_rtm_data('floor_length')
			x = screen_width - (self.no_of_elevators - i)*w
			y = 0
			for elem in [x, y, w, h]:
				temp_list.append(elem)
			
			elevator_temp_list.append(temp_list)
			elevator_next_floor_list.append([])
		self.rtm.set_rtm_data('elevator_data', elevator_temp_list)
		self.rtm.set_rtm_data('elevator_next_floors', elevator_next_floor_list)
		for d in elevator_temp_list:
			log.info(f'elevator_data: {d}')

class AvLiftLobbyAnimator:
	def __init__(self, rtm):
		self.rtm = rtm
		pygame.init()
		pygame.font.init()
		my_font = pygame.font.SysFont('Comic Sans MS', 30)
		

	def run_the_animation_launcher(self):
		log.debug('Launch the animation')
		Thread(target = self.run_the_animation, args = ()).start()

	def run_the_animation(self):
		fps = 60
		anim_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
		screen_w = self.rtm.get_rtm_data('building_x1')
		screen_h = self.rtm.get_rtm_data('building_y1')
		log.debug(f'screen_w: {screen_w}, screen_h: {screen_h}')
		white = (255, 255, 255)
		black = (0, 0, 0)
		red   = [240, 10, 10]
		green = (10, 150, 10)
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == KEYUP: 
					if event.key == K_q:
						self.rtm.set_rtm_data('quit_called', True)
						pygame.quit()
						sys.exit()

			anim_surface.fill(white)

			anim_surface.lock()

			x0 = self.rtm.get_rtm_data('building_x0')
			y0 = self.rtm.get_rtm_data('building_y0')
			x1 = self.rtm.get_rtm_data('building_x1')
			y1 = self.rtm.get_rtm_data('building_y1')
			# log.debug(f'y0, y1: {y0}, {y1}')
			# log.debug(f'Draw Rect y0: {screen_h-y0}, rect_y1: {screen_h-y1}')
			pygame.draw.rect(anim_surface, black, pygame.Rect(x0, screen_h-y0, x1, y1), 3)
			floor_no_display_surface_list = []
			lift_arriving_display_surface_list = []
			for floor_data in self.rtm.get_rtm_data('floor_data'):
				y_coordinate = floor_data[1]
				floor_no = floor_data[0]
				# log.debug(f'Draw Line Line y_coord: {y_coordinate}, draw coord: {screen_h - y_coordinate}')
				pygame.draw.line(anim_surface, black, (x0, screen_h - y_coordinate), (x1, screen_h - y_coordinate), 3)
				
				my_font = pygame.font.SysFont('Comic Sans MS', int(self.rtm.get_rtm_data('floor_length')*0.5))
				text_surface = my_font.render(str(floor_no), False, black)
				floor_no_display_surface_list.append([text_surface, screen_h - y_coordinate - int(self.rtm.get_rtm_data('floor_length'))])

				my_font_2 = pygame.font.SysFont('Comic Sans MS', int(self.rtm.get_rtm_data('floor_length')*0.3))
				lift_no_to_print = ''
				elevator_next_floors = self.rtm.get_rtm_data('elevator_next_floors')
				for i in range(len(elevator_next_floors)):
					for floor in elevator_next_floors[i]:
						if(floor == floor_no):
							lift_no_to_print += f'L{i+1}   '
				text_surface_lift_no = my_font_2.render(lift_no_to_print, False, green)
				lift_arriving_display_surface_list.append([text_surface_lift_no, screen_h - y_coordinate - int(self.rtm.get_rtm_data('floor_length'))])

			for elevator_data in self.rtm.get_rtm_data('elevator_data'):
				elevator_no = elevator_data[0]
				x0 = elevator_data[1]
				y0 = elevator_data[2]
				w = elevator_data[3]
				h = elevator_data[4]
				# log.info(f'elevator {elevator_no}: x0: {x0}, y0: {y0}')
				# log.info(f'elevator {elevator_no} draw: x0: {x0}, y0: {screen_h-y0-h}')
				pygame.draw.rect(anim_surface, red, pygame.Rect(x0, screen_h-y0-h, w, h), 3)
			anim_surface.unlock()
			for text_surface in floor_no_display_surface_list:
				anim_surface.blit(text_surface[0], (20, text_surface[1]))
			for text_surface in lift_arriving_display_surface_list:
				anim_surface.blit(text_surface[0], (100, text_surface[1]))
			pygame.display.update()
			pygame.time.Clock().tick(fps)


if(__name__ == '__main__'):
	parser = argparse.ArgumentParser()
	parser.add_argument('--d', '--debug', dest='debug', action='store_true', help='Enable debug logging')
	args = parser.parse_args()

	log = logging.getLogger()
	ch = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s %(levelname)-7s [%(filename)s:%(lineno)3d] [%(threadName)s] %(message)s', '%d-%b-%y %H:%M:%S')
	log.setLevel(logging.DEBUG)
	if args.debug:
		ch.setLevel(logging.DEBUG)
	else:
		ch.setLevel(logging.INFO)
	ch.setFormatter(formatter)
	log.addHandler(ch)
	for k_file in ['stdout.txt', 'console.txt']:
		if(os.path.exists(k_file)):
			os.remove(k_file)
	fh = logging.FileHandler('stdout.txt')
	fh.setFormatter(formatter)
	fh.setLevel(logging.INFO)
	log.addHandler(fh)
	dh = logging.FileHandler('console.txt')
	dh.setFormatter(formatter)
	dh.setLevel(logging.DEBUG)
	log.addHandler(dh)

	TheAvLiftLobby().main_run()

