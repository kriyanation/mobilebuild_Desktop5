# -*- coding:utf8 -*-
import os
import random
import traceback
import webbrowser
#os.environ['KIVY_TEXT']='pil'
from threading import Thread


from kivy.animation import Animation
from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import Metrics

from kivy.clock import  Clock
from kivy.uix.image import Image

from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar

from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.core.window import Window


import data_capture_lessons
import data_lessons

from indic_transliteration import sanscript, xsanscript
from indic_transliteration.sanscript import transliterate
from kivy.utils import platform

Window.softinput_mode = 'below_target'
from kivy.config import Config
if platform !='android':
    Config.remove_option('input','%(name)s')
    print (Config.items('input'))

class LessonGroupScreen(Screen):
    container = ObjectProperty(None)
    lesson_list_names = []
    def __init__(self,**kwargs):
        super(LessonGroupScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)
        Clock.schedule_once(self.add_buttons,1)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'lessons':
                return False

    def add_buttons(self,dt):
        self.list_groups = data_capture_lessons.get_groups()
        self.container.bind(minimum_height=self.container.setter('height'))
        for element in self.list_groups:
            font_name = "Caveat-Bold.ttf"
            button = Button(text=element[1],font_name=font_name,font_size="50sp",background_color=[0.76,0.83,0.86,0.8],pos_hint={'top': 1},size_hint_y=None,size_hint_x=1)
            button.on_release = lambda instance=button, a=element[0]: self.switch_to_title(instance, a)
            self.lesson_list_names.append(element[1])
            self.container.add_widget(button)

    def switch_to_title(self,i,a):

        self.selected_group = a
        self.manager.current ="lessons"
        self.manager.transition.direction = 'left'

    def launch_popup(self):
        show = ImportPop()
        self.popupWindow = Popup(title="Import Mini Lesson", content=show,
                                 size_hint=(1, 0.7), auto_dismiss=False)
        show.set_popupw(self.popupWindow)
        show.set_screen_instance(self,self.lesson_list_names)
        # open popup window
        self.popupWindow.open()




