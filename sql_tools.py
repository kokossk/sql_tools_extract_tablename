#!/bin/python
# _*_ coding:utf8 _*_

import tkinter as tk
from tkinter import  Button,Canvas, FLAT, BOTTOM, S
from tkinter.filedialog import askopenfilename as tkfile
import win32.win32clipboard as win32clipboard
from logo import img
import os
import base64
from sql_tools.input_output import Input_file
from sql_tools.relationship import SqlExtractor
import winreg
import time

def main():
    root = tk.Tk()
    root.title("sql_tools")
    w = 900
    h = 570
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.resizable(0, 0)
    edit(root)
    tmp = open("tmp.ico","wb+")
    tmp.write(base64.b64decode(img))
    tmp.close()
    root.iconbitmap("tmp.ico")
    os.remove("tmp.ico")
    root.mainloop()


def edit(root):

    remark = tk.Label(root, bg='lightblue', text="待处理数据", font=('微软雅黑', '10'))
    remark.grid(row=0, column=0)

    #  open file
    re_file = tk.Button(root, bg='lightblue', text='打开文件', font=('微软雅黑', '10'), command=lambda: read_file(text))
    re_file.grid(row=0, column=1)

    # save result file
    save_file = tk.Button(root, bg='lightblue', text='保存结果到桌面', font=('微软雅黑', '10'), command=lambda: save_result_file(text))
    save_file.grid(row=0, column=2)

    # 说明
    explain_mess = tk.Button(root, bg='lightblue', text='关于 Sql_tools', font=('微软雅黑', '10'), command=lambda: show_sql_tools())
    explain_mess.grid(row=0, column=3)

    # 输入文本
    edit = tk.Text(root,  font='微软雅黑', width=45, height=23)
    edit.grid(row=1, column=0, rowspan=15, columnspan=10)

    # 功能按钮
    re01 = tk.Label(root,text='Function', bg='#FFB6C1', width=10, height='1')
    re01.grid(row=1, column=10)

    sub1 = tk.Button(root, bg='#87CEEB', text='查询IN', width=10, height='1', command=lambda: sql_cx_in(text))
    # sub1.config(height='1')
    sub1.grid(row=2, column=10, pady='1')

    sub2 = tk.Button(root, bg='#87CEEB', text='美化SQL', width=10, height='1', command=lambda: beautiful_sql(text))
    sub2.grid(row=3, column=10)

    sub3 = tk.Button(root, bg='#87CEEB', text='Select', width=10, height='1', command=lambda: sql_select(text))
    sub3.grid(row=4, column=10)

    sub4 = tk.Button(root, bg='#87CEEB', text='Insert', width=10, height='1', command=lambda: sql_insert(text))
    sub4.grid(row=5, column=10)

    sub5 = tk.Button(root, bg='#87CEEB', text='Create', width=10, height='1', command=lambda: sql_create_tab(text))
    sub5.grid(row=6, column=10)

    sub6 = tk.Button(root, bg='#87CEEB', text='提取表名', width=10, height='1', command=lambda: get_table_name(text))
    sub6.grid(row=7, column=10)

    sub7 = tk.Button(root, bg='#87CEEB', text='提取依赖', width=10, height='1', command=lambda: get_relationship(text))
    sub7.grid(row=8, column=10)

    sub8 = tk.Button(root, bg='#FFB6C1', text='Clear', width=10, height='1', command=lambda: (edit.delete(1.0, tk.END),result.delete(1.0, tk.END)))
    sub8.grid(row=9, column=10)

    # 输出结果
    result = tk.Text(root, font='微软雅黑', width=45, height=23)
    result.grid(row=1, column=12, rowspan=15, columnspan=90)
    # 设置滚动条
    result_data_scrollbar_y = tk.Scrollbar(root)
    result_data_scrollbar_y.config(command=result.yview)
    result.config(yscrollcommand=result_data_scrollbar_y.set)
    result_data_scrollbar_y.grid(row=1, column=101, rowspan=15, sticky='NS')

    cp = tk.Button(root, bg='#2E8B57', text='Copy', font=('微软雅黑','11'), width=80, height=1, command=lambda: copy(text))
    cp.grid(row=20, column=0, rowspan=16, columnspan=100, pady='4')

    text = [edit, result]
    return text


