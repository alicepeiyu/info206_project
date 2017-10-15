from collections import OrderedDict
from itertools import takewhile, zip_longest
from os import listdir, remove
from os.path import join, isfile, splitext, basename
import webbrowser
import pickle
from collections import defaultdict
import readline
import urllib.request
import urllib.parse
import re

#crawled data is stored in pickle files
f = open("data_tags.pkl", 'rb')
data = pickle.load(f)

file = open("data_ing.pkl", 'rb')
ing_list = pickle.load(file)
ing_list = [x.strip(' ') for x in ing_list]

class MyCompleter(object):  # Custom completer

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                   if text in s]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None

#-------------------------------------------------------------------------------

SUBDIR = 'recipes'

tags = {}
ingredients = []
preference_selection = ['allrecipes.com']
video_selection = ''

completer = MyCompleter(ing_list)
readline.set_completer(completer.complete)
readline.parse_and_bind('tab: complete')
for kw in ing_list:
    readline.add_history(kw)

#main function where user is prompted to input the list of ingredients that will be stored in a list
def main():
    global ingredients
    print('Welcome To portFOODlio!\nYour own personalized recipe portfolio!')
    print('\nAre you hungry but have no clue as to what to cook?\nNo worries! \nJust provide us with the list of ingredients you would like to incorporate in a dish and we will do the rest for you!')
    ing = input("\nEnter the list of ingredients (comma seperated): ")
    ingredient = ing.split(',')
    ingredients.extend(ingredient)
    recipe_preference()

#-------------------------------------------------------------------------------
#function where user is prompted to select the recipe preference
def recipe_preference():
    print('\nUse the numbers to navigate the menu.')
    print('Please choose your recipe preference.')
    options = {'1': category,
               '2': world_cuisine,
               '3': no_preference,
               '4': quit}
    for key in sorted(options, key=int):
        print('{} - {}'.format(key, get_title(options[key].__name__)))
    while True:
        choice = input('> ')
        if choice in options:
            options[choice]()
            break
        else:
          print("Invalid selection. Please enter another number: ")
#-------------------------------------------------------------------------------
#function that is executed when the user selects 'category' for recipe preference
def category():
    global video_selection
    print('\nUse the numbers to navigate the menu.')
    print('Please choose a category for your recipe.')
    options = {'1': 'Appetizers and Snacks',
               '2': 'Breakfast and Brunch',
               '3': 'Main Dish',
               '4': 'Desserts',
               '5': 'Drinks',
               '6': 'salad',
               '7': 'Fruits and Vegetables',
               '8': 'Side Dish',
               '9': 'Soups, Stews and Chili',
               '10': 'Go Back to Preference Selection',
               '11': 'Quit'}
    for key in sorted(options, key=int):
        print('{} - {}'.format(key, get_title(options[key])))
    while True:
        choice = input('> ')
        if choice == '10':
          recipe_preference()
        elif choice == '11':
          quit()
        else:
          tags['category'] = options[choice]
          preference_selection.append(options.get(choice))
          video_selection = ' '.join(ingredients + preference_selection)
          recipe_options_category()
          break

#-------------------------------------------------------------------------------
#function that is executed when the user selects 'world cuisine' for recipe preference
def world_cuisine():
    global video_selection
    print('\nUse the numbers to navigate the menu.')
    print('Please choose a world cuisine for your recipe.')
    options = {'1': 'Chinese',
               '2': 'French',
               '3': 'German',
               '4': 'Greek',
               '5': 'Indian',
               '6': 'Japanese',
               '7': 'Korean',
               '8': 'Lebanese',
               '9': 'Pakistani',
               '10': 'Spanish',
               '11': 'Thai',
               '12': 'Italian',
               '13': 'Mexican',
               '14': 'Latin American',
               '15': 'Middle Eastern',
               '16': 'Go Back to Preference Selection',
               '17': 'Quit'}
    for key in sorted(options, key=int):
        print('{} - {}'.format(key, get_title(options[key])))
    while True:
        choice = input('> ')
        if choice == '16':
          recipe_preference()
        elif choice == '17':
          quit()
        elif choice in options:
            tags['world_cuisine'] = options[choice]
            preference_selection.append(options.get(choice))
            video_selection = ' '.join(ingredients + preference_selection)
            recipe_options_world()
            break
        else:
          print("Invalid selection. Please enter another number: ")
