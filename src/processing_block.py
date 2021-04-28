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
       
        self.model = self.create_model(self.image_shape,len(self.class_names))
        self.model.load_weights(tf.train.latest_checkpoint("./data/models/final_model/"))
        self.activation_model = tf.keras.Model(inputs=self.model.input,outputs=[layer.output for layer in self.model.layers])
        self.layer_names = []
        for layer in self.activation_model.layers[1:]:
            self.layer_names.append(layer.name)

        self.settings = self.global_manager.get_settings()
        self.event = self.settings["event_order"][self.global_manager.get_event_header()]

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

    def run_process(self):
        while(True):
            self.settings = self.global_manager.get_settings()
            self.event = self.settings["event_order"][self.global_manager.get_event_header()]
            if self.global_manager.get_command() == 'exit':
                break

            if self.event == 'context':
                image = os.listdir(self.directory)[rnd(0,len(os.listdir(self.directory))-1)]
                ##Open and process the image
                img_array = tf.keras.preprocessing.image.load_img(self.directory+image, target_size=(312, 576),color_mode="rgb")
                img_array = tf.keras.preprocessing.image.img_to_array(img_array)
                img_array = tf.expand_dims(img_array, 0) # Create a batch
                ##Create the layer outputs and the model prediction
                prediction = self.activation_model.predict(img_array)
                pred = self.model.predict(img_array)

                ##Create the booting sequence
                for layer in self.model.layers:
                    if self.global_manager.get_command() == 'exit':
                        break
                    weights = layer.get_weights()
                    if len(weights) > 1:
                        weights = weights[0]
                    weights = np.array(weights)
                    if weights.shape[0] > 512:
                        for i in range(weights.shape[0]):
                            if self.global_manager.get_command() == 'exit':
                                break
                            self.server.send_message("/weights/"+str(layer.name)+"/"+str(i),weights[i,:])
                    else:
                        for i in range(weights.shape[-1]):
                            if self.global_manager.get_command() == 'exit':
                                break
                            if len(weights.shape) >= 3:
                                self.server.send_message("/weights/"+str(layer.name)+"/"+str(i),weights[:,:,:,i])
                            else:
                                self.server.send_message("/weights/"+str(layer.name)+"/"+str(i),weights[:,i])
                
                self.global_manager.set_finished_processes(True)

            if self.event == 'analysis':
                ##Save images in between the layers
                for index,layer in enumerate(prediction):
                    if self.global_manager.get_command() == 'exit':
                        break
                    layer = np.squeeze(layer)
                    if len(layer.shape) == 3:
                        for i in range(layer.shape[-1]):
                            if self.global_manager.get_command() == 'exit':
                                break
                            save_image(np.array(layer[:,:,i]),self.layer_names[index],i)
                            # if layer_names[index][:4] == "conv":
                                # save_image(activation_model.layers[index+1].activation(np.copy(np.array(layer[:,:,i]))),layer_names[index]+"relu_activation",i)
                    elif len(layer.shape) == 1:
                        save_image(np.array(layer),self.layer_names[index],i)

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
                        self.server.send_message("/class_names"+str(layer.name),self.class_names[np.argmax(tf.keras.activations.sigmoid(pred[0]))])
                
                self.global_manager.set_finished_processes(True)
