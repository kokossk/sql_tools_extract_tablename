#!/bin/python
# _*_ coding:utf8 _*_

import os
import re
import sqlparse

path = os.path.dirname(os.path.abspath(__file__))
config_path = path + '/config'
print(config_path)


class Input_file(object):

    def __init__(self, str):
        self.str = str
        self._package_name = set()
        self._procedure_name = set()

    def replace_whitespace_with_space(self):
        str1 = self.str
        news_lis = []
        whitespace1 = '\n\n'
        whitespace2 = '\t'
        str2 = str1.replace(whitespace1,'')
        str3 = str2.replace(whitespace2, '')
        str4 = str3.split()
        str5 = list(str4)

        for str6 in str5:
           pass
           if str6 not in news_lis:
               pass
               news_lis.append(str6)

        return news_lis

    def mp_sql_beautiful(self):
        s_list = []
        keyword1 = r'SELECT'
        keyword2 = r';'
        # sql 美化
        str2 = sqlparse.format(self.str, reindent=True, keyword_case='upper')
        str3 = str2.splitlines()
        str4 = list(filter(None, str3))

        for line in str4:
            if line.find(keyword1) >= 0:
                str5 = line.replace(keyword1, 'SELECT \n')
                str6 = str5.split('\n')
                s_list.extend(str6)
            elif line.find(keyword2) >=0:
                str7 = line.replace(keyword2, '\n ;')
                str8 = str7.split('\n')
                s_list.extend(str8)
            else:
                s_list.append(line)
        return s_list

    def cx_select(self):
        max_len = 0
        value1 = ['FROM', 'TABLE_NAME', ';']
        value2 = 'SELECT'
        str1 = self.str
        news_lis = []
        news_lis1 = []
        news_lis2 = []
        whitespace1 = '\n\n'
        whitespace2 = '\t'
        str2 = str1.replace(whitespace1,'')
        str3 = str2.replace(whitespace2, '')
        st_up = str3.upper()
        str4 = st_up.split()
        str5 = list(str4)

        # 去重
        for str6 in str5:
           if str6 not in news_lis1:
               news_lis1.append(str6)

        # 求最长字段
        for str7 in news_lis1:
            str8 = len(str7)
            if str8 > max_len:
                str8, max_len = max_len, str8
            else:
                pass
        if max_len < 1:
            pass
        else:
            # 补齐
            len1 = len(news_lis1)
            for i in range(len1):
                if i == 0:
                    str9 = ' ' + news_lis1[i].ljust(max_len)+'    AS '+news_lis1[i]
                else:
                    str9 = ','+news_lis1[i].ljust(max_len)+'    AS '+news_lis1[i]
                news_lis2.append(str9)

            news_lis.extend(news_lis2)
            news_lis.extend(value1)
            news_lis.insert(0, value2)

        return news_lis

    def insert_sql(self):
        value1 = ['INSERT INTO ', 'TABLE_NAME', '(']
        value2 = [')']
        str1 = self.str
        news_lis1 = []
        news_lis2 = []
        news_lis = []
        whitespace1 = '\n\n'
        whitespace2 = '\t'
        str2 = str1.replace(whitespace1,'')
        str3 = str2.replace(whitespace2, '')
        st_up = str3.upper()
        str4 = st_up.split()
        str5 = list(str4)

        # 去重
        for str6 in str5:
           if str6 not in news_lis1:
               news_lis1.append(str6)

        max_len = len(news_lis1)
        # print(max_len)
        # print('---')

        for i in range(max_len):
            # print(i)
            # print(news_lis1[i])
            if i == max_len - 1:
                str7 = news_lis1[i]
            else:
                str7 = news_lis1[i]+','
            news_lis2.append(str7)

        if max_len >= 1:
            news_lis.extend(value1)
            news_lis.extend(news_lis2)
            news_lis.extend(value2)
        else:
            pass
        return news_lis

    def create_tab_sql(self):
        value1 = ['CREATE TABLE ', 'TABLE_NAME', '(']
        value2 = [')', ';']
        value3 = ' STRING DEFAULT NULL COMMENT '' '
        str1 = self.str
        news_lis1 = []
        news_lis2 = []
        news_lis = []
        whitespace1 = '\n\n'
        whitespace2 = '\t'
        str2 = str1.replace(whitespace1,'')
        str3 = str2.replace(whitespace2, '')
        st_up = str3.upper()
        str4 = st_up.split()
        str5 = list(str4)

        # 去重
        for str6 in str5:
           if str6 not in news_lis1:
               news_lis1.append(str6)

        lis_len = len(news_lis1)
        max_len = 0

        # 求最长字段
        for str7 in news_lis1:
            str8 = len(str7)
            if str8 > max_len:
                str8, max_len = max_len, str8
            else:
                pass

        for i in range(lis_len):
            if i == lis_len - 1:
                str7 = news_lis1[i].ljust(max_len) + value3 + "''"
            else:
                str7 = news_lis1[i].ljust(max_len) + value3 + "''" + ','
            news_lis2.append(str7)

        if max_len >= 1:
            news_lis.extend(value1)
            news_lis.extend(news_lis2)
            news_lis.extend(value2)
        else:
            pass
        return news_lis

    def proc_relationship(self):
        package_procedure_name = {"PROCEDURE", "PACKAGE", "BODY"}
        str_sql = self.str
        sql = sqlparse.format(str_sql, reindent=True, keyword_case="upper", strip_comments=True)
        parsed = sqlparse.parse(sql)
        for statement in parsed:
            statement_str = ''
            for tok in statement.tokens:
                statement_str += tok.value
            for keyword in package_procedure_name:
                if keyword in statement_str:
                    _pack_name1 = re.findall(r".*BODY(.*?)IS.*", statement_str)
                    # pack_name2 = re.findall(r".*PACKAGE(.*?)[(]", statement_str)
                    _proc_name = re.findall(r".*PROCEDURE(.*?)[(]", statement_str)
                    if len(_pack_name1) == 1:
                        self._package_name.add((_pack_name1[0]).upper())
                    elif len(_pack_name1) > 1:
                        print(_pack_name1)

                    if len(_proc_name) == 1:
                        self._procedure_name.add((_proc_name[0]).upper())
                    elif len(_proc_name) > 1:
                        print(_proc_name)

    @property
    def package_name(self):
        return self._package_name

    @property
    def procedure_name(self):
        return self._procedure_name