def beautiful_sql(text):
    edit, result = text[0], text[1]
    result.delete(1.0, tk.END)
    data = edit.get(1.0, tk.END)
    re1 = Input_file(data)
    re2 = re1.mp_sql_beautiful()
    for line in re2:
        result.insert('end', line+'\n')
        result.focus_force()
    return True


def sql_cx_in(text):
    edit, result = text[0], text[1]
    result.delete(1.0, tk.END)
    data = edit.get(1.0, tk.END)
    re1 = Input_file(data)
    re2 = re1.replace_whitespace_with_space()
    re3 = str(re2)
    if len(re2) == 0:
        pass
    else:
        re4 = re3.replace('[', '(')
        re5 = re4.replace(']', ')')
        result.insert('end', re5)
        result.focus_force()
    return True


def sql_select(text):
    file_data, result = text[0], text[1]
    result.delete(1.0, tk.END)
    data = file_data.get(1.0, tk.END)
    re1 = Input_file(data)
    re2 = re1.cx_select()
    for line in re2:
        result.insert('end', line+'\n')
        result.focus_force()
    return True


def sql_insert(text):
    file_data, result = text[0], text[1]
    result.delete(1.0, tk.END)
    data = file_data.get(1.0, tk.END)
    re1 = Input_file(data)
    re2 = re1.insert_sql()

    if len(re2) > 0:
        for line in re2:
            result.insert('end', line)
            result.focus_force()

        result.insert('end', '\n\n')
        result.insert('end', '--------------------------'+'\n\n')

        for line in re2:
            result.insert('end', line+'\n')
            result.focus_force()
    return True


def sql_create_tab(text):
    file_data, result = text[0], text[1]
    result.delete(1.0, tk.END)
    data = file_data.get(1.0, tk.END)
    re1 = Input_file(data)
    re2 = re1.create_tab_sql()
    for line in re2:
        result.insert('end', line + '\n')
        result.focus_force()


def get_table_name(text):
    file_data, result = text[0], text[1]
    result.delete(1.0, tk.END)
    data = file_data.get(1.0, tk.END)
    sql_extraction = SqlExtractor(data)
    table_name = sql_extraction.tables
    for line in table_name:
        result.insert('end', line + '\n')
        result.focus_force()


