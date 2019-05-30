#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tensorflow as tf
import numpy as np
import time
import os
from sklearn.preprocessing import LabelEncoder
import re
import collections
import random
import pickle


# In[3]:


maxlen = 20
location = os.getcwd()
num_layers = 3
size_layer = 256
learning_rate = 0.0001
batch = 100


# In[4]:


with open("dataset-emotion.p", "rb") as fopen:
    df = pickle.load(fopen)
with open("vector-emotion.p", "rb") as fopen:
    vectors = pickle.load(fopen)
with open("dataset-dictionary.p", "rb") as fopen:
    dictionary = pickle.load(fopen)


# In[5]:


label = np.unique(df[:, 1])


# In[ ]:


from sklearn.cross_validation import train_test_split

train_X, test_X, train_Y, test_Y = train_test_split(df[:, 0], df[:, 1].astype("int"), test_size=0.2)


# In[ ]:


class Model:
    def __init__(
        self,
        num_layers,
        size_layer,
        dimension_input,
        dimension_output,
        attention_size,
        learning_rate,
    ):
        def lstm_cell():
            return tf.nn.rnn_cell.LSTMCell(size_layer)

        self.rnn_cells = tf.nn.rnn_cell.MultiRNNCell([lstm_cell() for _ in range(num_layers)])
        self.X = tf.placeholder(tf.float32, [None, None, dimension_input])
        self.Y = tf.placeholder(tf.float32, [None, dimension_output])
        drop = tf.contrib.rnn.DropoutWrapper(self.rnn_cells, output_keep_prob=0.5)
        self.outputs, self.last_state = tf.nn.dynamic_rnn(drop, self.X, dtype=tf.float32)
        attention_w = tf.get_variable("attention_v", [attention_size], tf.float32)
        query = tf.layers.dense(tf.expand_dims(self.last_state[-1].h, 1), attention_size)
        keys = tf.layers.dense(self.outputs, attention_size)
        align = tf.reduce_sum(attention_w * tf.tanh(keys + query), [2])
        align = tf.nn.softmax(align)
        self.outputs = tf.squeeze(
            tf.matmul(tf.transpose(self.outputs, [0, 2, 1]), tf.expand_dims(align, 2)), 2
        )
        self.rnn_W = tf.Variable(tf.random_normal((size_layer, dimension_output)))
        self.rnn_B = tf.Variable(tf.random_normal([dimension_output]))
        self.logits = tf.matmul(self.outputs, self.rnn_W) + self.rnn_B
        self.cost = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(logits=self.logits, labels=self.Y)
        )
        l2 = sum(0.0005 * tf.nn.l2_loss(tf_var) for tf_var in tf.trainable_variables())
        self.cost += l2
        self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(self.cost)
        self.correct_pred = tf.equal(tf.argmax(self.logits, 1), tf.argmax(self.Y, 1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))


# In[ ]:


tf.reset_default_graph()
sess = tf.InteractiveSession()
model = Model(num_layers, size_layer, vectors.shape[1], label.shape[0], 50, learning_rate)
sess.run(tf.global_variables_initializer())
dimension = vectors.shape[1]
saver = tf.train.Saver(tf.global_variables())
EARLY_STOPPING, CURRENT_CHECKPOINT, CURRENT_ACC, EPOCH = 10, 0, 0, 0
while True:
    lasttime = time.time()
    if CURRENT_CHECKPOINT == EARLY_STOPPING:
        print("break epoch:", EPOCH)
        break
    train_acc, train_loss, test_acc, test_loss = 0, 0, 0, 0
    for i in range(0, (train_X.shape[0] // batch) * batch, batch):
        batch_x = np.zeros((batch, maxlen, dimension))
        batch_y = np.zeros((batch, len(label)))
        for k in range(batch):
            tokens = train_X[i + k].split()[:maxlen]
            emb_data = np.zeros((maxlen, dimension), dtype=np.float32)
            for no, text in enumerate(tokens[::-1]):
                try:
                    emb_data[-1 - no, :] += vectors[dictionary[text], :]
                except Exception as e:
                    print(e)
                    continue
            batch_y[k, int(train_Y[i + k])] = 1.0
            batch_x[k, :, :] = emb_data[:, :]
        loss, _ = sess.run(
            [model.cost, model.optimizer], feed_dict={model.X: batch_x, model.Y: batch_y}
        )
        train_loss += loss
        train_acc += sess.run(model.accuracy, feed_dict={model.X: batch_x, model.Y: batch_y})

    for i in range(0, (test_X.shape[0] // batch) * batch, batch):
        batch_x = np.zeros((batch, maxlen, dimension))
        batch_y = np.zeros((batch, len(label)))
        for k in range(batch):
            tokens = test_X[i + k].split()[:maxlen]
            emb_data = np.zeros((maxlen, dimension), dtype=np.float32)
            for no, text in enumerate(tokens[::-1]):
                try:
                    emb_data[-1 - no, :] += vectors[dictionary[text], :]
                except:
                    continue
            batch_y[k, int(test_Y[i + k])] = 1.0
            batch_x[k, :, :] = emb_data[:, :]
        loss, acc = sess.run(
            [model.cost, model.accuracy], feed_dict={model.X: batch_x, model.Y: batch_y}
        )
        test_loss += loss
        test_acc += acc

    train_loss /= train_X.shape[0] // batch
    train_acc /= train_X.shape[0] // batch
    test_loss /= test_X.shape[0] // batch
    test_acc /= test_X.shape[0] // batch
    if test_acc > CURRENT_ACC:
        print("epoch:", EPOCH, ", pass acc:", CURRENT_ACC, ", current acc:", test_acc)
        CURRENT_ACC = test_acc
        CURRENT_CHECKPOINT = 0
        saver.save(sess, os.getcwd() + "/model-rnn-vector.ckpt")
    else:
        CURRENT_CHECKPOINT += 1
    EPOCH += 1
    print("time taken:", time.time() - lasttime)
    print(
        "epoch:",
        EPOCH,
        ", training loss:",
        train_loss,
        ", training acc:",
        train_acc,
        ", valid loss:",
        test_loss,
        ", valid acc:",
        test_acc,
    )


# In[ ]:
