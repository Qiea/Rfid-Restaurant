import logging
from datetime import datetime, timezone, timedelta
import encodings.idna
from decimal import Decimal
import serial
import serial.tools.list_ports
import time
import json
import pymysql
from collections import Counter


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# 配置logging，将日志输出到文件rfid.log和readrfid.log中
readrfid_log_handler = logging.FileHandler('readrfid.log')
# 设置日志级别
readrfid_log_handler.setLevel(logging.DEBUG)
# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
readrfid_log_handler.setFormatter(formatter)
# 添加文件处理程序到日志记录器
logging.getLogger().addHandler(readrfid_log_handler)


# rfid_log_handler = logging.FileHandler('rfid.log')
# rfid_log_handler.setLevel(logging.DEBUG)
# rfid_log_handler.setFormatter(formatter)
# logging.getLogger().addHandler(rfid_log_handler)


class mysql:
    data_list = []
    tabel_data_list = []
    admin_card_list = []
    db_connection = pymysql.connect(
        host="qiea.cc",  # 数据库主机
        user="rfid",  # 数据库用户名
        password="rfid",  # 数据库密码
        database="rfid"  # 数据库名称
    )
    cursor = db_connection.cursor()

    def connect(self):
        logging.info("正在连接数据库...")
        if self.db_connection:
            logging.info("数据库连接成功")
            self.cursor.execute("SELECT * FROM menu_copy")
            results = self.cursor.fetchall()
            for row in results:
                self.data_list.append(row)
            self.cursor.execute("SELECT * FROM menu_table_copy")
            results = self.cursor.fetchall()
            for row in results:
                self.tabel_data_list.append(row)
            self.cursor.execute("SELECT * FROM menu_admin_copy")
            results = self.cursor.fetchall()
            for row in results:
                self.admin_card_list.append(row)


mysql = mysql()


class jsondata:
    matching_items_dict: dict
    all_money_as_float: float
    local_time: str
    matching_table: int
    admin_cards: dict

    def getjsondata(self):
        matching_items_dict = {}
        matching_items = []
        matching_money = []
        matching_table = rfid.matching_tables[0]
        for i in range(len(rfid.rfid_data_list)):
            for item in mysql.data_list:
                if item[5] == rfid.epc_data[i]:
                    matching_items.append((item[1], 1))  # 将第二个数据添加到结果列表
                    matching_money.append(item[2])
        # 将每种物品的名称和数量放入字典中
        all_money_as_float = float(sum(matching_money))
        sha_tz = timezone(
            timedelta(hours=8),
            name='Asia/Shanghai',
        )
        beijing_now = datetime.now(timezone.utc).astimezone(sha_tz)
        date_string = beijing_now.date().strftime('%Y-%m-%d')
        time_string = beijing_now.strftime('%H:%M:%S')
        local_time = date_string + ' ' + time_string
        for item_name, total_quantity in Counter(matching_items).items():
            matching_items_dict[item_name] = total_quantity
        matching_items_dict = {f"{key[0]}": value for key, value in matching_items_dict.items()}
        self.matching_items_dict = matching_items_dict
        self.all_money_as_float = all_money_as_float
        self.local_time = local_time
        self.matching_table = matching_table
        self.admin_cards = rfid.admin_cards
        return self

    def send_orderdata_tomysql(self):
        order_jsoninfo = self.getjsondata()
        _mysqldata = {
            "all_items": order_jsoninfo.matching_items_dict,
            "allmoney": order_jsoninfo.all_money_as_float,
            "order_time": order_jsoninfo.local_time,
            "table": order_jsoninfo.matching_table,
            "admin": order_jsoninfo.admin_cards
        }
        json_send_data = json.dumps(_mysqldata, ensure_ascii=False)
        insert_query = "INSERT INTO history_test (json_data) VALUES (%s)"
        mysql.cursor.execute(insert_query, (json_send_data,))
        mysql.db_connection.commit()
        return _mysqldata


jsondata = jsondata()


class rfid:
    hex_string_16_nospace: str
    rfid_data_list: list
    epc_data: list
    matching_tables: list
    admin_cards: dict

    def startrfid(self):
        clear_screen()
        ser.flushInput()  # 清空接收缓冲区
        time.sleep(0.1)
        rfid.ser.send.startread()
        progress_bar(1, 6, "正在读取卡片信息"); clear_screen()
        rfid.ser.send.stopread()
        logging.info("正在分析卡片信息："); update.log()
        time.sleep(0.1)
        rfid.ser.send.return_and_clear()
        time.sleep(0.1)

    class message:
        def cardinfo(self):
            time.sleep(0.1)
            logging.info("共检测到 %d 张卡片", len(rfid.rfid_data_list))
            update.log()

        def tableinfo(self):
            logging.info("检测到 %d 号桌卡", rfid.matching_tables[0])
            logging.info("请在10秒内刷【收银卡】以确认订单")
            update.log()

        def orderinfo(self, _mysqldata):
            clear_screen()
            logging.info("检测到管理员：%s", rfid.admin_cards)
            update.log()
            logging.info("")
            logging.info("共检测到 %d 张卡片", len(rfid.rfid_data_list))
            logging.info("")
            for i, data in enumerate(rfid.rfid_data_list):
                rfid_data_list_temp = rfid.rfid_data_list[i]
                hex_string_epc_data = "".join(rfid_data_list_temp[7:11])
                rfid_hex_to_utf8_data = hex_string_epc_data.encode('utf-8')
                logging.info(f"卡 %d 相关数据: ", i + 1)
                logging.info("完整卡片数据(HEX): %s", "".join(rfid.rfid_data_list[i]))
                logging.info("EPC数据(HEXstring): %s", hex_string_epc_data)
                logging.info("EPC数据(UTF-8): %s", rfid_hex_to_utf8_data)
                logging.info("")
            logging.info("购买的物品有：%s", jsondata.matching_items_dict)
            logging.info("总消费 %s ￥", jsondata.all_money_as_float)
            logging.info("")
            logging.info("JSON数据如下：")
            logging.info(_mysqldata)
            logging.info("")
            logging.info("订单创建成功 5秒后将重新读卡......")
            update.log()
            time.sleep(5)

        class error:
            def nocard(self):
                logging.info("没有菜品")
                update.log()
                time.sleep(1)
                clear_screen()
                logging.info("没有检测到卡片，机器进入休眠")
                update.log()

            def normal(self, _char, _time):
                logging.info(_char)
                update.log()
                time.sleep(_time)
                clear_screen()

    class get:
        def hexdata(self):
            _read_cache_data = ser.read_all()  # 读取[15]个数据位的数据
            _hex_string_16_nospace = "".join(['{:02X}'.format(byte) for byte in _read_cache_data])
            return _hex_string_16_nospace

        def datalist(self, _hex_string_16_nospace):
            _rfid_data_list = []  # 保存每个A0开头的数据的数组
            rfid_current_data = []  # 当前正在解析的数据
            rfid_hex_byte_caches = [_hex_string_16_nospace[i:i + 2] for i in
                                    range(0, len(_hex_string_16_nospace), 2)]
            for RFID_hex_byte_cache in rfid_hex_byte_caches:
                rfid_current_data.append(RFID_hex_byte_cache)  # 将当前字节添加到当前数据中
                if RFID_hex_byte_cache == "A0":
                    if len(rfid_current_data) > 1:
                        _rfid_data_list.append(rfid_current_data[:-1])  # 除去当前A0之前的数据，将之前的数据添加到数组
                    rfid_current_data = ["A0"]  # 开始新的数据
            # 处理最后一个数据
            if len(rfid_current_data) > 1:
                _rfid_data_list.append(rfid_current_data)
            return _rfid_data_list

        def epcdata(self, _rfid_data_list):
            start_index = 7
            end_index = 11
            _epc_data = []
            for i, data in enumerate(_rfid_data_list):
                rfid_data_list_temp = _rfid_data_list[i]
                # 提取第8到第11字节的数据并将其合并为一个字符串
                hex_string_epc_data = "".join(rfid_data_list_temp[start_index:end_index])
                _epc_data.append(hex_string_epc_data)
            return _epc_data

        def tables(self):
            _tables = []
            for i in range(len(rfid.rfid_data_list)):
                for item in mysql.tabel_data_list:
                    if item[1] == rfid.epc_data[i]:
                        _tables.append(item[0])  # 将第二个数据添加到结果列表
            return _tables

        def admincards(self):
            _admin_cards = {}
            ser.flush()  # 清除发送文件
            ser.flushInput()  # 清空接收缓冲区
            ser.write(b'\xA0\x04\x00\x89\x01\xD2')
            ser.flush()  # 清除发送文件
            time.sleep(0.1)
            admin_rfid_data_list = rfid.get.datalist(rfid.get.hexdata())
            admin_epc_data = rfid.get.epcdata(admin_rfid_data_list)
            for i in (range(len(admin_rfid_data_list))):
                for item in mysql.admin_card_list:
                    if item[2] == admin_epc_data[i]:
                        _admin_cards[item[0]] = item[1]
            return _admin_cards

    class ser:
        class send:
            def startread(self):
                update.isreadcard = 1
                ser.flush()  # 清除发送文件
                ser.write(b'\xA0\x04\x00\x80\x01\xDB')
                ser.flush()  # 清除发送文件

            def onceread(self):
                update.isreadcard = 1
                ser.flushInput()  # 清空接收缓冲区
                ser.flush()  # 清除发送文件
                ser.write(b'\xA0\x0E\x00\x81\x01\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\xCD')
                time.sleep(0.1)

            def stopread(self):
                ser.flush()  # 清除发送文件
                ser.write(b'\xA0\x03\x00\x8C\xD1')
                ser.flush()  # 清除发送文件
                update.isreadcard = 0

            def clear(self):
                ser.flush()  # 清除发送文件
                ser.write(b'\xA0\x03\x00\x93\xCA')
                ser.flush()  # 清除发送文件
                update.isreadcard = 0

            def return_and_clear(self):
                ser.flush()  # 清除发送文件
                ser.flushInput()  # 清空接收缓冲区
                ser.write(b'\xA0\x03\x00\x91\xCC')
                ser.flush()  # 清除发送文件
                update.isreadcard = 0


rfid = rfid()
rfid.get = rfid.get()
rfid.message = rfid.message()
rfid.message.error = rfid.message.error()
rfid.ser = rfid.ser()
rfid.ser.send = rfid.ser.send()


class update:
    isreadcard = 0
    heartbeats = 0

    def log(self):
        clear_query = "DELETE FROM log WHERE log IS NULL"
        mysql.cursor.execute(clear_query)
        mysql.db_connection.commit()

        with open('readrfid.log', 'r') as file:
            log_content = file.read().strip()

        insert_query = "UPDATE log SET log = (%s)"  # Replace xxx with your column name
        mysql.cursor.execute(insert_query, (log_content,))
        mysql.db_connection.commit()
        update.heartbeat()

    def heartbeat(self):
        update_query = "UPDATE log SET HeartBeat = 1"
        mysql.cursor.execute(update_query)
        mysql.db_connection.commit()
        update.heartbeats += 1
        if update.heartbeats > 5 and update.isreadcard == 0:
            print("温度:", update.temp())
            update.heartbeats = 0

    def temp(self):
        ser.flush()  # 清除发送文件
        ser.flushInput()  # 清空接收缓冲区
        ser.write(b'\xA0\x03\x00\x7B\xE2')
        time.sleep(0.1)
        _rfid_data_list = rfid.get.datalist(rfid.get.hexdata())[0]
        _temp = int(_rfid_data_list[5], 16)
        update_query = "UPDATE log SET Temp = %s"
        mysql.cursor.execute(update_query, (_temp,))
        mysql.db_connection.commit()
        ser.flush()  # 清除发送文件
        ser.flushInput()  # 清空接收缓冲区
        return _temp


update = update()


def progress_bar(_n, _tasks_per_segment, _char):
    total_tasks = _n * _tasks_per_segment
    for i in range(1, total_tasks + 1):
        progress = i / total_tasks
        logging.info(_char)
        bar_length = 50
        progress = min(max(progress, 0), 1)
        block = int(round(bar_length * progress))
        _progress_bar = "#" * block + "-" * (bar_length - block)
        logging.info(f"[{_progress_bar}] {int(progress * 100)}%")
        clear_screen()
        time.sleep(0.1)


def clear_screen():
    update.log()
    with open('readrfid.log', 'w') as file:
        file.write("")