class LessonListScreen(Screen):
    container = ObjectProperty(None)
    def __init__(self,**kwargs):
        super(LessonListScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_enter(self, *args):
        groupid = self.manager.get_screen('groups').selected_group


        self.list_lessons = data_capture_lessons.get_Lessons_ofgroup(groupid)
        self.container.clear_widgets()
        Clock.schedule_once(self.add_buttons, 1)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'lessons' :
                self.manager.transition.direction = 'right'
                self.manager.current = self.manager.previous()
                return True
    def add_buttons(self,dt):
        groupid = self.manager.get_screen('groups').selected_group

        self.list_lessons = data_capture_lessons.get_Lessons_ofgroup(groupid)
        self.container.bind(minimum_height=self.container.setter('height'))
        for element in self.list_lessons:
            if element[2] is None or element[2] == "" or element[2] == "English":
                font_name = "Caveat-Bold.ttf"
            else:
                font_name = "unifont.ttf"
            button = Button(text=element[1],font_name=font_name,font_size="50sp",background_color=[0.76,0.83,0.86,0.8],pos_hint={'top': 1},size_hint_y=None,size_hint_x=1)
            button.on_release = lambda instance=button, a=element[0],b=element[2]: self.switch_to_title(instance, a,b)
            self.container.add_widget(button)

    def switch_to_title(self,i,a,b):
        if b is None or b == "" or b == "English":
            self.manager.set_font("Caveat-Bold.ttf")
            self.manager.set_lang("English")
        else:
            self.manager.set_font("unifont.ttf")
            self.manager.set_lang("Hindi")
        self.selected_lesson = a
        self.manager.current ="title"
        self.manager.transition.direction = 'left'

    def set_previous_screen(self):
        if self.manager.current == 'lessons':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()




    def launch_del_popup(self):
        self.popup_delete = DeletePop()
        self.popup_delete.set_screen_instance(self,self.manager.get_screen('groups').selected_group)
        # self.popupWindow = Popup(title="Delete Lesson", content=show,
        #                     size_hint=(1, 0.4),auto_dismiss=True)
        # show.set_popupw(self.popupWindow)
        # show.set_screen_instance(self)
        # open popup window
        self.popup_delete.open()

class DeletePop(Popup):
    lesson_list = ListProperty()


    selected_lesson = StringProperty()
    status_label = StringProperty()

    def __init__(self, **kwargs):
        super(DeletePop, self).__init__(**kwargs)

    def fill_lesson_list(self):
        lessons = data_capture_lessons.get_Lessons_ofgroup(self.groupid)
        lessonlistdisplay = []
        for element in lessons:
            lesson_display = str(element[0])+":"+element[1]
            lessonlistdisplay.append(lesson_display)
        self.lesson_list = lessonlistdisplay


    def on_select_lesson(self,lesson):
        self.selected_lesson = lesson

    def on_delete(self):
        if self.selected_lesson != "Selected Lesson":
            lesson_id = self.selected_lesson.split(":")[0]
            deletion = data_lessons.delete_lesson(lesson_id)
            if deletion == 0:
                self.status_label = "You have deleted the selected lesson"
            else:
                self.status_label = "We could not delete the lesson, try again"
        self.listscreen.container.clear_widgets()
        self.listscreen.add_buttons(1)


    def set_screen_instance(self, listscreen,groupid):
        self.listscreen = listscreen
        self.groupid = groupid
        self.fill_lesson_list()



class ImportPop(BoxLayout):
    text_userid = StringProperty()
    text_classid = StringProperty()
    text_lessonid = StringProperty()
    text_status = StringProperty()
    lesson_groups = ListProperty()
    selected_group = StringProperty("Group A")

    def __init__(self, **kwargs):

        super(ImportPop, self).__init__(**kwargs)
        self.lesson_import_flag = 0

    def import_lesson(self,button_sub):

        button_sub.state = "down"
        print(self.text_classid+self.text_userid+self.text_lessonid)
        response_code = 0
        if self.lesson_import_flag == 0:
             response_code, json_object = data_lessons.import_new_lesson(self.text_userid,self.text_classid,self.text_lessonid)

        if response_code == 1:
            self.text_status = "There was an error accessing the lesson. Check your access details."
            button_sub.disabled = False
            button_sub.state = "normal"
            self.lesson_import_flag = 0
        else:

            self.text_status = "Access details correct. Downloading the lesson..."
            self.call_update = Thread(target = data_lessons.update_lesson_details,args=(json_object,))
            self.call_update.start()
            self.progress_bar = ProgressBar()
            self.popup = Popup(
                title='Importing lesson',
                content=self.progress_bar,
                size_hint=(1, 0.3), auto_dismiss=False
            )
            self.popup.open()
            Clock.schedule_interval(self.next, 0.5)





    def next(self, dt):
        groupid = ""
        if self.call_update.is_alive():
            self.progress_bar.value += 5
        else:
            if self.selected_group == "Science":
                groupid = 1
            elif self.selected_group == "Mathematics":
                groupid = 2
            elif self.selected_group == "English":
                groupid = 3
            elif self.selected_group == "Social Science":
                groupid = 4
            elif self.selected_group == "Languages":
                groupid = 5
            elif self.selected_group == "Other Subjects":
                groupid = 6
            data_capture_lessons.update_group_id(groupid)
            self.popup.dismiss()
            self.lesson_import_flag = 0
            self.text_status ="Import Completed and the Lesson is added to the "+self.selected_group
            return False


    def close_pop(self):

        self.popw.dismiss()

    def set_popupw(self,pop):
        self.popw=pop

    def set_screen_instance(self,listscreen,lessongroups):
        self.listscreen =listscreen
        self.lesson_groups = lessongroups
        print(self.lesson_groups)

    def on_select_group(self, group):
        self.selected_group = group




class LessonTitleScreen(Screen):
    text_label_1 = StringProperty()
    text_label_2 = StringProperty()
    text_image= StringProperty()
    animation_count = NumericProperty()
    font_name = StringProperty("Caveat-Bold.ttf")

    def __init__(self,**kwargs):
        super(LessonTitleScreen,self).__init__(**kwargs)
        self.speak_flag = 0
        Window.bind(on_keyboard=self.on_key)


    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'title' :
                self.manager.transition.direction = 'right'
                self.manager.current = 'lessons'
                return True

    def read_intro(self,sb_button):
        sound_speak = Thread(target=data_lessons.playtextsound, args=(self.text_label_1,))
        sound_speak.start()


    def animate(self,dt):
        # create an animation object. This object could be stored
        # and reused each call or reused across different widgets.
        # += is a sequential step, while &= is in parallel
        self.animation_count += 1
        animation = Animation(center_x=self.width/1.7, t='in_quad')
        animation += Animation(center_x=self.width/2.3,t='in_quad')
        # animation += Animation(pos=(200, 100), t='out_bounce')
        # animation &= Animation(size=(500, 500))
        # animation += Animation(size=(100, 50))

        # apply the animation on the button, passed in the "instance" argument
        # Notice that default 'click' animation (changing the button
        # color while the mouse is down) is unchanged.
        if self.animation_count == 3:
            animation += Animation(center_x=self.width/2, t='in_quad')
            animation.start(self.ids.tl_image)
            self.animation_count = 0
            return False

        animation.start(self.ids.tl_image)


    def reset_speak_flag(self,t):
        self.speak_flag = 0

    def on_enter(self):
        lessonid = self.manager.get_screen('lessons').selected_lesson
        self.font_name = self.manager.get_font()
        title, title_image, title_running_notes = data_capture_lessons.get_title_info(lessonid)
        self.text_label_1 = title_running_notes
        self.text_label_2 = title
        imagepath = "Lessons/Lesson"+str(lessonid)+"/images/"+title_image
        if os.path.exists(imagepath) and title_image != "":
            self.text_image = imagepath
        else:
            self.text_image = "placeholder.png"
        Clock.schedule_interval(self.animate,2)




    def set_previous_screen(self):
        if self.manager.current == 'title':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()
    def set_next_screen(self):
        if self.manager.current == 'title':
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

class LessonFactualScreen(Screen):


    text_image_1 = StringProperty()
    text_image_2 = StringProperty()
    text_image_3 = StringProperty()
    text_image_display = StringProperty()
    font_name = StringProperty("Caveat-Bold.ttf")

    text_term_description_1 = StringProperty()
    text_term_description_2  = StringProperty()
    text_term_description_3  = StringProperty()
    text_term_description = StringProperty()

    def __init__(self, **kwargs):
        super(LessonFactualScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_enter(self):
        self.font_name = self.manager.get_font()
        lessonid = self.manager.get_screen('lessons').selected_lesson
        textimage_1, textimage_2, textimage_3 = data_capture_lessons.get_fact_images(lessonid)
        text_term_1, text_term_2, text_term_3 = data_capture_lessons.get_fact_terms(lessonid)
        textterm_description_1,textterm_description_2 ,textterm_description_3 = data_capture_lessons.get_fact_descriptions(lessonid)
        imagepath = "Lessons/Lesson" + str(lessonid) + "/images/"

        text_image1 =  imagepath+textimage_1
        text_image2 = imagepath + textimage_2
        text_image3 = imagepath + textimage_3

        self.display_index = 0
        self.text_term_description_1 = text_term_1+" : "+textterm_description_1
        self.text_term_description_2 = text_term_2 + " : " + textterm_description_2
        self.text_term_description_3 = text_term_3 + " : " + textterm_description_3
        self.text_to_read = self.text_term_description_1

        self.text_term_description = self.text_term_description_1

        if not os.path.exists( text_image1 ) or textimage_1 == "":
            self.text_image_1 = "placeholder.png"
        else:
            self.text_image_1 = text_image1
        if not os.path.exists(text_image2) or textimage_2 == "":
            self.text_image_2 = "placeholder.png"
        else:
            self.text_image_2 = text_image2
        if not os.path.exists(text_image3) or textimage_3 == "":
            self.text_image_3 = "placeholder.png"
        else:
            self.text_image_3 = text_image3
        self.text_image_display = self.text_image_1

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'factual' :
                self.manager.transition.direction = 'right'
                self.manager.current = 'title'
                return True


    def read_aloud(self,text,button):
        sound_speak = Thread(target=data_lessons.playtextsound, args=(text,))
        sound_speak.start()


    def load_next(self):
        self.display_index += 1
        if self.display_index == 3:
            self.display_index = 0

        if self.display_index == 0:
            self.text_image_display = self.text_image_1
            self.text_term_description = self.text_term_description_1
        elif self.display_index == 1:
            self.text_image_display = self.text_image_2
            self.text_term_description = self.text_term_description_2
        else:
            self.text_image_display = self.text_image_3
            self.text_term_description = self.text_term_description_3



    def load_previous(self):

        self.display_index -= 1
        if self.display_index == -1:
            self.display_index = 2

        if self.display_index == 0:
            self.text_image_display = self.text_image_1
            self.text_term_description = self.text_term_description_1
        elif self.display_index == 1:
            self.text_image_display = self.text_image_2
            self.text_term_description = self.text_term_description_2
        else:
            self.text_image_display = self.text_image_3
            self.text_term_description = self.text_term_description_3


    def set_previous_screen(self):
        if self.manager.current == 'factual':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()
    def set_next_screen(self):
        if self.manager.current == 'factual':
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()
class imgpopup(Popup):
    text_image = StringProperty()
    text_step = StringProperty()
    text_no_image = StringProperty()
    def set_text(self,text_image,text_step,text_no_image):
        self.text_image = text_image
        self.text_step = text_step
        self.text_no_image = text_no_image
class imgpopupall(Popup):

    text_step = StringProperty()
    text_no_image = StringProperty()
    def set_text(self,title,text_no_image):

        self.text_step = title
        self.text_no_image = text_no_image

class LessonApplyScreen(Screen):
    text_label_1 = StringProperty("Dynamic Text"+str(random.randint(1,100)))
    text_label_2 = StringProperty("test.png")
    steps = ObjectProperty(None)
    font_name = StringProperty("Caveat-Bold.ttf")
    def __init__(self,**kwargs):
        super(LessonApplyScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)


    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'apply' :
                self.manager.transition.direction = 'right'
                self.manager.current = 'factual'
                return True


    def on_enter(self):
        self.font_name = self.manager.get_font()
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.number_of_steps = data_capture_lessons.get_number_of_steps(self.lessonid)
        self.step_list = data_capture_lessons.get_description_list(self.lessonid)
        self.image_list = data_capture_lessons.get_step_image_list(self.lessonid)
        self.add_steps_buttons()

    def set_previous_screen(self):
        if self.manager.current == 'apply':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()
    def set_next_screen(self):
        if self.manager.current == 'apply':
            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def add_steps_buttons(self):

        self.button_list = []
        self.steps.clear_widgets()
#        self.images.clear_widgets()

        if platform != 'android':
            textsize = (1200,None)
        else:
            textsize = (2.0*Metrics.dpi, None)

        for i in range(8):
            if self.step_list[i] is None or self.step_list[i] == "":
                break
            button = Button(text=self.step_list[i],font_name=self.font_name, size_hint_y=None,size_hint_x=1,height="70sp"
                            ,background_color=[0.76,0.83,0.86,0.8],text_size=textsize,font_size='50sp')

            self.button_list.append(button)
            button.on_release = lambda instance=button,a =i: self.add_image(instance,a)
            self.steps.add_widget(button)
        button1 = Button(text="View All",font_name=self.font_name, size_hint_y=None, size_hint_x=1, height="70sp"
                        , background_color=[0.76, 0.83, 0.86, 0.8], text_size=textsize,
                        font_size='50sp')
        button1.on_release =  self.add_all_images
        self.steps.add_widget(button1)

    def add_all_images(self):
        img_pop = imgpopupall()
        title = "Sequence View"
        if len(self.image_list)==0:
            text_no_image ="There are no images associated with the steps"
        else:
            text_no_image = ""

        img_pop.set_text( title, text_no_image)
        imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/"
        for i in range(len(self.image_list)):
            if self.image_list[i] is not None and self.image_list[i] != "":
                step_image = Image(source = imagepath+self.image_list[i],size=(200,200))
                animation = Animation(size_hint = (0.3,0.3), t='in_quad')
                animation += Animation(size_hint=(1, 1), t='in_quad')

                if (i < 4):
                    img_pop.all_images1.add_widget(step_image)
                    animation.start(step_image)
                else:
                    img_pop.all_images2.add_widget(step_image)
                    animation.start(step_image)
        img_pop.open()

    def add_image(self,instance,a,*args):
        print(a)
        print(instance)
        if a < len(self.button_list)-1:
            button = self.button_list[a+1]
            button.disabled = False
        imagepath = "Lessons/Lesson" + str(self.lessonid) + "/images/"
        if (self.image_list[a] != None and self.image_list[a].strip() != ""):
            # image = Image(source=imagepath+self.image_list[a],size_hint_y=None,size=(400,400))
            # self.images.add_widget(image)

            self.text_image = imagepath+self.image_list[a]
            text_no_image = ""
        else:
            self.text_image = "trans.png"
            text_no_image = "No Image Associated with this step"
        img_pop = imgpopup()
        img_pop.set_text(self.text_image,self.step_list[a],text_no_image)
        img_pop.open()
        sound_speak = Thread(target=data_lessons.playtextsound, args=(self.step_list[a],))
        sound_speak.start()







class LessonWhiteboardScreen(Screen):
    text_image_1 = StringProperty()
    font_name = StringProperty("Caveat-Bold.ttf")
    def __init__(self,**kwargs):
        super(LessonWhiteboardScreen,self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)


    def on_enter(self, *args):
        self.font_name = self.manager.get_font()
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        self.filename_pfix = "Lessons" + os.path.sep + "Lesson" + str(
                     self.lessonid) + os.path.sep + "images" + os.path.sep

        filename = data_capture_lessons.get_whiteboard_image(self.lessonid)

        if filename is not None and filename != "":
            self.text_image_1 = self.filename_pfix+filename
        else:
            self.text_image_1 = "placeholder.png"

    def set_next_screen(self):
        if self.manager.current == 'whiteboard':

            self.manager.transition.direction = 'left'
            self.manager.current = self.manager.next()

    def set_previous_screen(self):
        if self.manager.current == 'whiteboard':
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.previous()

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'whiteboard':
                self.manager.transition.direction = 'right'
                self.manager.current = 'apply'
                return True

class LessonNotesScreen(Screen):
    text_label_1 = StringProperty()

    font_name = StringProperty("Caveat-Bold.ttf")
    def __init__(self, **kwargs):
        super(LessonNotesScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.manager.current == 'notes':
                self.manager.transition.direction = 'right'
                self.manager.current = 'apply'
                return True

    def on_enter(self):
        self.font_name = self.manager.get_font()
        self.lessonid = self.manager.get_screen('lessons').selected_lesson
        txt_notes = data_capture_lessons.get_notes(self.lessonid)
        if (txt_notes is None):
            self.text_label_1 = ""
        else:
            self.text_label_1 = txt_notes


    def set_next_screen(self):
        if self.manager.current == 'notes':
            self.manager.transition.direction = 'left'
            self.manager.current = 'assess'

    def set_previous_screen(self):
        if self.manager.current == 'notes':
            self.manager.transition.direction = 'right'
            self.manager.current = 'whiteboard'




class LessonAssessScreen(Screen):


        text_label_1 = StringProperty()
        text_label_2 = StringProperty()
        font_name = StringProperty("Caveat-Bold.ttf")
        steps = ObjectProperty(None)

        def __init__(self, **kwargs):
            super(LessonAssessScreen, self).__init__(**kwargs)
            Window.bind(on_keyboard=self.on_key)

        def on_key(self, window, key, *args):
            if key == 27:  # the esc key
                if self.manager.current == 'assess':
                    self.manager.transition.direction = 'right'
                    self.manager.current = 'apply'
                    return True

        def on_enter(self):
            self.font_name = self.manager.get_font()
            self.lessonid = self.manager.get_screen('lessons').selected_lesson
            self.text_label_1, self.text_label_2 = data_capture_lessons.get_questions_answer(self.lessonid)
            self.formlink = data_capture_lessons.get_formlink(self.lessonid)
            if self.formlink is not None and self.formlink != "" and hasattr(self,"form_button") == False:
                self.form_button = Button(text="launch",size_hint=(1,0.1),background_color = [0.76,0.83,0.86,0.8],
                                          on_release = self.launch_form)
                self.ids.assess.add_widget(self.form_button)
        def launch_form(self,*args):
            webbrowser.open(self.formlink)

        def on_assess_text(self, wid, text):
            if text is not None and len(text) > 0 and text[-1] == " " and self.manager.get_lang() != "English":
                text = text.strip()
                output = transliterate(text, sanscript.HK, sanscript.DEVANAGARI)
                output = output + " "
                wid.text = output

        def on_save(self):
            ret = data_capture_lessons.set_answer(self.lessonid,self.text_label_2)
            print(self.text_label_2)
            print(str(ret))
        def on_share(self):
            Clipboard.copy(self.text_label_2)


        def set_next_screen(self):
            if self.manager.current == 'assess':
                self.manager.transition.direction = 'left'
                self.manager.current = 'lessons'

        def set_previous_screen(self):
            if self.manager.current == 'assess':
                self.manager.transition.direction = 'right'
                self.manager.current = 'notes'



class Popups(BoxLayout):
    pass

class ScreenManagement(ScreenManager):
    lesson_font = StringProperty()
    def set_font(self, text):
        self.lesson_font = text

    def get_font(self):
        return self.lesson_font

    def set_lang(self, text):
        self.lesson_lang = text

    def get_lang(self):
        return self.lesson_lang
class MagicRoomApp(App):
    def on_pause(self):
        return True

    def build(self):

        self.icon = 'logo_bg_small.png'
        self.title = 'Learning Room'


        return ScreenManagement()

#from jnius import autoclass, cast







MagicRoomApp().run()

