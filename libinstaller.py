from subprocess import Popen, PIPE
from collections import OrderedDict
import os
import sys
import json
import time

# импорт модуля 'colorama' происходит внизу скрипта
# импорт модуля 'tabulate' происходит внизу скрипта

PATH = os.path.dirname(sys.argv[0])
MODULES_PATH = os.path.join(PATH, 'Modules.txt')

RED = ''
CYAN = ''
GREEN = ''
WHITE = ''
YELLOW = ''
TABULATE = False

# Получает установление модули 
def _installed_modules():
	process = Popen('python -m pip freeze', stdout = PIPE, stderr = PIPE)
	out,err = process.communicate()
	if out:
		return set(out.decode('cp866').replace('\r','').strip('\n').split('\n'))
	else:
		print(YELLOW + '[!] Ошибка модуля \'freeze\'!')
		return set() # Для избежания вылета программы

# Сортирует словарь по длине списков в порядке спадания 
def _sorter(dict_to_sort):
	new_sorted_dict = OrderedDict()
	while dict_to_sort:
		max_len = 0
		for value in dict_to_sort:
			cur_len = len(dict_to_sort[value])
			if cur_len > max_len:
				max_len = cur_len
				keyname = value
		new_sorted_dict[keyname] = dict_to_sort.pop(keyname)
	# Создание списка модулей к установке по индексу. Пустая строка нужна для сдвига модуля в списке для соотвецтвия с его номером в таблице
	module_list = [''] 
	for modules in new_sorted_dict.values():
		module_list.extend(modules)
	return new_sorted_dict, module_list

# 
def print_table():
	if TABULATE:
		return _print_table()
	else:
		return _print_table_old()

# Выводит таблицу. Так меньше кода, красивее и надежнее
def _print_table():
	headers = ['Раздел', 'Библиотеки', '', '', '']
	list_to_print = []
	ind = 1 # Индекс товара с писке модулей
	for key in module_dict.keys():
		line = [key] # Запись имени секции для отобрадения в одной линии
		pos = 0 # Условный индекс модуля в списке
		for module in module_dict[key]:
			line.append('%i. %s' % (ind, module) )	
			if pos == 3:
				list_to_print.append(line) # Добавление готового ряда в список для печати
				line = [''] # Добавление пустой первой ячейки
				pos = 0 # Обнуление позиции модуля в списке 
		
			ind += 1
			pos += 1
		# Отсекает список с пустой ячейкой. Так выходит когда всего 3 модуля в сикции
		if len(line) > 1:
			list_to_print.append(line)
			
	print(CYAN + tabulate(list_to_print, headers, tablefmt = 'fancy_grid'))

