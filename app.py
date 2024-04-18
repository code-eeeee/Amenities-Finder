from geopy.geocoders import Nominatim
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView, MapMarker
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.progressbar import ProgressBar
from kivy.properties import ObjectProperty
from kivy.properties import BooleanProperty
from kivy.graphics import Rectangle, Color, InstructionGroup
from kivy.lang import Builder
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from googlesearch import search
from fake_useragent import UserAgent



from kivy.app import App
from kivy.uix.textinput import TextInput
import osmnx as ox
import pandas as pd
import time
import threading
import tensorflow as tf
import numpy as np
import keras
import math
from keras.preprocessing.text import tokenizer_from_json
import json 
tokenizer = keras.preprocessing.text.Tokenizer()
pad_sequences = keras.preprocessing.sequence.pad_sequences
import webbrowser
from kivy.animation import Animation
from kivy.clock import Clock


try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")
 






Builder.load_file("ui.kv")

resturarnt_checkbox = ObjectProperty()
retail_checkbox = ObjectProperty()
church = ObjectProperty()
social_facility = ObjectProperty()
clothes_checkbox = ObjectProperty()
class_1 = ObjectProperty()
class_2 = ObjectProperty()
map_view = ObjectProperty()
info = ObjectProperty()
control_panel = ObjectProperty()
distance_picker = ObjectProperty()
pb = ObjectProperty()
close = ObjectProperty()
opener = ObjectProperty()
status = ObjectProperty()
indicator = ObjectProperty()
loadingscreen = ObjectProperty()
mapscreen = ObjectProperty()
screenmanager = ObjectProperty()
latitude = ObjectProperty()
longitude = ObjectProperty()
errormessage = ObjectProperty()
text_input = ObjectProperty()
locator = ObjectProperty()
address = ObjectProperty()
min = ObjectProperty()
max = ObjectProperty()
range = ObjectProperty()

locations = {}
passed_link_dict = {}

ua = UserAgent()
user_agent = ua.random
chrome_options = Options()

chrome_options.add_argument('--user-agent=f"{user_agent}"')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

global checker
checker = False


from functools import partial

list = [39.95145,-75.15669]
global presses
presses = 0
global double_check
double_check = 0
        