def get_relationship(text):
    file_data, result = text[0], text[1]
    result.delete(1.0, tk.END)
    data = file_data.get(1.0, tk.END)
    all_key_list = []
    relationship_name = {}
    # 获取表名
    sql_extraction = SqlExtractor(data)
    table_name = sql_extraction.tables

    # 获取包 存储过程名
    re_sql_rela = Input_file(data)
    re_sql_rela.proc_relationship()
    pack_name = re_sql_rela.package_name
    proc_name = re_sql_rela.procedure_name

    # 生成 all_key_list
    for line in data.splitlines(True):
        line = line.upper()
        for pack_keyword in pack_name:
            if pack_keyword in line:
                all_key_list.append("PACK-"+pack_keyword.strip())
        for proc_keyword in proc_name:
            if proc_keyword in line:
                all_key_list.append("PROC-"+proc_keyword.strip())
        for table_keyword in table_name:
            if table_keyword in line:
                all_key_list.append("TABLE-"+''+table_keyword.strip())

    # 生成 relationship list
    if len(pack_name) > 0 or len(proc_name) > 0:
        i = 0
        pa_i = 0
        pr_i = 0
        if len(pack_name) > 0 and len(proc_name) > 0:
            for line in all_key_list[i:]:
                lin_split = line.split("-", 1)
                if lin_split[0] == 'PACK':
                    pack_1 = lin_split[1]
                    pa_i = 1
                if lin_split[0] == 'PROC':
                    proc_1 = lin_split[1]
                    pr_i = 1
                if lin_split[0] == 'TABLE':
                    table_1 = lin_split[1]
                    relationship_name[pack_1 + '-' + proc_1 + '-' + table_1] = pack_1 + '-' + proc_1

        elif len(pack_name) == 0 and len(proc_name) >0:
            for line in all_key_list[i:]:
                lin_split = line.split("-", 1)
                if lin_split[0] == 'PROC':
                    proc_1 = lin_split[1]
                    pr_i = 1
                if lin_split[0] == 'TABLE':
                    table_1 = lin_split[1]
                    relationship_name[proc_1 + '-' + table_1] = proc_1

    # 循环展示 包名 存储过程名称 包名
    line_str = "----------------------------------------"
    break_str = "\n"
    break_str2 = "\n\n"
    re_str_proc = ''
    re_str_tbl = ''
    re_str_proc = re_str_proc + break_str + (str("Result :").title()) + break_str
    if len(pack_name) > 0:
        re_str_proc = re_str_proc + line_str + break_str + (str("Package_name :").title())
        for out_item in pack_name:
            re_str_proc = re_str_proc + break_str + ' '*16 + out_item
    if len(proc_name) > 0:
        re_str_proc = re_str_proc + break_str + line_str + break_str + (str("Procedure_name :").title())
        for out_item in proc_name:
            re_str_proc = re_str_proc + break_str + ' '*16 + out_item
    if len(table_name) > 0:
        re_str_proc = re_str_proc + break_str + line_str + break_str + (str("Table_Name :").title())
        for out_item in table_name:
            re_str_proc = re_str_proc + break_str + ' '*16 + out_item

        re_str_proc = re_str_proc + break_str + line_str

    #  存储过程关系
    if len(relationship_name) > 0:
        len_out = len(str(max(zip(relationship_name.values())))) + 6
        itm1 = ([i for i in relationship_name.values()][0])
        h = 0
        re_str_tbl = break_str + re_str_tbl + (str("relationship :").title())
        if len(pack_name) > 0:
            for k, v in relationship_name.items():
                if v == itm1 and h == 0:
                    re_str_tbl = re_str_tbl + break_str + (str(k.split("-", 2)[0] + ' --> ' + k.split("-", 2)[1]).ljust(len_out) + k.split("-", 2)[2])
                    h += 1
                    itm1 = v
                elif v == itm1:
                    re_str_tbl = re_str_tbl + break_str + ' '*len_out + str((k.split("-", 2))[2])
                    itm1 = v
                else:
                    itm1 = v
                    h = 1
                    re_str_tbl = re_str_tbl + break_str2 + (str(k.split("-", 2)[0] + ' --> ' + k.split("-", 2)[1]).ljust(len_out) + k.split("-", 2)[2])

        else:
            for k, v in relationship_name.items():
                if v == itm1 and h == 0:
                    re_str_tbl = re_str_tbl + break_str2 + str(k.split("-", 1)[0] + ' --> ').ljust(len_out) + k.split("-", 2)[1]
                    h += 1
                    itm1 = v
                elif v == itm1:
                    re_str_tbl = re_str_tbl + break_str + ' '*len_out + str((k.split("-", 1))[1])
                    itm1 = v
                else:
                    itm1 = v
                    h = 1
                    re_str_tbl = re_str_tbl + break_str2 + str(k.split("-", 1)[0] + ' --> ').ljust(len_out) + k.split("-", 1)[1]

    else:
        None

    result_relationship_str = re_str_proc + break_str + re_str_tbl
    print(result_relationship_str)
    result.insert('end', result_relationship_str)
    result.focus_force()


def read_file(text):
    file_data, result = text[0], text[1]
    file_data.delete(1.0, tk.END)
    key = os.path.join(os.path.expanduser("~"), 'Desktop')
    file_path = tkfile(title=u'选择文件', initialdir=(os.path.expanduser(key)))

    try:
        with open(file_path, 'r', encoding="utf8") as a:
            re_file = a.read()
    except ImportError as e:
        print("读取文件出错")

    file_data.insert('end', re_file + '\n')
    file_data.focus_force()


