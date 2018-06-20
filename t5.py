# -*- coding: utf-8 -*-
import os
import pandas as pd

### 以下import自行開發公用程式 ###
#import MAIL_SENDER as MAILER
import util.TABLE_IMAGE_CONVT as tb_img_cvt


#DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 't5.py'))
#print(DATA_DIR)


df = pd.DataFrame()
df['日期22'] = ['2016-04-01', '2016-04-02', '2016-04-03']
df['calories'] = [2200, 2100, 1500]
df['sleep hours'] = [2200, 2100, 1500]
df['gym'] = [True, False, False]

tb_img_cvt.table_to_image(df,'tb_img2')

