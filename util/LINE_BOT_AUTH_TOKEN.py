# -*- coding: utf-8 -*-
"""
LINE_BOT_AUTH_TOKEN 認證郵件TOKEN驗證

@usage:

	def TOKEN_AUTH(arg_token)

	傳入參數說明:
		arg_token: 輸入參數TOKEN

@Note: 
	驗證成功後，寫入正式user資料檔

"""
import datetime
from dateutil.parser import parse
from dateutil import parser
import cx_Oracle
from linebot import LineBotApi
from linebot.models import TextSendMessage

### 以下import自行開發公用程式 ###
import util.APP_ENVIR_ARGS as APP_ENVIR_ARGS

def AUTH_URL_TOKEN(arg_token):
	#取得line token
	line_token = APP_ENVIR_ARGS.getArg('line_bot_arg','token')
	line_bot_api = LineBotApi(line_token)

	err_code = 0
	yu_empl_no = ""
	line_userid = ""
	str_dt = str(datetime.datetime.now())
	curr_dt = parser.parse(str_dt).strftime("%Y/%m/%d %H:%M:%S")

	#建立資料庫連線
	db_conn_str = APP_ENVIR_ARGS.getArg('ora_rp547a','conn_str')
	conn = cx_Oracle.connect(db_conn_str)

	#讀取驗證請求資料
	strsql  = "select EMPL_NO, LINE_USERID from LINEBOT_USER_AUTH "
	strsql += "where TOKEN = '" + arg_token + "' "

	#print(strsql)
	cursor = conn.cursor()
	cursor.execute(strsql)
	result = cursor.fetchone()

	if result != None:
		yu_empl_no = result[0]
		line_userid = result[1]

		#print(yu_empl_no + "帳號驗證通過.")

		strsql  = "select count(*) as CNT from LINEBOT_USER "
		strsql += "where EMPL_NO = '" + yu_empl_no + "' "
		#print(strsql)

		cursor.execute(strsql)
		result2 = cursor.fetchone()

		if result2[0] == 0:
			strsql  = "insert into LINEBOT_USER (EMPL_NO,LINE_USERID,TOKEN,USER_STATE"
			strsql += ") values ("
			strsql += "'" + yu_empl_no + "', "
			strsql += "'" + line_userid + "', "
			strsql += "'" + arg_token + "', "
			strsql += "'Y' "
			strsql += ") "

		else:
			strsql  = "update LINEBOT_USER set "
			strsql += "LINE_USERID = '" + line_userid + "', "
			strsql += "TOKEN = '" + arg_token + "' "
			strsql += "where EMPL_NO='" + yu_empl_no + "'"

		try:
			#print(strsql)
			cursor.execute(strsql)
			conn.commit()
		except cx_Oracle.DatabaseError as e:
			conn.execute("rollback")
			err_code = 2
			error, = e.args
			print("LINEBOT_USER_AUTH 資料庫操作錯誤:\n")
			print(strsql + "\n")
			print("sql_code=" + str(error.code) + "\n")
			print("err_msg=" + error.message + "\n")

		if err_code == 0:
			strsql  = "delete from LINEBOT_USER_AUTH where EMPL_NO= '" + yu_empl_no + "'"
			cursor.execute(strsql)
			conn.commit()

		#push message to one user
		line_bot_api.push_message(line_userid, 
			TextSendMessage(text='你好，你已通過郵件驗證，歡迎使用!'))

	else:
		err_code = 1
		print("查無驗證請求資料，帳號驗證失敗.")

	#Close SQL connection
	conn.close	

	return err_code, line_userid

	print(curr_dt + ' USER TOKEN 驗證結束.')


if __name__ == '__main__':
	print('請勿直接執行本程式...')