# 2020 07 11 ADD
def save_result_file(text):
    edit_f, result = text[0], text[1]
    dec = str(result.get(1.0, tk.END))

    if len(dec) > 1:

        ti = time.strftime('%Y%m%d%H%M%S')
        out_file_name = 'output_' + str(ti) + '.sql'

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
            path1 = winreg.QueryValueEx(key, "Desktop")[0]
        except Exception as e:
            print('get path error !')

        try:
            path2 = os.path.join(os.path.expanduser('~'), "Desktop")
        except Exception as e:
            print('get path error !')


        if len(path1) > 0:
            out_file_path = path1 + '\\' + out_file_name
            try:
                with open(out_file_path, 'w', encoding="utf8") as file_object:
                    file_object.write(dec)
            except Exception as e:
                print("Write ERROR ")

        elif len(path2) > 0:
            out_file_path = path2 + '\\' + out_file_name
            try:
                with open(out_file_path, 'w', encoding="utf8") as file_object:
                    file_object.write(dec)
            except Exception as e:
                print("Write ERROR ")
    else:
        None


# def about_sql_tools():
#     msgBox = QMessageBox(QMessageBox.NoIcon, '关于 Casaba',
#                              '\n    这是一个免费工具，你可以再次更改或重新分发。工具目标是提升\n'
#                              '数据开发的效率，对数据开发中一些繁琐手工逻辑用工具替代。软件提\n'
#                              '取数据间的血缘关系部分功能还不完善，对于包、存储过程分析当前只\n'
#                              '实现提取包、存储过程依赖的表。后续尽快完善血缘分析功能。\n\n'
#                              '功能说明:\n'
#                               '  查询IN      :  生成查询语句 IN （） 语句\n'
#                               '  美化Sql     :  格式化SQL\n'
#                               '  Select       :  将输入的字段生成查询语句\n'
#                               '  Insert       :  将输入的字段生成Insert语句\n'
#                               '  Create      :  将输入的字段生成建表语句\n'
#                               '  提取表名    :  提取sql文件中涉及的表名\n'
#                               '  提取依赖    :  提取sql文件中包、存储过程、表之间的依赖关系'
#                               '\n'
#                               '\n'
#                               '注意事项 :\n'
#                               '  1)、 提取表名时如果程序中实际表名和表的别名相同会被排出。\n'
#                               '  2)、 提取依赖关系时如果sql存在语法问题可能提取不会成功。'
#                              '\n'
#                              '\n'
#                              '更新说明 :\n'
#                              '   最新版本更新时间: 2021-01-22'
#
#                              )
#     msgBox.setIconPixmap(QPixmap("33.png"))
#     msgBox.exec()

def show_sql_tools():
    root_mes = tk.Tk()
    root_mes.overrideredirect(True)
    root_mes.attributes("-alpha", 1)
    root_mes.geometry("450x335+200+200")
    #root_mes.after(70000, lambda: root_mes.destroy())
    w = Canvas(root_mes, width=450, height=300, background="#F5F5F5")
    w.pack()

    w.create_text(225, 110
                       , text='功能说明:\n'
                              '查询IN    : 生成查询语句 IN ()语句\n'
                              '美化Sql   : 格式化SQL\n'
                              'Select    : 将输入的字段生成查询语句\n'
                              'Insert    : 将输入的字段生成Insert语句\n'
                              'Create    : 将输入的字段生成建表语句\n'
                              '提取表名   : 提取sql文件中涉及的表名\n'
                              '提取依赖   : 提取sql文件中包、存储过程、表之间的依赖关系'
                              '\n'
                              '\n'
                              '注意事项 :\n'
                              '  1)、 提取表名时如果程序中实际表名和表的别名相同会被排出。\n'
                              '  2）、提取依赖关系时如果sql存在语法问题可能提取不会成功。'
                       ,font="time 11"
                       ,fill='gray'
                       )

    button1 = Button(root_mes, text = "Quit", command = root_mes.destroy,anchor = S )
    button1.configure(width = 20, activebackground = "#33B5E5", relief = FLAT)
    button1.pack(side=BOTTOM)
    #root_mes.after(70000, lambda: root_mes.destroy())
    #root_mes.withdraw()
    root_mes.after(5400, lambda: root_mes.destroy())
    root_mes.mainloop()


def copy(text):
    edit, result = text[0], text[1]
    dec = str(result.get(1.0, tk.END))
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, dec)
    win32clipboard.CloseClipboard()


if __name__ == '__main__':
    main()