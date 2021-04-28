import os
import json
from PIL import Image
import numpy as np

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

def save_image(matrix,layer_name,name):
    save_im = np.squeeze(matrix)
    save_im -= save_im.mean()
    save_im /= save_im.std()
    save_im *= 160
    save_im += 96
    save_im = np.clip(save_im, 0, 255).astype(np.uint8)
    if not os.path.exists("./data/images/"+str(layer_name)+"/"):
        os.mkdir("./data/images/"+str(layer_name)+"/")
    Image.fromarray(np.squeeze(save_im)).save("./data/images/"+str(layer_name)+"/"+str(name)+".png")