# Старая версия используется в случае если пользователь использует версию питона неподдерживаемую библиотекой tabulate
# # Выводит таблицу
def _print_table_old():

	number = 1
	mx_len = 3

	lengths = [[0] * 4 for _ in range(30)]

	#Вычисление найбольшей длинны имени раздела
	for _row, section in enumerate(module_dict.keys()):
		lengths[_row][0] = len(section)

	#Вычисление найбольшей длинны имени модуля
	_pos = 1
	_row = 1
	for modules in module_dict.values():
		for name in modules:
			if _pos > 3:
				_pos = 1
				_row += 1
			lengths[_row][_pos] = len(name)
			_pos += 1
		_row += 1
		_pos = 1

	for h in range(4):
		l = [lengths[i][h] for i in range(len(lengths))]
		m_x = max(l)
		for i in range(len(lengths)):
			lengths[i][h] = m_x

	for num, section in enumerate(module_dict.keys()):

		modules = module_dict[section]
		str_len = 1 # Длинна строки в ячейках (от 1 до 3)
		fiprint = 0 # Флаг первой печати
		linebreak = 0 # Флаг переноса строки
		pos = 1

		line = '| %s: %s| ' % (section, ' ' * (lengths[num][0] - len(section) ) ) #
		for name in modules:
			if  pos == mx_len + 1:
				pos = 1
			line += '%i - %s %s| ' % (number, name, ' ' * (lengths[num][pos] - len(str(name)) + (2 - len(str(number)) )))

			if str_len == mx_len:
				linebreak = 1 # Есть перенос
				underscore_len = len(line) - 1 # Длинна подчеркивания. нужна после цикла 'for'

				if fiprint == 0: # Верх для первой строчки
					print(CYAN + '[m] ' + '-' * underscore_len )
				print(CYAN + '[m] ' + line)

				line = '|%s| ' % (' ' * (lengths[num][0] + 3) )
				str_len = 1 # Новая длинна строки
				fiprint = 1 # Первая печать
			else:
				str_len += 1 # 

			number += 1 # Автоподсчет номеров модулей
			pos += 1

		if str_len < mx_len and linebreak == 0:
			if num == 0: #Верх для первой строчки
				print(CYAN + '[m] ' + '-' * (len(line) - 1) )
			print(CYAN + '[m] ' + line)
			print(CYAN + '[m] ' + '-' * (len(line) - 1) )
		elif str_len < mx_len and linebreak == 1:
			line = '[m] %s' % line
			while str_len <= mx_len:
				if pos == mx_len + 1:
					pos = 1
				line += '%s| ' % (' ' * (lengths[num][pos] + 6))
				str_len += 1
				pos += 1
			print(CYAN + line)
			print(CYAN + '[m] ' + '-' * underscore_len )
		else:
			print(CYAN + '[m] ' + line)
			print(CYAN + '[m] ' + '-' * (len(line) - 1) )

		linebreak = 0 # Обновляем данные о переносе

# Получение списка модулей для установки
def get_command(params = None):

	# Возвращает только числа и существующие ключи
	def _filter(value):
		if module_dict.get(value, None): # Если значение есть в словаре
			return value
		elif value.lower() == 'all':
			return 'all'
		try:
			return int(value) # Отсеет все символы
		except ValueError:
			return 999 # В дальнейшем будет отсеено

	# Форматирует пользовательский ввод. C такого:   1, 2  3.4 5,  6 7, делает такое: 1 2 3 4 5 6 7
	def _format(_input):
		for char in (',', '.', ' '):
			for l in (3, 2, 1):
				_input = _input.replace(char * l, ' ')
		return _input

	# будет возвращен с номерами модулей для установки
	_tmp = set()

	# Если не были переданы индексы модулей, выводит таблицу и просит ввести номера модулей к установке
	if not params:

		print_table()
		print(CYAN + '[>] Нажмите клавишу \'enter\', или напишите \'all\' для установки ВСЕХ модулей.\n'
			' Для выборочной установки введите номера модулей с таблицы'\
			' \nТакже можно указать имя раздела и все библиотеки этого раздела будут установлены.')

		inp = _format(input('[<] ').strip())

		# Возвращает список всех модулей для установки
		if inp == '' or inp == 'all':
			return module_list[1:] # Убераем пустую строку
		elif inp == 'exit':
			return []
		elif inp == '--e':
			return []

		params = inp.split(' ')
	# Если были переданы номера модулей либо ключи секций
	params = _format(' '.join(params)).split(' ') # Склеивает список полученый с главного меню для автокорекции полученых данных
	params = list(map(_filter, params))
	# Перебор полученых имен и номеров
	for index in params:
		if isinstance(index, int):
			if int(index) in range(0, len(module_list)): # Отсеивает значения больше длинны списка, в том числе и 999 
				_tmp.add(module_list[index])

		elif isinstance(index, str) and index == 'all':
			return module_list[1:]

		elif isinstance(index, str):
			_tmp = _tmp | set(module_dict.get(index, None))

	return _tmp

