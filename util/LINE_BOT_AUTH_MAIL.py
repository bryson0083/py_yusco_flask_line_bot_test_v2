# -*- coding: utf-8 -*-
"""
LINE_BOT_AUTH_MAIL 帳號驗證郵件發送

@Usage: 
	def SEND_MAIL(arg_yu_empl_no, arg_line_userid)
	傳入參數說明:
		arg_yu_empl_no: 驗證請求之工號
		arg_line_userid: 驗證請求之Line ID

	return err_code
	err_code 代表意義 
	1: 帳號已驗證過，不再重複認證.
	2: 短時間重複認證請求.
	3: 資料庫操作錯誤.

@Note: 
	發送LINE Bot身分認證信件
	由傳入的工號(YU99999)、LINE USER ID，經加密成token
	透過發送公司內部郵件，讓使用者點選連結，進行內部工號確認

"""
import os
import smtplib
from email.mime.text import MIMEText
import datetime
from dateutil.parser import parse
from dateutil import parser
import hashlib
import cx_Oracle

### 以下import自行開發公用程式 ###
import util.APP_ENVIR_ARGS as APP_ENVIR_ARGS
import util.MAIL_SENDER as MAILER

def PROCESS_DATA(arg_yu_empl_no, arg_line_userid):
	err_code = 0

	date_fmt = "%Y/%m/%d %H:%M:%S"
	date_fmt2 = "%Y%m%d%H%M%S"

	str_dt = str(datetime.datetime.now())
	curr_dt = parser.parse(str_dt).strftime(date_fmt)
	curr_dt2 = parser.parse(str_dt).strftime(date_fmt2)

	target_str = str(arg_yu_empl_no) + str(arg_line_userid)
	a = str(target_str).encode('utf-8')
	token = hashlib.sha256(a).hexdigest()
	#print("New Token=" + token)

	#建立資料庫連線
	db_conn_str = APP_ENVIR_ARGS.getArg('ora_rp547a', 'conn_str')
	conn = cx_Oracle.connect(db_conn_str)

	#檢查是否已有驗證過
	strsql  = "select TOKEN from LINEBOT_USER "
	strsql += "where EMPL_NO = '" + arg_yu_empl_no + "' "

	#print(strsql)
	cursor = conn.cursor()
	cursor.execute(strsql)
	result = cursor.fetchone()

	if result != None:
		if token == result[0]:
			err_code = 1
			print(arg_yu_empl_no + "帳號已驗證過，不再重複認證.")

	if err_code == 0:
		#檢查是否已有發過驗證信
		strsql  = "select VERIFY_DATE, VERIFY_TIME from LINEBOT_USER_AUTH "
		strsql += "where EMPL_NO = '" + arg_yu_empl_no + "' "

		#print(strsql)
		cursor.execute(strsql)
		result = cursor.fetchone()

		if result != None:
			verify_dt = result[0] + result[1]

			a = datetime.datetime.strptime(verify_dt, date_fmt2)
			b = datetime.datetime.strptime(curr_dt2, date_fmt2)
			delta = b - a

			tot_diff_minu = delta.days * 1440 + delta.seconds / 60
			#print("tot_diff_minu=" + str(tot_diff_minu))

			if tot_diff_minu <= 2:
				err_code = 2
				print(arg_yu_empl_no + "短時間重複認證請求.")
			else:
				strsql  = "delete from LINEBOT_USER_AUTH where EMPL_NO= '" + arg_yu_empl_no + "'"
				cursor.execute(strsql)

	if err_code == 0:
		#寫入認證請求資料
		now = str(datetime.datetime.now())
		strsql  = "insert into LINEBOT_USER_AUTH (EMPL_NO,LINE_USERID,TOKEN,VERIFY_DATE,"
		strsql += "VERIFY_TIME) values ("
		strsql += "'" + arg_yu_empl_no + "', "
		strsql += "'" + arg_line_userid + "', "
		strsql += "'" + token + "', "
		strsql += "'" + parser.parse(now).strftime("%Y%m%d") + "', "
		strsql += "'" + parser.parse(now).strftime("%H%M%S") + "'"
		strsql += ") "

		try:
			#print(strsql)
			cursor.execute(strsql)
			conn.commit()
		except cx_Oracle.DatabaseError as e:
			conn.execute("rollback")
			err_code = 3
			error, = e.args
			print("LINEBOT_USER_AUTH 資料庫 insert 錯誤:\n")
			print(strsql + "\n")
			print("sql_code=" + str(error.code) + "\n")
			print("err_msg=" + error.message + "\n")

	#Close SQL connection
	conn.close

	return err_code, token


def SEND_MAIL(arg_yu_empl_no, arg_line_userid):
	rt_code = 0

	#進行認證請求資料處理
	rt_code, token = PROCESS_DATA(arg_yu_empl_no, arg_line_userid)
	#print("rt_code=" + str(rt_code))

	#如有錯誤則不繼續
	if rt_code != 0:
		return rt_code

	#發送驗證郵件
	str_dt = str(datetime.datetime.now())
	curr_dt = parser.parse(str_dt).strftime("%Y/%m/%d %H:%M:%S")

	recipient = arg_yu_empl_no + "@mail.yusco.com.tw"
	subject = "YUSCO Line Bot Authentication Email " + curr_dt

	msg_body  = '<html><head></head><body>'
	msg_body += '你好:<br>請點擊以下連結進行身分驗證.<br>'
	msg_body += '<a href="http://172.16.5.35:5000/auth?token=' + token + '">驗證連結</a>'
	msg_body += '<br><br><br>'
	msg_body += 'ps:<br>'
	msg_body += '1. 如果非你本人進行驗證，請勿點擊驗證連結.<br>'
	msg_body += '2. 本郵件自動發送，請勿回覆本郵件.<br>'
	msg_body += '</body></html>'

	rt_code, rt_desc = MAILER.SEND_MAIL(recipient, subject, msg_body, 'html')
	print("郵件發送回傳=>code=" + str(rt_code) + ",  desc=" + rt_desc)

	return rt_code

if __name__ == '__main__':
	print('請勿直接執行本程式...')