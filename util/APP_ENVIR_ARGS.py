# -*- coding: utf-8 -*-
"""
APP_ENVIR_ARGS 取得系統設定參數值

@Usage: 
	def getArg(arg_group, arg_name)

		--傳入參數說明:
		  arg_group: 參數組別
		  arg_name: 參數名稱

		return value
		--傳入參數說明:	
		  value: 回傳取得系統參數值

@Note: 


"""
import os
import json

def getArg(arg_group, arg_name):

	fpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'envir_args.json'))
	#print(fpath)

	#讀取參數檔
	with open(fpath) as data_file:
		data = json.load(data_file)

	value = data[arg_group][arg_name]

	return value

if __name__ == '__main__':
	print('請勿直接執行本程式...')	