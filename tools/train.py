"""
---
name: train.py
description: IknowU train package
copyright: 2020 Marcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@telefonica.com
change-log: Check CHANGELOG.md file.
"""

import os
import contextlib
import json

# 0 = all messages are logged (default behavior)
# 1 = INFO messages are not printed
# 2 = INFO and WARNING messages are not printed
# 3 = INFO, WARNING, and ERROR messages are not printed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

with contextlib.redirect_stdout(None):
    import tensorflow as tf  # pylint: disable=import-error
    from keras_preprocessing.image import ImageDataGenerator  # pylint: disable=import-error


class Train():
    """
    description:
    """

    __version__ = 0.02

    def __init__(self):
        self.__directory = None
        self.__dir_training = None
        self.__dir_evaluate = None
        self.__model = None
        self.__generator_training = None
        self.__generator_evaluate = None

    def config(self, directory=None):
        """
        description:
        """
        if directory:
            self.__directory = directory
            self.__dir_training = os.path.join(self.__directory, 'training')
            self.__dir_evaluate = os.path.join(self.__directory, 'evaluate')
            directories = (self.__dir_training, self.__dir_evaluate)
            for i in directories:
                if not os.path.isdir(i):
                    return \
                        {
                            'error': {
                                'message': 'Directory not found: ' + i
                            }
                        }
        return {}

    def _datagen(self):
        # Set data generator
        datagen_training = ImageDataGenerator(
            rescale=1/255,
            rotation_range=90,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            fill_mode='nearest')
        datagen_evaluate = ImageDataGenerator(
            rescale=1/255)
        # Set image directories
        self.__generator_training = datagen_training.flow_from_directory(
            self.__dir_training,
            target_size=(150, 150),
            class_mode='categorical')
        self.__generator_evaluate = datagen_evaluate.flow_from_directory(
            self.__dir_evaluate,
            target_size=(150, 150),
            class_mode='categorical')

    def _model(self):
        self.__model = tf.keras.models.Sequential([
            # Note the input shape is the desired size of the image 150x150 with 3 bytes color
            # This is the first convolution
            tf.keras.layers.Conv2D(
                64, (3, 3),
                activation='relu',
                input_shape=(150, 150, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            # The second convolution
            tf.keras.layers.Conv2D(
                64, (3, 3),
                activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            # The third convolution
            tf.keras.layers.Conv2D(
                128, (3, 3),
                activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            # The fourth convolution
            tf.keras.layers.Conv2D(
                128, (3, 3),
                activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            # Flatten the results to feed into a DNN
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dropout(0.5),
            # 512 neuron hidden layer
            tf.keras.layers.Dense(
                512,
                activation='relu'),
            tf.keras.layers.Dense(
                3,
                activation='softmax')])
        self.__model.compile(
            loss='categorical_crossentropy',
            optimizer='rmsprop',
            metrics=['accuracy'])
        self.__model.summary()

    def _save(self):
        model_file_path = os.path.join(self.__directory, 'model.h5')
        self.__model.save(model_file_path)

    def run(self):
        """
        description:
        """
        self._datagen()
        self._model()
        history = self.__model.fit(
            self.__generator_training,
            epochs=25,
            validation_data=self.__generator_evaluate,
            verbose=True)
        self._save()
        history_str = str(history.history).replace('\'', '"')
        history_dic = json.loads(history_str)
        return \
            {
                'results': {
                    'history': history_dic,
                    'epocs': len(history.history['accuracy'])
                }
            }
