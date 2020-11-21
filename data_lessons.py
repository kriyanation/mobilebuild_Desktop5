import json
import os
import shutil
import sys
import traceback

import pyttsx3
import requests

import data_capture_lessons


def import_new_lesson(user,classid,lessonid):
    headers = {'Content-Type': 'application/json'}
    url = "https://thelearningroom.el.r.appspot.com/lesson/lesson/?username=" + user + "&lesson_id=" + lessonid + "&class_id=" + classid
    try:
        response_get = requests.get(url, headers=headers)
        response_object_get = json.loads(response_get.content)
    except:
        return 1, None
    if response_get.status_code == 200 and len(response_object_get) > 0:
        print(str(response_get.status_code))
        json_object = response_object_get[0]
        #status = update_lesson_details(json_object)
        #if status == "error":
        return 0, json_object
    else:
        return 1, None

def update_lesson_details(json_object):
    title_image_file = json_object["title_image"]
    title_filename, term1_filename, term2_filename,\
    term3_filename,step1_filename,step2_filename,step3_filename,step4_filename,step5_filename,\
    step6_filename,step7_filename,step8_filename,whiteboard_filename = "","","","","","","","","","","","",""

    if not os.path.exists("tmp"):
      os.mkdir("tmp")
    if title_image_file is not None:
        title_filename = constructfilename(title_image_file,"title")
    term1_image_file = json_object["term1_image"]
    if term1_image_file is not None:
        term1_filename = constructfilename(term1_image_file,"term1")
    term2_image_file = json_object["term2_image"]
    if term2_image_file is not None:
        term2_filename = constructfilename(term2_image_file,"term2")
    term3_image_file = json_object["term3_image"]
    if term3_image_file is not None:
        term3_filename = constructfilename(term3_image_file,"term3")
    step1_image_file = json_object["step1_image"]
    if step1_image_file is not None:
        step1_filename = constructfilename(step1_image_file,"step1")
    step2_image_file = json_object["step2_image"]
    if step2_image_file is not None:
        step2_filename = constructfilename(step2_image_file,"step2")
    step3_image_file = json_object["step3_image"]
    if step3_image_file is not None:
        step3_filename = constructfilename(step3_image_file,"step3")
    step4_image_file = json_object["step4_image"]
    if step4_image_file is not None:
        step4_filename = constructfilename(step4_image_file,"step4")
    step5_image_file = json_object["step5_image"]
    if step5_image_file is not None:
        step5_filename = constructfilename(step5_image_file,"step5")
    step6_image_file = json_object["step6_image"]
    if step6_image_file is not None:
        step6_filename = constructfilename(step6_image_file,"step6")
    step7_image_file = json_object["step7_image"]
    if step7_image_file is not None:
        step7_filename = constructfilename(step7_image_file,"step7")
    step8_image_file = json_object["step8_image"]
    if step8_image_file is not None:
        step8_filename = constructfilename(step8_image_file,"step8")
    whiteboard_image = json_object["whiteboard_image"]
    if whiteboard_image is not None:
        whiteboard_filename = constructfilename(whiteboard_image, "whiteboard")


    json_object["title_description"] = make_data_ready(json_object["title_description"])
    json_object["term1_description"] = make_data_ready(json_object["term1_description"])
    json_object["term2_description"] = make_data_ready(json_object["term2_description"])
    json_object["term3_description"] = make_data_ready(json_object["term3_description"])
    json_object["term1"] = make_data_ready(json_object["term1"])
    json_object["term2"] = make_data_ready(json_object["term2"])
    json_object["term3"] = make_data_ready(json_object["term3"])
    json_object["questions"] = make_data_ready(json_object["questions"])
    json_object["application_video_running_notes"] = make_data_ready(json_object["application_video_running_notes"])
    json_object["title"] = make_data_ready(json_object["title"])
    json_object["step1_description"] = make_data_ready(json_object["step1_description"])
    json_object["step2_description"] = make_data_ready(json_object["step2_description"])
    json_object["step3_description"] = make_data_ready(json_object["step3_description"])
    json_object["step4_description"] = make_data_ready(json_object["step4_description"])
    json_object["step5_description"] = make_data_ready(json_object["step5_description"])
    json_object["step6_description"] = make_data_ready(json_object["step6_description"])
    json_object["step7_description"] = make_data_ready(json_object["step7_description"])
    json_object["step8_description"] = make_data_ready(json_object["step8_description"])
    query_parameters = [json_object["title"],title_filename,json_object["title_video"],json_object["title_description"],
                        json_object["term1"],json_object["term1_description"],term1_filename,json_object["term2"],json_object["term2_description"],term2_filename,
                        json_object["term3"],json_object["term3_description"],term3_filename,json_object["number_of_steps"],json_object["step1_description"],step1_filename,json_object["step2_description"],step2_filename,
                        json_object["step3_description"],step3_filename,json_object["step4_description"],step4_filename,json_object["step5_description"],step5_filename,
                        json_object["step6_description"],step6_filename,json_object["step7_description"],step7_filename,json_object["step8_description"],step8_filename,
                        json_object["questions"],"",whiteboard_filename,json_object["application_video_running_notes"],json_object["application_video_link"],json_object["lesson_language"]]
    try:
        data_capture_lessons.insert_imported_record(query_parameters)
        new_id = data_capture_lessons.get_new_id()
        print("New ID"+str(new_id))
        if not os.path.exists("Lessons/Lesson"+str(new_id)):
            print("Inside If loop of directory creation")
            os.mkdir("Lessons/Lesson"+str(new_id))
            os.mkdir("Lessons/Lesson"+str(new_id)+"/images")
            src_files = os.listdir("tmp")
            for file_name in src_files:
                full_file_name = os.path.join("tmp", file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, "Lessons/Lesson"+str(new_id)+"/images")
                    os.remove(full_file_name)
            os.rmdir("tmp")
            return 0
    except:
        traceback.print_exc()
        print("Wondersky: Error while creating directories")
        return 198

def make_data_ready(text):
    data_ready_string = text.replace("~","\n")
    data_ready_string = data_ready_string.replace("|","\"")
    return data_ready_string

def constructfilename(fileurl,prefix):
    try:
        file_dl = fileurl.split("?", 2)
        extension = file_dl[0].split(".")[-1]
        status_dl = download_file(fileurl, "tmp/"+prefix+"."+ extension)
        title_filename = prefix+"."+extension
        return title_filename
    except:
        traceback.print_exc()
        print("Wondersky: Error while constructing  filename")

def playtextsound(text):
    if sys.platform.startswith('linux'):
        engine = pyttsx3.init(driverName='espeak')
    else:
        import pythoncom
        pythoncom.CoInitialize()
        engine = pyttsx3.init()
    engine.setProperty('voice', 'en+f2')
    engine.setProperty('rate', 130)
    engine.setProperty("volume", 0.9)
    if text != "" and text is not None:
        engine.say(text)
        engine.runAndWait()
    else:
        return



def  download_file(fileurl,filename):
    try:
        response = requests.get(fileurl)
        if response.status_code != 200:
            return "error"
        file = open(filename, "wb")
        file.write(response.content)
        file.close()
    except:
        traceback.print_exc()
        print("Wondersky: Error while downloading Images")


def delete_lesson(lesson_id):
    try:
        delete_data = data_capture_lessons.delete_lesson(lesson_id)
        if delete_data == 0:
            shutil.rmtree("Lessons/Lesson"+lesson_id,True)
            return 0
    except:
        traceback.print_exc()
        print("Wondersky: Error Deleting Lessons")
        return 1
