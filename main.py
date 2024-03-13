# import necessary modules/packages
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton
from kivymd.uix.button import MDFabButton
from kivymd.uix.button import MDButtonText
from kivymd.uix.button import MDExtendedFabButton
from kivymd.uix.button import MDExtendedFabButtonText
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.screen import MDScreen
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.imagelist import MDSmartTile
from kivymd.uix.imagelist import MDSmartTileImage
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from win32api import GetSystemMetrics
import os
import cv2
import numpy as np
import keras_ocr
import math


# Initialize keras_ocr for detector and recognizer
detector = keras_ocr.detection.Detector()
recognizer = keras_ocr.recognition.Recognizer()


# Disable exit_on_esc
Config.set('kivy', 'exit_on_escape', '0')


# Make the app run on fullscreen
Window.size = (GetSystemMetrics(0), GetSystemMetrics(1))
Window.fullscreen = True


# Define class for it's design and function
class Design(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

        # Initialize a variable for storing the checkbox value
        self.checkbox = None

        # Initialize source path of base image and final image
        self.uploaded_image_path = None
        self.result_image_path = "background.png"

        # Define a display heading of the app on top of the screen
        self.heading = MDLabel(text= "OPTICAL CHARACTER RECOGNIZER",  
                            adaptive_size=True,
                            theme_text_color="Custom",                    
                            text_color=(52/255, 235/255, 216/255,1),
                            line_color=(0,0.5,1,1),
                            pos_hint={"center_x": 0.5, "center_y": 0.93},
                            font_style="Display",
                            role="medium",
                            radius=20,
                            padding=(10,10),
                            line_width=3,
                            outline_color=(1,1,1,1),
                            outline_width=2
                            )
        

        # Define a label for button description
        self.function_to_perform = MDLabel(text="Choose Function",
                                           adaptive_size=True,
                                           theme_text_color="Custom",
                                           outline_color=(1,1,1,1),
                                           pos_hint={"center_x":0.26,"center_y":0.75},
                                           font_style="Display",
                                           role="small",
                                           text_color=(68/255, 227/255, 97/255,1),
                                           outline_width=1
                                           )
        

        # Define 2 checkbox button with their labels
        self.remove_checkbox = MDCheckbox(group = 'function',
                                      size_hint_x = .047,
                                      size_hint_y = .047, 
                                      color = [0, 0, 0], 
                                      id ='remove',
                                      pos_hint={"center_x":0.55,"center_y":0.77},
                                      on_release=self.on_press_checkbox
                                      )
        self.remove_text = MDLabel(text="Remove Text",
                              adaptive_size=True,
                              theme_text_color="Custom",
                              text_color=(0.5,1,1,1),
                              pos_hint={"center_x":0.55,"center_y":0.74},
                              font_style="Headline",
                              role="small"
                              )

        self.label_checkbox = MDCheckbox(group = 'function', 
                                       size_hint_x = .047, 
                                       size_hint_y = .047, 
                                       color = [1, 0, 0],
                                       pos_hint={"center_x":0.75,"center_y":0.77},
                                       on_release=self.on_press_checkbox
                                       )
        self.label_text = MDLabel(text="Detect and Label",
                                   adaptive_size=True,
                                   theme_text_color="Custom",
                                   text_color=(0.5,1,1,1),
                                   pos_hint={"center_x":0.75,"center_y":0.74},
                                   font_style="Headline",
                                   role="small"
                                   )


        # Define the area and show uploaded image
        self.upload_tile = MDSmartTile(size_hint=(0.4,0.4),
                                       pos_hint={"center_x": .27, "center_y": .465},
                                       md_bg_color=(255,0,0),
                                       radius=[25,25,25,25]
                                      )
        self.upload_tile_image = MDSmartTileImage(source=self.uploaded_image_path,
                                                  allow_stretch=True,
                                                  size_hint=(0.97,0.90),
                                                  pos_hint={"center_x": .5, "center_y": .5},
                                                  keep_ratio=False,
                                                  radius=[30,30,30,30],
                                                  color=(81/255,87/255,82/255,1)
                                                 )
                    

        # Define the area and show result image
        self.result_tile = MDSmartTile(size_hint=(0.4,0.4),
                                       pos_hint={"center_x": .73, "center_y": .465},
                                       md_bg_color=(0,255,0),
                                       radius=[25,25,25,25]
                                      )
        self.result_tile_image = MDSmartTileImage(source=self.result_image_path,
                                                  allow_stretch=True,
                                                  size_hint=(0.97,0.90),
                                                  pos_hint={"center_x": .5, "center_y": .5},
                                                  keep_ratio=False,
                                                  radius=[30,30,30,30],
                                                 )


        # Initialize a browse button to upload a image for performing function
        self.browse_button_text = MDButtonText(text = "Upload Image",
                                          theme_text_color="Custom", 
                                          theme_font_size="Custom",
                                          text_color=(52/255, 235/255, 216/255,1),
                                          font_size="16"
                                          )
        self.browse_button_text.disabled = True
        self.browse_button = MDButton(theme_line_color="Custom",       
                                      pos_hint={"center_x":0.27,"center_y":0.465},
                                      line_color=(0,0.5,1,1),
                                      radius=10,
                                      focus_color=(1,1,1,0.2),
                                      unfocus_color=(0,0,0,0),
                                      on_release=self.open_file_manager,
                                     )
        self.browse_button.disabled = True
        
        self.filemanger_obj = MDFileManager(select_path=self.select_path,
                                            exit_manager=self.exit_manager
                                            )
        

        # Define a generate button that starts the process of extracting text from images
        self.generate_button = MDButton(MDButtonText(text = "Generate Result",
                                                   theme_text_color="Custom", 
                                                   theme_font_size="Custom",
                                                   text_color=(1, 1, 1, 1),
                                                   font_size="18",
                                                   bold=True
                                                   ),
                                      theme_line_color="Custom",       
                                      pos_hint={"center_x":0.5,"center_y":0.18},
                                      line_color=(0,1,0,1),
                                      radius=10,
                                      focus_color=(0,1,0,0.5),
                                      unfocus_color=(0,0,0,0),
                                      ripple_effect=False,
                                      on_release=self.generate_results,
                                     )
        self.generate_button.disabled = True


        # Define a save button for generated image
        self.save_button = MDFabButton(
                                   icon="content-save",
                                   style="standard",
                                   pos_hint={"center_x": 0.55, "center_y": 0.30},
                                   focus_color=(0,1,0,0.5),
                                   opacity=0,
                                   on_release=self.save_image
                                   )
        self.save_button.disabled = True
        

        # Define a close button to exit the application
        self.close_button = MDExtendedFabButton(
                                   MDExtendedFabButtonText(text = "Close"),
                                   pos_hint={"center_x": 0.5, "center_y": 0.04},
                                   size_hint=(0.07,0.04),
                                   focus_color=(1,0,0,0.5),
                                   on_release=self.close_app
                                   )
        
        
        # Add all the widgets to the screen
        self.add_widget(self.heading)
        self.add_widget(self.function_to_perform)
        self.add_widget(self.remove_checkbox)
        self.add_widget(self.remove_text)
        self.add_widget(self.label_checkbox)
        self.add_widget(self.label_text)
        self.add_widget(self.upload_tile)
        self.upload_tile.add_widget(self.upload_tile_image)
        self.add_widget(self.result_tile)
        self.result_tile.add_widget(self.result_tile_image)
        self.add_widget(self.browse_button)
        self.browse_button.add_widget(self.browse_button_text)
        self.add_widget(self.generate_button)
        self.add_widget(self.save_button)
        self.add_widget(self.close_button)


    # Function called when user click on either of the checkbox
    def on_press_checkbox(self,obj):
        if self.remove_checkbox.active:
            self.checkbox = 'remove text'
        elif self.label_checkbox.active:
            self.checkbox = 'detect and label'       

        if self.browse_button.disabled:
            if self.remove_checkbox.active == True or self.label_checkbox.active == True:
                self.browse_button.disabled=False
                self.browse_button_text.disabled=False
        else:
            if self.remove_checkbox.active == False and self.label_checkbox.active == False:
                self.browse_button.disabled = True
                self.browse_button_text.disabled = True


    # Functions related to upload image
    def select_path(self,path):
        self.browse_button.pos_hint = {"center_x": 0.13, "center_y": 0.235}
        self.browse_button_text.font_size = "14"
        self.browse_button_text.text = "Change Image"
        self.uploaded_image_path = path
        self.upload_tile_image.color = (1,1,1,1)
        self.upload_tile_image.source = path
        self.generate_button.disabled = False
        self.exit_manager(path)
    
    def open_file_manager(self,obj):
        self.filemanger_obj.show('C:\\Users\\Dell\\Desktop\\Image-Text-Remover\\input images')  #Change path either to desired folder or can also leave it with single '\'

    def exit_manager(self,obj):
        self.filemanger_obj.close()


    # Function to generate results according to user 
    def generate_results(self,obj):
        
        image = cv2.imread(self.uploaded_image_path)
        img = image.copy()            
        img = cv2.resize(img,(360,360))

        # Detect the location of text in the image
        result= detector.detect(images=[img],detection_threshold=0.80)[0]

        # Creating a mask of same size as input image
        mask = np.zeros(img.shape[:2], dtype="uint8")

        # Creating a empty list to store the words and
        final_list = []

        # Performing desired function
        for bbox in result:
            box_group = np.array_split(bbox,indices_or_sections=(1))
            x0, y0 = box_group[0][0]
            x1, y1 = box_group[0][1]
            x2, y2 = box_group[0][2]
            x3, y3 = box_group[0][3] 

            if self.remove_checkbox.active:
                # Inpaint the image where text is present
                thickness = int(math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 ))
                cv2.line(mask, (int((x1 + x2)/2), int((y1 + y2)/2)), (int((x0 + x3)/2), int((y0 + y3)/2)), 255,thickness)
                self.inpainted_img = cv2.inpaint(img, mask, 7, cv2.INPAINT_NS)
            elif self.label_checkbox.active:
                # Recognize the detected text 
                text = recognizer.recognize_from_boxes(images=[img],box_groups=[box_group])
                results = (text[0][0],box_group[0])
                final_list.append(results)
        
        # For labeling the image
        if self.label_checkbox.active:
           self.inpainted_img = self.annotate_image(img,final_list)

        # Convert the inpainted image to display inside the app
        final_image = cv2.cvtColor(self.inpainted_img,cv2.COLOR_RGB2BGR)
        final_image = cv2.flip(final_image,0)
        height,width,_ = final_image.shape
        texture = Texture.create(size=(width, height), colorfmt='rgb')
        texture.blit_buffer(final_image.flatten(), colorfmt='rgb', bufferfmt='ubyte')
        self.result_tile_image.color = (1,1,1,1)
        self.result_tile_image.source = ""
        self.result_tile_image.texture = texture
        
        # Enable and show the save button
        self.save_button.disabled = False
        self.save_button.opacity = 1


    # Function to annotate the image
    def annotate_image(self,image,final_list):
        
        xleft = 30
        xright = 520
        yleft = 50
        yright = 50
        img1 = keras_ocr.tools.drawBoxes(image=image, boxes=final_list,color=(0,255,255), thickness=2,boxes_format="predictions")
        img2 = np.full((360, 660, 3), 255, dtype = np.uint8)
        img2[0:360,150:510] = img1 
        left = []
        right = []
        for (word, box) in final_list:
            if box[:, 0].min() < img1.shape[1] / 2:
                left.append((word, box))
            else:
                right.append((word, box))
        for side, group in zip(["left", "right"], [left, right]):
            for (text, box) in group:
                left_end = (int(box[:, 0].min() +148), int(box[3][1]-(box[3][1]-box[0][1])/2))
                right_end = (int(box[:,0].max()+152), int(box[3][1]-(box[3][1]-box[0][1])/2))
                if side == "left":
                    annotated_image = cv2.putText(img2,text,(xleft,yleft),fontScale=1,color=(0,0,255),thickness=1,fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL)
                    annotated_image = cv2.arrowedLine(img2,(110,yleft-5),left_end,(0,0,255),2,tipLength=0.05)
                    yleft+=50
                    
                elif side == "right":
                    annotated_image = cv2.putText(img2,text,(xright,yright),fontScale=1,color=(0,0,255),thickness=1,fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL)
                    annotated_image = cv2.arrowedLine(img2,(520,yright-5),right_end,(0,0,255),2,tipLength=0.05)
                    yright+=50

        return annotated_image


    # Function to save the generated image
    def save_image(self,obj):
        image_name = os.path.split(self.uploaded_image_path)
        if not os.path.exists("output images"):
            os.mkdir("output images") 

        cv2.imwrite(f"output images/{image_name[1]}",self.inpainted_img)

    
    # Function called when close button is pressed that will close the application
    def close_app(self,obj):
        MDApp.get_running_app().stop()  


# Class to initialize the app
class DemoApp(MDApp):
    def build(self):
        self.title="OCR"
        self.theme_cls.theme_style = "Dark"
        return Design()


if __name__=='__main__':
    
    # Run the App
    DemoApp().run()