# Сюда передается комманды для выполнения с помощью Popen
# При передаче соотвецтвующих комманд происходит установка 
# модуля 'colorama' и обновление 'pip' 
def pre_install(command):
	process = Popen('python -m pip install %s' % command, stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = False)
	out,err = process.communicate()

	if err:
		error = err.decode('cp866')
		if error == 'DEPRECATION' in error: # возникает в питоне 3.4
			pass
		
		elif 'ERROR: Package \'%s\' requires a different Python' % command in error:
			print(CYAN + '[!] Ошибка: ' + RED + 'Модуль \'%s\' не установливается для данной версии python' % command, file = sys.stderr)
		
		else:
			print('[!] Ошибка: Возникла ошибка при установки модуля: \'%s\' ' % command, file = sys.stderr)

	if out:
		output = out.decode('cp866')
		if 'Requirement already satisfied: %s'  % command in output:
			print('[i] Модуль: %s уже был установлен!' % command, file = sys.stdout)

		elif 'Successfully installed: %s' % command in output:
			if command == 'colorama':
				print('[i] Модуль \'colorama\' успешно установлен!')
			
			elif command == 'tabulate':
				print('[i] Модуль \'tabulate\' успешно установлен!')
			
			elif command == '--upgrade pip':
				print('[i] Пакетный менеджер \'pip\' успешно обновлен!')

			return True

# Объявление установщика
def installer(module_list):
	print(CYAN + '[i] Начало установки...')
	installed = 0
	collecting = 0

	if not module_list:
		print(RED + '[>] Статус: Установка была прервана вами!')
		return 0 # Для выхода с функции 

	for module in module_list:
		time.sleep(0.3) # Делает задержку после вывода статуса установки. Так более красиво
		print(CYAN + '[>] Статус: ' + GREEN + 'Начало установки %s...' % (module), file = sys.stdout )

		process = Popen('python -m pip install %s' % module, stdout = PIPE, stderr = PIPE, shell = False)
		out,err = process.communicate()

		if err:
			error = err.decode('cp866')
			if 'Retrying' in error:
				print(CYAN + '[!] Ошибка: ' + RED + 'Ошибка интернет-соединения при установке модуля: \'%s\' ' % module, file = sys.stderr)
			
			elif 'ERROR: No matching distribution found for %s' % module in error:
				print(CYAN + '[!] Ошибка: ' + RED + 'Модуль \'%s\' не установливается для данной версии python' % module, file = sys.stderr)
					
			elif 'WARNING: You are using pip version' in error:
				pre_install('--upgrade pip')

			else:
				print(CYAN + '[!] Ошибка: ' + RED + 'Ошибка установки модуля: \'%s\' ' % module, file = sys.stderr)
		if out:
			output = out.decode('cp866')

			if 'Requirement already satisfied: %s' % module in output:
				print(CYAN + '[>] Модуль: ' + YELLOW + '\'%s\' уже был установлен!' % (module))
				collecting += 1

			if 'Successfully installed %s' % module in output:
				print(CYAN + '[>] Модуль: \'%s\' успешно установлен!' % (module), file = sys.stdout  )
				installed += 1

	if installed == len(module_list):
		print(CYAN + '[>] Все %i модулей установлено успешно!' % (installed) )

	elif collecting == len(module_list) and installed == 0:
		print(CYAN + '[>]' + YELLOW + ' Все модули уже были установлены!')

	elif installed == 0 and collecting == 0:
		print(CYAN + '[>]' + RED + ' Не установлено ни одного модуля по неизвестной причине!', file = sys.stderr)

	else:
		print(CYAN + '[>]' + YELLOW + ' Установлено %i модулей из %i' % (installed, len(module_list) - 1) )

# Проверка версии pip
def check_pip_update():
	process  = Popen('python -m pip install --upgrade pip', stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = True)
	out, err = process.communicate()
	if out:
		output = out.decode('cp866')
		if 'Requirement already up-to-date: pip' in output:
			pip_version()
		else:
			return True

# Проверка версии pip
def pip_version():
	process  = Popen('python -m pip --version', stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = True)
	out, err = process.communicate()
	if out:
		output = out.decode('cp866')
		# Получение версии в виде строки, отбор первой части с номером версии
		# Разбиваем на список, конвертируем строки в числа и пакуем их в кортеж
		version = tuple(map(int, output.split(' ')[1].split('.') ))
		print('[i] Версия pip: %i.%i.%i' % version)

