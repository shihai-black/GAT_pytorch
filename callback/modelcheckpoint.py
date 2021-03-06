# _*_coding:utf-8_*_
# 作者      ：46925
# 创建时间  ：2020/11/1614:08  
# 文件      ：modelcheckpoint.py
# IDE       ：PyCharm
import os
import numpy as np
import torch
from datetime import datetime


class ModelCheckPoint(object):
    def __init__(self, model, optimizer, log, filename, name=None, epoch_freq=1, mode='min',
                 save_best_model=True,patience=10):
        self._model = model
        self._optimizer = optimizer
        self._now_data = datetime.now().strftime('%Y-%m-%d')
        self._name = name
        self._log = log
        self._filename = filename
        self._early_stop = False
        self._counter = 0
        self._patience = patience
        self._epoch_freq = epoch_freq
        self._save_best_model = save_best_model

        if mode == 'min':
            self._monitor_op = np.less
            self._best = np.Inf  # 正无穷
        else:
            self._monitor_op = np.greater
            self._best = -np.Inf  # 负无穷

    def save_info(self, epoch):
        state = {
            'module': self._name,
            'epoch': epoch,
            'state_dict': self._model.state_dict(),
            'optimizer': self._optimizer.state_dict(),
        }
        resume_path = os.path.join(self._filename,
                                   '{}-checkpoint-epoch.pth'.format(self._name))
        torch.save(state, resume_path)
        return state

    def step_save(self, state, current):
        epoch_path = os.path.join(self._filename,
                                  '{}-checkpoint-epoch.pth'.format(self._name))
        if self._save_best_model:
            if self._monitor_op(current, self._best):
                self._best = current
                state['best'] = self._best
                best_path = os.path.join(self._filename, '{}-model_best.pth'.format(state['module']))
                torch.save(state, best_path)
                self._log.info(f'save the best module where loss is {state["best"]}')
                self._counter = 0
            else:
                self._counter += 1
                self._log.info(f'EarlyStopping counter: {self._counter} out of {self._patience}')
                if self._counter>=self._patience:
                    self._early_stop = True

        else:
            if state['epoch'] % self._epoch_freq == 0:
                state['epoch'] += 1
                torch.save(state, epoch_path)
                self._log.info("\nEpoch %05d: save model to disk." % (state['epoch']))

        return state,self._early_stop