def debug_buzzer(times, islong):
    ser.flush()  # 清除发送文件
    ser.write(b'\xA0\x04\x00\x7A\x01\xE1')
    for i in range(times):
        ser.flush()  # 清除发送文件
        ser.write(b'\xA0\x0E\x00\x81\x01\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\xCD')
        ser.flush()  # 清除发送文件
        if islong == 1:
            time.sleep(1)
        time.sleep(0.1)
        ser.flush()  # 清除发送文件
    time.sleep(1)
    ser.write(b'\xA0\x04\x00\x7A\x00\xE2')
    ser.flush()  # 清除发送文件
    ser.flushInput()  # 清空接收缓冲区


def debug_buzzer_test():
    ser.flushInput()  # 清空接收缓冲区
    ser.flush()  # 清除发送文件
    ser.write(b'\xA0\x04\x00\x7A\x01\xE1')
    ser.flush()  # 清除发送文件
    ser.write(b'\xA0\x0E\x00\x81\x01\x00\x00\x00\x02\x00\x01\x00\x00\x00\x00\xCD')
    ser.flush()  # 清除发送文件
    time.sleep(1)
    ser.write(b'\xA0\x04\x00\x7A\x00\xE2')
    ser.flush()  # 清除发送文件
    ser.flushInput()  # 清空接收缓冲区


# init初始化
ser = serial.Serial((serial.tools.list_ports.comports())[0].device, 115200, timeout=0)
mysql.connect()
ser.write(b'\xA0\x04\x00\x7A\x00\xE2')  # 蜂鸣器静音
debug_buzzer(2, 0)  # 开机提示

# Main
while True:
    rfid.startrfid()
    hex_string_16_nospace = rfid.get.hexdata()
    if hex_string_16_nospace != "A00400913893":  # 若检测到卡片
        rfid.rfid_data_list = rfid.get.datalist(hex_string_16_nospace)
        rfid.epc_data = rfid.get.epcdata(rfid.rfid_data_list)
        rfid.matching_tables = rfid.get.tables()
        rfid.message.cardinfo()
        if len(rfid.matching_tables) == 1:  # 若检测到单张桌卡(满足条件)
            rfid.message.tableinfo()
            debug_buzzer(3, 0)
            start_time = time.time()
            while True:
                update.heartbeat()
                rfid.admin_cards = admin_cards = rfid.get.admincards()
                if len(admin_cards) >= 1:  # 若检测到管理员
                    rfid.ser.send.stopread(); rfid.ser.send.clear()
                    debug_buzzer(1, 0)
                    mysqldata = jsondata.send_orderdata_tomysql()
                    rfid.message.orderinfo(mysqldata)
                    break
                if len(admin_cards) == 0 and time.time() - start_time >= 10:
                    rfid.ser.send.stopread(); rfid.ser.send.clear()
                    rfid.message.error.normal("未检测到【收银卡】，请再试一次", 2)
                    break
        elif len(rfid.matching_tables) > 1:
            rfid.message.error.normal("检测到【多张】桌卡，请检查卡片", 2)
        else:
            rfid.message.error.normal("未检测到【桌卡】，请检查卡片", 2)
    elif hex_string_16_nospace == "A00400913893":  # 若检测不到卡片
        rfid.message.error.nocard()
        start_time = time.time()
        while True:
            if (time.time() - start_time) <= 10:
                print("待机状态:S0")
                update.heartbeat()
                rfid.ser.send.onceread()
                if rfid.get.hexdata() != "" and rfid.get.hexdata() != "A004008110CBA004008136A5":
                    rfid.message.error.normal("发现卡片，进入工作", 1); break
                update.isreadcard = 0
                time.sleep(1)
            elif (time.time() - start_time) <= 60:
                print("待机状态:S1")
                update.heartbeat()
                rfid.ser.send.onceread()
                if rfid.get.hexdata() != "" and rfid.get.hexdata() != "A004008110CBA004008136A5":
                    rfid.message.error.normal("发现卡片，进入工作", 1); break
                update.isreadcard = 0
                time.sleep(3)
            elif (time.time() - start_time) > 60:
                print("待机状态:S2")
                update.heartbeat()
                rfid.ser.send.onceread()
                if rfid.get.hexdata() != "" and rfid.get.hexdata() != "A004008110CBA004008136A5":
                    rfid.message.error.normal("发现卡片，进入工作", 1); break
                update.isreadcard = 0
                time.sleep(5)
    else:
        rfid.message.error.normal("未知错误", 2)