# Запуск нового процеса autoinstaller.py
def restart():
	print('[!] Рестарт скрипта...')
	os.system('python "%s"' % sys.argv[0])
	exit()

# 
def help():
	help_list = [
	'Для справки введите комманду:' + CYAN + ' \'help\'' + YELLOW + ' или ' + CYAN + '\'--h\' ',
	'Для завершения скрипта введите:' + CYAN + ' \'exit\'' + YELLOW + ' или ' + CYAN + '\'--e\' ',
	'Для вывода таблицы модулей введите:' + CYAN + ' \'table\'' + YELLOW + ' или ' + CYAN + '\'--t\' ',
	'Для добавления нового модуля в таблицу введите:' + CYAN + ' \'append\'' + YELLOW + ' или ' + CYAN + '\'--a\' ',
	'Формат комманды: ' + WHITE + '[<] --a key1:value1' + YELLOW + ' или ' + WHITE + '[<] append key1:value1, key2:value2, ..',
	'Для удаления значения введите: ' + WHITE +  '[<] --r key1:value1 ' + YELLOW + ' или ' + WHITE +  ' [<] remove key1:value1, key2:value2, ..',
	'Также возможно удаление по имени модуля или по назварию раздела (будет удален весь раздел).',
	'Для запуска установки введите:' + CYAN + ' \'install\'' + YELLOW + ' или ' + CYAN + '\'--i\' ',
	'После комманды в консоль будудет выведена таблица с модулями.',
	'Для выбора модулей можно указывать номера модулей или имя раздела',
	'Если выбраный номер модуля входит в указаный раздел, модуль повторно не попадает в список для установки.',
	'Чтобы выйти из выбора модулей введите комманду:' + CYAN + '\'exit\'.' + YELLOW + ' или ' + CYAN + '\'--e\' ',
	'*Также можно передать параметрами номера модулей или названия разделов',
	'Коммандой' + CYAN + ' \'dump\'' + YELLOW + ' или ' + CYAN + '\'--d\'' + YELLOW + ' можно сохранить имена установленых модулей для дальнейшей их',
	'передачи другу или для переноса на другой ПК. Можно задать имя файла указав его после комманды,',
	'тогда модули будут сохранены в папке скрипта',
	'По умолчанию файл дампа находится в директории скрипта с именем ' + CYAN + '\'Requirement.txt\' ',
	'Для автоматической установки модулей с файла дампа введите комманду: ' + CYAN + '\'load\'' + YELLOW + ' или ' + CYAN + '\'--l\'', 
	'По умолчанию файл дампа: ' + CYAN + '\'Requirement.txt\'' + YELLOW + ', указав имя файла (без пути к нему) данны будут загружаться с него.']

	for line in help_list:
		print(YELLOW + '[i] ' + line)

# Сохранение списка установленых модулей для дальнейших их установки
def dump_modules(filename = None):
	if filename:
		filename = filename = os.path.join(PATH, filename)
	else:
		filename = os.path.join(PATH, 'Requirement.txt')

	print(CYAN + '[>] Начало сохранения модулей...')
	process = Popen('python -m pip freeze', stdout = PIPE, stderr = PIPE)
	out,err = process.communicate()
	if err:
		print(RED + err.decode('cp866'))
	if out:
		output = out.decode('cp866')
		output = output.replace('\r','').strip('\n').split('\n')
		for name in output:
			print(YELLOW + '[m] ' + name)
		
		with open(filename, mode = 'w') as file:
			json.dump(output, file)

		print(CYAN + '[!] Файл дампа: \'%s\'' % filename)
		print(YELLOW + '[>] Сохранено модулей: %i шт.' % (len(output) - 1) )

