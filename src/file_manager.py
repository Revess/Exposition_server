import os
import json
from PIL import Image
import numpy as np
from math import floor

def split_folder(path,return_file_and_drive=False):
    folders = []
    if ":" in path:
        drive, path = os.path.splitdrive(path)
    while(True):
        if path == '':
            break
        else:
            path, folder = os.path.split(path)
            folders.insert(0,folder)
    return folders

def make_folder(path):
    folders = split_folder(path)
    path = ''
    for folder in folders:
        path += folder+"/"
        if not os.path.exists(path):
            os.mkdir(path)
    path = path[:-1]
    
def save_json(data,path):
    with open(path,"w") as file__:
        json.dump(data,file__,sort_keys=True,indent=4)

def load_json(path):
    with open(path,"r") as file__:
        data = json.load(file__)
    return data

def save_image(matrix,layer_name,name,size=None):
    save_im = np.squeeze(matrix)
    save_im -= save_im.mean()
    save_im /= save_im.std()
    save_im *= 160
    save_im += 96
    save_im = np.clip(save_im, 0, 255).astype(np.uint8)
    if not os.path.exists("./data/model_output/images"+"/"+str(layer_name)+"/"):
        os.mkdir("./data/model_output/images"+"/"+str(layer_name)+"/")
    if layer_name == "conv1" or layer_name == "mp1":
        height = 540
        w = 480
        save_im = np.asarray(Image.fromarray(np.squeeze(save_im)).resize((floor((height/save_im.shape[0])*save_im.shape[1]),height)))
        width = int((save_im.shape[1]-w)/2)
        save_im = save_im[:,width:w+width]
    elif layer_name == "conv2" or layer_name == "conv3" or layer_name == "conv4" or layer_name == "mp2" or layer_name == "mp3" or layer_name == "mp4":
        height = 320
        w = 270
        save_im = np.asarray(Image.fromarray(np.squeeze(save_im)).resize((floor((height/save_im.shape[0])*save_im.shape[1]),height)))
        width = int((save_im.shape[1]-w)/2)
        save_im = save_im[:,width:w+width]
    elif layer_name == "flatten" or layer_name == "dense_1" or layer_name == "dense":
        height = 180
        w = 960
        save_im = np.asarray(Image.fromarray(np.squeeze(save_im)).rotate(90).resize((w,height)))
        
    Image.fromarray(np.squeeze(save_im)).save("./data/model_output/images/"+str(layer_name)+"/"+str(layer_name)+"_"+str(name)+".png")