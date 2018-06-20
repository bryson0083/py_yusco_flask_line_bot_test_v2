# -*- coding: utf-8 -*-
"""
TABLE_IMAGE_CONVT 表格數據資料轉圖片輸出(PNG)

@Usage: 
    def table_to_image(arg_df, arg_img_name)

    傳入參數說明:
        arg_df: 傳入Data Frame資料
        arg_img_name: 傳入最後產生之圖檔名

    無回傳參數

@Note: 


"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):

    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

def table_to_image(arg_df, arg_img_name):
    img_name = arg_img_name + ".png"
    render_mpl_table(arg_df, header_columns=0, col_width=2.0)
    plt.savefig(img_name)

if __name__ == "__main__":
    print('請勿直接執行本程式...')