# Установка сохраненных модулей в файлеы
def load_modules(filename = 'None'):
	if os.path.exists(os.path.join(PATH, filename)):
		filename = os.path.join(PATH, filename)
	else:
		filename = os.path.join(PATH, 'Requirement.txt')

	filename = os.path.join(PATH, 'Requirement.txt')
	if os.path.exists(filename):
		print(CYAN + '[>] Найден файл дампа: \'%s\'' % filename)
		with open(filename, mode = 'r') as file:
			loaded_modules = set(json.load(file))

			to_install = loaded_modules - _installed_modules() # Вычет уже установленых модулей

		if len(to_install) > 0:		
			print(YELLOW + '[>] Загружено модулей: %i шт.' % (len(modules) - 1) )
			installer(modules)
		else:
			print(YELLOW + '[>] Все модули уже установлены!')			
	else:
		print(RED + '[>] Файл дампа: \'%s\', не найден!' % filename )

# Проверка могут ли быть данные загружены
def can_be_load_data():
	if os.path.exists(MODULES_PATH):
		return True
	return False

# Загрузка расширеного пользователем словаря модулей.
def load_data():
	with open(MODULES_PATH, mode = 'r') as file:
		return _sorter(json.load(file))

# Если не найден файл 'Modules.txt', возвращает базовый словарь модулей 'base_module_dict'
def reestablish_data():
	print(YELLOW + '[>] Загружен базовый словарь!')
	# Базовый словарь модулей доступных для установке
	base_module_dict = {
	'network':  ['wget', 'requests', 'beautifulsoup4', 'newspaper3k'],
	'install':  ['pyinstaller', 'py2exe', 'uncompyle6', 'unpy2exe', 'cx_Freeze'],
	'useful':   ['datetime', 'howdoi', 'uuid', 'simplejson', 'Delorean'],
	'cmd':      ['sh', 'emoji', 'Prettytable'],
	'other':    ['zip', 'Fuzzywuzzy'],
	'os':       ['winshell', 'pywin32', 'virtualenv', 'pyautogui'],
	'dataproc': ['Theano', 'matplotlib', 'pandas', 'numpy', 'scipy'],
	'ui':       ['Kivy', 'PySide2', 'PySide', 'Eel', 'wxPython'],
	'telegram': ['aiogram', 'pyTelegramBotAPI'],
	'images':   ['Pillow'],
	'neuralnet':['tensorflow', 'Keras', 'scikit-learn'],
	'webdev':   ['Flask', 'Django', 'dash'],
	'games':    ['pygame', 'arcade']}

	return _sorter(base_module_dict)

# Сохранение словаря модулей 
def save_data(dict_name):
	try:
		with open(MODULES_PATH, mode = 'w') as file:
			json.dump(dict_name, file)
		print(CYAN + '[>] Данные успешно обновлены!')
		# Обновление списка и словаря в программе
		update_data()
	except:
		print(RED + '[!] Произошла ошибка при сохранении модулей!')

# Обновление списка и словаря после изменений в словаре
def update_data():
	global module_dict, module_list
	module_dict, module_list = load_data()

# Добавление модулей пользователем в 'module_dict'
def append_module(names):
	global module_dict

	if len(names) == 0:
		print(CYAN + '[>] Формат ввода: \'раздел\':\'значение\' \'раздел\':\'значение\'')
		names = input('[<] ').strip().split(' ')

	for name in names:
		name = name.split(':')

		if len(name) == 2:
			key, value = name

			modules = module_dict.get(key, None)

			if modules:
				modules.append(value)
			else:
				modules = [value]

			module_dict.setdefault(key, modules)
			print(CYAN + '[>] Значение: ' + YELLOW + value + CYAN + ' добавлено в раздел: ' + YELLOW + key ) 
	# Сохраняет измененный словарь после всех изменений
	save_data(module_dict)	