#-------------------------------------------------------------------------------
#function that is executed when the user selects 'no preference' for recipe preference
def no_preference():
    tags['no_preference'] = 0
    recipe_options_category()

#-------------------------------------------------------------------------------
#function is executed to prompt user to either view or download recipe if chosen from category. 
def recipe_options_category():
    print(tags)
    print('\nUse the numbers to navigate the menu.')
    options = {'1': view_recipes,
               '2': view_youtube_recipe,
               '3': go_back_to_category_selection,
              '4': quit}
    for key in sorted(options, key=int):
        print('{} - {}'.format(key, get_title(options[key].__name__)))
    while True:
        choice = input('> ')
        if choice in options:
          options[choice]()
          break
        else:
          print("Invalid selection. Please enter another number: ")
#-------------------------------------------------------------------------------
#function is executed to prompt user to either view or download recipe if chosen from world cuisine. 
def recipe_options_world():
    print(tags)
    print('\nUse the numbers to navigate the menu.')
    options = {'1': view_recipes,
               '2': view_youtube_recipe,
               '3': go_back_to_world_cuisine_selection,
              '4': quit}
    for key in sorted(options, key=int):
        print('{} - {}'.format(key, get_title(options[key].__name__)))
    while True:
        choice = input('> ')
        if choice in options:
          options[choice]()
          break
        else:
          print("Invalid selection. Please enter another number: ")

#-------------------------------------------------------------------------------
#function to navigate back to category options
def go_back_to_category_selection():
  category()
#-------------------------------------------------------------------------------
#function to navigate back to world cuisine options
def go_back_to_world_cuisine_selection():
  world_cuisine()
#-------------------------------------------------------------------------------
#function that is executed when the user selects 'view recipe'. web browser opens to the recipe of choice.
def view_recipes():
    ing_count = defaultdict(int)
    for k,v in data.items():
        for ing in ingredients:
            if ing in ';'.join(v['ing']):
                ing_count[k] += 1
                if (('world_cuisine' in tags.keys() and \
                    tags['world_cuisine'] in ';'.join(v['tags'])) or ('category' in tags.keys() and tags['category'] in ';'.join(v['tags'])) or \
                    ('no_preference' in tags.keys())):
                    ing_count[k] += len(ingredients)
    ing_match = sorted(ing_count, key=lambda k: (ing_count[k]*1.0)/len(data[k]), reverse=True)
    for idx in range(0, len(ing_match), 5):
        for j in range(idx, idx + 5):
            print(j - idx + 1,'- Link:' , ing_match[j])#, '\nMeta : ' , data[ing_match[j]])
        opt = int(input('\nEnter the number for the recipe you would like to view or -1 for more recipes?'))
        if opt == -1:
            continue
        else:
            webbrowser.open(ing_match[(idx + opt - 1)])
            quit(); break

def quit():
    exit()
#-------------------------------------------------------------------------------
#function executed when user wants to view YouTube recipe
def view_youtube_recipe():
    query_string = urllib.parse.urlencode({"search_query" : video_selection})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    webbrowser.open("http://www.youtube.com/watch?v=" + search_results[0])
#-------------------------------------------------------------------------------

def get_file(prompt):
    # files = tuple(name for name in
    #               (join(SUBDIR, name) for name in listdir(SUBDIR))
    #               if isfile(name))
    # for index, path in enumerate(files, 1):
    #     print('{}) {}'.format(index, get_name(path)))
    # print('Type in the number of the recipe you '
    #       'would like to view and press enter.')
    # return files[int(input('> ')) - 1]
    print('get file')

def get_name(path):
    # return get_title(splitext(basename(path))[0])
    print('get name')

def get_title(name):
    return name.replace('_', ' ').title()

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

#-------------------------------------------------------------------------------
#function that is executed when the user selects 'view youtube recipe'. web browser opens to the recipe of choice.
#def view_youtube_recipes():
    # raise NotImplementedError()
 #   print('Explore More Recipes')
  #  print('Use the numbers to navigate the menu.')
   # options = {'1': from_youtube,
    #           '2': from_masterchef,
     #          '3': quit,}
    #for key in sorted(options, key=int):
    #    print('{}) {}'.format(key, get_title(options[key].__name__)))
    #while True:
     #   choice = input('> ')
      #  if choice in options:
       #     options[choice]()
        #    break

    # webbrowser.open('https://www.youtube.com/user/allrecipes')