class Controller(FloatLayout):
    def do_action(self):

        print("meep")
       
        self.link_dict = {}
        
        passed_dict = {}
        self.markers = []
        self.category = 0

        self.coordinate = tuple(list)
        dict = {"shop": [], "amenity": []}
        cont = False

        global point
        point = MapMarker(lat=list[0], lon=list[1])
        self.map_view.add_widget(point)
        
        
        def processing(): 
            
            if self.retail_checkbox.active == True:
                dict["shop"].append("supermarket")
            if self.clothes_checkbox.active == True:
                dict["shop"].append("clothes")
            if self.resturarnt_checkbox.active == True:
                dict["amenity"].append("restaurant")
                dict["amenity"].append("fast_food")
            if self.church.active == True:
                dict["amenity"].append("place_of_worship")
            if self.social_facility.active == True:
                dict["amenity"].append("social_facility")
            
            try:
                number_of_locations =  int(self.text_input.text)
            except:
                number_of_locations = 5
            
            try:
                supermarket = ox.features_from_point(self.coordinate, tags=dict, dist= self.distance).head(number_of_locations)
            except:
                print("waaa")
                Clock.schedule_once(self.error_message, 1)
                self.cont = False
            else:
                self.cont = True
                
            if self.cont == True:
                service_points = supermarket[supermarket.geom_type == "Point"]
                print(len(service_points))
                unique_names = service_points['name'].unique()
                locs = zip(service_points.geometry.y, service_points.geometry.x)
              
                self.locations = {}
                for name, long in zip(unique_names, locs):
                    self.locations[name] = long
                self.info.clear_widgets()
                supermarket_names = unique_names.astype(str)
                print(supermarket_names)
                sources_number = len(unique_names)
                self.pb.max = sources_number   

                

                
                threading.Thread(target=self.webscrapper, args=(supermarket_names,)).start()

                
            
                

                    
                
                
           
        

        if self.class_1.active == True :
            self.category = 1
            
            processing()
        elif self.class_2.active == True:
            self.category = 0
            processing()

    def location(self, indicator):
        
        if indicator == "latitude":
            
            latitude = float(self.latitude.text)
            list[0] = latitude
            print(list)
            
        if indicator == "longitude":
            longitude = float(self.longitude.text)
            list[1] = longitude
            print(list)
        if indicator == "text_input":
            value = self.text_input.text
            if not value.isdigit():
                self.text_input.text = "Type another value"
        if indicator == "min":
            value = self.min.text
            if not value.isdigit():
                self.min.text = "Type another value"
            else:
                value = int(value)
                self.range.min = value
                self.distance_picker.text = str(value)
                self.range.value = value     
                print(self.range.value)
        if indicator == "max":
            value = self.max.text
            if not value.isdigit():
                self.max.text = "Type another value"
            else:
                value = int(value)
                self.range.max = value
                self.distance_picker.text = str(self.range.min )
                self.range.value = self.range.min 
          

    def slider(self, value):
        self.distance = value
        self.distance = math.ceil(self.distance)
        self.distance_picker.text = str(self.distance)
        print(self.distance)

    def process_supermarket_names(self,dt):
        print("tehehe")
        self.pb.value += 1
        self.map_view.center_on(list[0], list[1])  # Center the map on the specified coordinates
        self.map_view.zoom = 16
        if self.pb.value == self.pb.max:
            self.pb.opacity = 1
            self.indicator.text = "Searching websites..."
            self.pb.value = 0
            threading.Thread(target=self.neural_network).start()
    

    
    def websitte_handler(self, dt):
        self.pb.value += 1

    def neural_network(self):
       
        
        
        for key in self.link_dict.keys():
            phrases = []
            link = self.link_dict[key]

            driver = webdriver.Chrome(options=chrome_options) 
            driver.get(link)

                    # Wait for the page to fully load (adjust the time as needed)
            driver.implicitly_wait(10)

            html_content = driver.page_source
            driver.quit()
            related_phrases = []
                    

            with open(r"C:\Users\Kodi\.vscode\Projects\Food Insecuirty App\FinalWork\words.json", 'r', encoding='utf-8') as json_file:
                tokenizer_data = json.load(json_file)
                tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_data)



            interpreter = tf.lite.Interpreter(model_path=r"C:\Users\Kodi\.vscode\Projects\Food Insecuirty App\FinalWork\model.tflite")
            interpreter.allocate_tensors()
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            max_sequence_length = 10

            soup = BeautifulSoup(html_content, "html.parser")
            for paragraph in soup.find_all(string=True):
                phrase = [paragraph]
                print(phrase)
                new_sequence = tokenizer.texts_to_sequences(phrase)
                new_padded_sequence = pad_sequences(new_sequence, maxlen=max_sequence_length, padding="post", truncating="post")
                input = new_padded_sequence.astype(np.float32)

                num_classes = 3  
                prediction = np.empty((1, num_classes), dtype=np.float32)

                interpreter.set_tensor(input_details[0]['index'], input)
                interpreter.invoke()
                prediction = interpreter.get_tensor(output_details[0]['index'])


                highest_num = 0
                for value in prediction[0]:
                    print(value)
                    if value > highest_num:
                        highest_num = value

                print(self.category)
                divison = np.where(prediction[0] == highest_num)[0]
                if divison == self.category:
                    related_phrases.append(phrase)
                    phrases.append(phrase)

            print(phrases)
            if len(phrases) > 1:    
                extracting_text = []
                
                for text in phrases:
                    string = text[0]
                    print(string)
                    if string not in extracting_text:
                        extracting_text.append(string)
                self.event = Clock.schedule_once(partial(self.make_button,key, extracting_text,), .1)

                passed_link_dict[key] = link
                print(key)
                print(link)
                
                print(self.locations[key])
                lat, lon = self.locations[key]
                Clock.schedule_once(partial(self.marker_maker,lat,lon), .1)
            Clock.schedule_once(self.websitte_handler, .1)
        print(passed_link_dict)
        if len(passed_link_dict) == 0:
            Clock.schedule_once(self.error_message, 1)
        Clock.schedule_once(self.reset, 1)
    def close_window(self):
        self.control_panel.opacity = 0 
        self.info.size_hint = (.15, 1) 
        self.close.disabled = True
        self.opener.opacity = 1
        self.opener.disabled = False           

    def open_window(self):
        self.opener.disabled = True
        self.opener.opacity = 0
        self.control_panel.opacity = 1 
        self.info.size_hint = (.15, .8) 
        self.close.disabled = False
 
    def reset(self, dt):
        self.status.opacity = 0
        self.pb.opacity = 1
        self.pb.value = 0
        self.indicator.text = "Loading Links..."

    def set_up(self, dt):
        print(self.pb.max)
        self.status.opacity = 1

    def menu_selector(self, menu):
        if menu == "screen1":
            self.screenmanager.transition.direction = "right"
        else: 
            self.screenmanager.transition.direction = "left"
        self.screenmanager.current = str(menu)
        

    
    def webscrapper(self, supermarket_names):
        Clock.schedule_once(self.set_up, .1) 
        for name in supermarket_names:
            for j in search(name, num_results=1):
                if j:
                    if name != "nan":
                        self.link_dict[name] = j
                        print(self.link_dict)
            Clock.schedule_once(self.process_supermarket_names, .1)           

    def trigger(self,instance, value):
        if value == True and instance == "D":
            self.class_2.active = False
        if value == True and instance == "F":
            self.class_1.active = False

    def marker_maker(self, lat, lon, dt):
        self.marker = MapMarker(lat=lat, lon=lon, source = r"Food Insecuirty App\FinalWork\marker_2.png")  # Add each café as a marker on the map
        self.map_view.center_on(lat, lon)
        self.map_view.zoom = 18
        self.markers.append(self.marker)
        self.map_view.add_widget(self.marker)


    def make_button(self, key,extracting_text, dt):
        leftovers = ""
        for text in extracting_text:
            leftovers = leftovers + ", " + str(text)
        text = str(key) + "," + str(leftovers)
        self.label = Button(text = text,text_size= (self.width/10, None), halign = "center", valign = "middle")
        self.info.add_widget(self.label)
        self.label.bind(on_press=self.initiate)
        
        Clock.unschedule(self.event)
            
    
    def initiate(self, instance):
        chopped = instance.text.rsplit(",")
        finder = chopped[0]
        lin = passed_link_dict[finder]
        webbrowser.open(lin)  
    
    def error_message(self, dt):
        print("y")

        self.errormessage.opacity = 1
        self.errormessage.text = "Sorry No Search Results! Try To Expand Your Search!"


        slide_in_animation = Animation(pos_hint={"center_x": .5, "center_y": 0.5}, duration=2)

        slide_out_animation = Animation(pos_hint={"center_x": 1.5, "center_y": .5}, duration=2)


        def start_slide_out_animation(dt):
            slide_out_animation.start(self.errormessage)

        slide_in_animation.start(self.errormessage)


        Clock.schedule_once(start_slide_out_animation, 4)


                  
    def insert(self):
        print(self.address.opacity)
        if self.address.opacity == 0:
            self.address.opacity = 1
            slide_in_animation = Animation(pos_hint={"center_x": .5, "center_y": 0.5}, duration=2)
            slide_in_animation.start(self.address)
        elif self.address.opacity == 1:
            def closing(dt):
                self.address.opacity = 0
            slide_out_animation = Animation(pos_hint={"center_x": -.5, "center_y": 0.5}, duration=2)
            slide_out_animation.start(self.address)
            Clock.schedule_once(closing, 2)


    def process_address(self,text):
        print(text)
        geolocator = Nominatim(user_agent='--user-agent=f"{user_agent}"')
        try:
            geolocator.geocode(text)
        except:
            Clock.schedule_once(self.error_message, 4)
        location = geolocator.geocode(text)
        list[0] = location.latitude
        list[1] = location.longitude
        global point
        point.lat = list[0]
        point.lon = list[1] # Add each café as a marker on the map
        self.map_view.center_on(list[0], list[1])
        print(f"Latitude: {latitude}, Longitude: {longitude}")
        print(list)

class MapApp(App):
    def build(self):


        return Controller()



if __name__ == '__main__':
    MapApp().run()


    