# Удаление модулей пользователем в 'module_dict'
def remove_module(names):
	global module_dict

	if len(names) == 0:
		print(CYAN + '[>] Формат ввода: \'раздел\':\'значение\' \'раздел\':\'значение\'')
		names = input('[<] ').strip().split(' ')

	for name in names:
		name = name.split(':')
		# Если передано пару раздел:модуль
		if len(name) > 1:
			key, value = name

			modules = module_dict.get(key, None)
			if modules:
				modules.pop(modules.index(value)) # Если удаляймое значение является последним в разделе
				if len(modules) == 0:
					module_dict.pop(key)
					print(CYAN + '[>] Удалено раздел: ' + YELLOW + key) 
				else:
					module_dict[key] = modules
					print(CYAN + '[>] Значение: ' + YELLOW + value + CYAN + ' удалено с раздела: ' + YELLOW + key)
			else:
				print(RED + '[!] Ключ: %s не существует!' % key)
		# Если для удаления передано имя модуля или раздел
		elif len(name) == 1:
			modules = module_dict.get(name[0], None)
			if modules:
				del module_dict[name[0]] # Удаляет раздел
				print(CYAN + '[>] Удалено раздел: ' + YELLOW + name[0] + CYAN + '. Были удалены следущие модули: ' + YELLOW + ', '.join(modules))
			else:
				for key in [k for k in module_dict.keys()]:
					if name[0] in module_dict[key]:
						modules = module_dict.get(key, None)
						if modules:
							modules.pop(modules.index(name[0]))
							if modules:
								module_dict[key] = modules # Обновление спуска модулей в словаре
								print(CYAN + '[>] Значение: ' + YELLOW + name[0] + CYAN + ' удалено!') 
							else:
								del module_dict[key]
								print(CYAN + '[>] Раздел: ' + YELLOW + key + CYAN + ' удален!')
	# Сохраняет измененный словарь после всех изменений
	save_data(module_dict)

# 
if __name__ == '__main__':
	print('[i] Вас привецтвует libinstaller модулей 1.0.0')
	print('[i] Ваша версия питона: %i.%i.%i' % sys.version_info[0:3])	

	if sys.version_info < (3, 0, 0):
		print('[i] Скрипт написан на версии python: 3+, ваша версия: %i.%i.%i' % sys.version_info[0:3])
		print('[i] Вы можете продолжить выполнение скрипта на свой страх и риск.')

	# Запуск проверки версии pip #19.3.1 последняя
	if check_pip_update():
		print('[i] требуется обновить pip')
		pre_install('--upgrade pip')

	try:
		from colorama import Fore, init
		init(autoreset = True)
		RED = Fore.RED
		CYAN = Fore.CYAN
		GREEN = Fore.GREEN
		WHITE = Fore.WHITE
		YELLOW = Fore.YELLOW
	except:
		print('[!] Модуль \'colorama\' не установлен!')
		if pre_install('colorama'):
			restart() #! Костыль. Перезапуск скрипта для импорта модуля 'colorama'

	try:
		from tabulate import tabulate
		TABULATE = True
	except:
		print('[!] Модуль \'tabulate\' не установлен!')
		if pre_install('tabulate'):
			restart() #! Костыль. Перезапуск скрипта для импорта модуля 'tabulate'
		else:
			TABULATE = False

	# module_dict и module_list глобальные переменные
	# Если файл Modules.txt существует загружает данные с него
	if can_be_load_data():
		module_dict, module_list = load_data()
	# Вернет базовый словарь и сохранит его
	else:
		module_dict, module_list = reestablish_data()
		save_data(module_dict)

	print('[i] Для получения справки введите комманду \'help\'')
	while True:
		print(CYAN + '[>] Введите комманду:')

		command = input('[<] ').strip().split()

		if command:
			command[0] = command[0].lower() # Превидение комманды к нижнему регистру 

		if len(command) > 0:
			if command[0] in ('--h', 'help'):
				help()
			elif command[0] in ('--e', 'exit'):
				exit()
			elif command[0] in ('--t', 'table'):
				print_table()
			elif command[0] in ('--i', 'install'):
				if len(command) > 1:
					installer(get_command(command[1:]))
				else:
					installer(get_command())
			elif command[0] in ('--a', 'append'):
				append_module(command[1:])
			elif command[0] in ('--r', 'remove'):
				remove_module(command[1:])
			elif command[0] in ('--d', 'dump'):
				if len(command) > 1:
					dump_modules(command[1])
				else:
					dump_modules()
			elif command[0] in ('--l', 'load'):
				if len(command) > 1:
					load_modules(command[1])
				else:
					load_modules()
			else:
				print(RED + '[!] Не удалось распознать комманду \'%s\' !' % ' '.join(command))


