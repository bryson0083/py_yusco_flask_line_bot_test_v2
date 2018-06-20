# -*- coding: utf-8 -*-
"""
MAIL_SENDER 郵件發送

@Usage: 
	發送郵件程式
	def SEND_MAIL(arg_recipient, arg_subject, arg_msg, arg_msg_type)

	傳入參數說明:
		arg_recipient: 收件者MAIL
		arg_subject: 郵件主旨
		arg_msg: 郵件內容
		arg_msg_type: 郵件內文型態('plain': 純文字, 'html': 網頁)

	return err_code
	err_code 代表意義 
	0: 正常結束
	1: 缺少收件者MAIL參數
	2: 其他錯誤

@Note: 


"""
import smtplib
from email.mime.text import MIMEText
import datetime
from dateutil.parser import parse
from dateutil import parser

### 以下import自行開發公用程式 ###
import util.APP_ENVIR_ARGS as APP_ENVIR_ARGS

def SEND_MAIL(arg_recipient, arg_subject, arg_msg, arg_msg_type):
	rt_code = 0

	#取得郵件發送系統參數
	sender_host = APP_ENVIR_ARGS.getArg('mail_sender', 'host_ip')
	sender_port = APP_ENVIR_ARGS.getArg('mail_sender', 'host_port')
	sender_mail = APP_ENVIR_ARGS.getArg('mail_sender', 'sender_mail')
	sender_id = APP_ENVIR_ARGS.getArg('mail_sender', 'id')
	sender_pwd = APP_ENVIR_ARGS.getArg('mail_sender', 'pwd')

	rt_desc = ""
	if len(arg_recipient) == 0:
		rt_code = 1
		rt_desc = "缺少收件者MAIL參數."

	if len(arg_subject) == 0:
		arg_subject = "無主旨"

	if len(arg_msg) == 0:
		arg_msg = " "

	if len(arg_msg_type) == 0:
		arg_msg_type = "plain"

	if rt_code == 0:
		str_dt = str(datetime.datetime.now())
		curr_dt = parser.parse(str_dt).strftime("%Y/%m/%d %H:%M:%S")
		recipient = arg_recipient

		msg = MIMEText(arg_msg, arg_msg_type)
		msg['Subject'] = arg_subject
		msg['From'] = sender_mail
		msg['To'] = recipient

		try:
			server = smtplib.SMTP(sender_host, sender_port)
			server.ehlo()
			server.login(sender_id, sender_pwd)
			server.send_message(msg)
			server.quit()
			print(curr_dt + ' Email sent.')
		except Exception as e:
			rt_code = 2
			print("Err exception from MAIL_SENDER")
			print(str(e.args[0]))
			f = open("MAIL_SENDER_LOG.txt", "a")
			f.write("MAIL_SENDER Err:\n" + curr_dt + "\n" + str(e.args) + "\n\n")
			f.close()
			print('The mail not sent.')

	return rt_code, rt_desc

if __name__ == '__main__':
	print('請勿直接執行本程式...')	