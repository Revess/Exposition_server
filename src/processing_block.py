import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import tensorflow as tf
import numpy as np
from random import randint as rnd
from src.file_manager import save_image

class Processing_block():
    def __init__(self, global_manager, server, image_shape = (312,576,3)):
        self.global_manager = global_manager
        self.server = server
        self.image_shape = image_shape
        self.directory = "./data/input_images/"
        self.class_names = ["140-142","133-136","unkown","unkown_shard"]
        self.pred = None
       
        self.model = self.create_model(self.image_shape,len(self.class_names))
        self.model.load_weights(tf.train.latest_checkpoint("./data/models/final_model/"))
        self.activation_model = tf.keras.Model(inputs=self.model.input,outputs=[layer.output for layer in self.model.layers])
        self.layer_names = []
        for layer in self.activation_model.layers[1:]:
            self.layer_names.append(layer.name)

        self.settings = self.global_manager.finished_loading()

        self.settings = self.global_manager.get_settings()
        self.event = self.global_manager.get_event()[:-5]

    def create_model(self,image_shape,num_classes):
        model = tf.keras.Sequential([
            tf.keras.layers.experimental.preprocessing.Rescaling(1./255, input_shape=image_shape,name="inp"),
            tf.keras.layers.Conv2D(256, (3,3), padding='same', activation='relu',name="conv1"),
            tf.keras.layers.MaxPooling2D(name="mp1"),
            tf.keras.layers.Conv2D(128, (3,3), padding='same', activation='relu',name="conv2"),
            tf.keras.layers.MaxPooling2D(name="mp2"),
            tf.keras.layers.Conv2D(64, (3,3), padding='same', activation='relu',name="conv3"),
            tf.keras.layers.MaxPooling2D(name="mp3"),
            tf.keras.layers.Conv2D(32, (3,3), padding='same', activation='relu',name="conv4"),
            tf.keras.layers.MaxPooling2D(name="mp4"),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(image_shape[1]),
            tf.keras.layers.Dense(num_classes)
        ])

        model.compile(optimizer='adam',loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),metrics=['accuracy'])
        return model

    def stack(self,d3_array):                                                                                        ##Stack a 3d array into a 2d array
        d2_array = np.full(d3_array.shape[:2],"",dtype=object)
        for row_index in range(d3_array.shape[0]):
            for col_index in range(d3_array.shape[1]):
                for block_index in range(d3_array.shape[2]):
                    d2_array[row_index,col_index] += str(d3_array[row_index,col_index,block_index])+" | "
        return d2_array

    def run_time_based_values(self):
        while(True):
            self.settings = self.global_manager.get_settings()
            self.event = self.global_manager.get_event()[:-5]
            if self.global_manager.get_command() == 'exit':
                break

            if self.event == 'booting':
                for layer in self.model.layers:
                    if self.global_manager.get_command() == 'exit':
                        break
                    elif self.global_manager.get_event()[:-5] != 'booting':
                        break
                    weights = layer.get_weights()
                    if len(weights) > 1:
                        weights = weights[0]
                    weights = np.array(weights)
                    if "conv" in layer.name:
                        self.global_manager.set_progress_bar(layer.name+"weights",len(range(weights.shape[-1])))
                        for filter_kernel in range(weights.shape[-1]):
                            self.global_manager.update_progress_bar(layer.name+"weights",filter_kernel)
                            output = np.mean(weights[:,:,:,filter_kernel],axis=2)
                            self.server.send_message("/weights/"+str(layer.name)[:4]+"/"+str(layer.name)[4:]+"_"+str(filter_kernel),output+np.random.normal(loc=0,scale=0.01,size=output.shape))
                        self.global_manager.remove_progress_bar(layer.name+"weights")
                    elif "dense" in layer.name:
                        output = np.mean(weights,axis=0)
                        self.server.send_message("/weights/"+str(layer.name)[:5]+"/"+str(layer.name)[5:]+"0",output+np.random.normal(loc=0,scale=0.1,size=output.shape))

            if self.event == 'analysis':
                ##process the other variables
                for index,layer in enumerate(self.activation_model.layers):
                    if self.global_manager.get_command() == 'exit':
                        break
                    if layer.name[:4] == "conv":
                        kernel = np.array(layer.kernel)
                        for i in range(kernel.shape[-1]):
                            if self.global_manager.get_command() == 'exit':
                                break
                        self.server.send_message("/strides"+str(layer.name),str(layer.strides))
                        self.server.send_message("/filters"+str(layer.name),layer.filters)
                        self.server.send_message("/padding"+str(layer.name),layer.padding)
                        self.server.send_message("/class_names"+str(layer.name),self.class_names[np.argmax(tf.keras.activations.sigmoid(self.pred[0]))])

    def run_image_rendering(self):
        while(True):
            self.settings = self.global_manager.get_settings()
            self.event = self.global_manager.get_event()[:-5]
            if self.global_manager.get_command() == 'exit':
                break
              
            if self.event != 'analysis' and not self.global_manager.get_analysis_ready():
                image = os.listdir(self.directory)[self.global_manager.get_input_img()]
                img_array = tf.keras.preprocessing.image.load_img(self.directory+image, target_size=(312, 576),color_mode="rgb")
                img_array = tf.keras.preprocessing.image.img_to_array(img_array)
                img_array = tf.expand_dims(img_array, 0) # Create a batch
                prediction = self.activation_model.predict(img_array)
                self.pred = self.model.predict(img_array)
                self.global_manager.set_progress_bar("loading images",len(prediction))
                for index,layer in enumerate(prediction):
                    self.global_manager.update_progress_bar("loading images",index)
                    if self.global_manager.get_command() == 'exit':
                        break
                    layer_name = self.layer_names[index]
                    layer = np.squeeze(layer)
                    if "conv" in layer_name or "mp" in layer_name:
                        self.global_manager.set_progress_bar(layer_name,len(range(layer.shape[-1])))
                        for img in range(layer.shape[-1]):
                            if self.global_manager.get_command() == 'exit':
                                break
                            self.global_manager.update_progress_bar(layer_name,img)
                            if np.mean(layer[:,:,img]) == 0.0 or (np.mean(layer[:,:,img]) >= 95.0/255 and np.mean(layer[:,:,img]) < 97.0/255):
                                pass
                            else:
                                self.server.send_message("/system", layer[:10,:10,img]  )
                                save_image(layer[:,:,img],layer_name,img)
                        self.global_manager.remove_progress_bar(layer_name)
                    elif "dense" in layer_name or "flatten" in layer_name:
                        self.server.send_message("/system", layer[:4]  )
                        save_image(layer,layer_name,0,size=())
                self.global_manager.remove_progress_bar("loading images")
                self.global_manager.set_analysis_ready(True)
