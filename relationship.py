#! user/bin/python
# -*- coding:utf8 -*-

import sqlparse
import re
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import Keyword, Name


# 提取表名SQL
# 2020- 05 -18
# 定义关键字
RESULT_OPERATIONS = {"UNION", "INTERSECT", "EXCEPT", "SELECT"}
ON_KEYWORD = "ON"
PRECEDES_TABLE_NAME = {"FROM", "JOIN", "DESC", "DESCRIBE", "WITH"}
PACKAGE_PROCEDURE_NAME = {"PROCEDURE", "PACKAGE", "BODY"}


class BaseExtractor(object):
    def __init__(self, sql_statement):
        self.sql = sqlparse.format(sql_statement, reindent=True, keyword_case="upper", strip_comments=True)
        self._table_names = set()
        self._alias_names = set()
        self._limit = None
        self._parsed = sqlparse.parse(self.stripped())
        for statement in self._parsed:
            self.__extract_from_token(statement)
            self._limit = self._extract_limit_from_query(statement)
            self._extrac_special_tab(statement)
        self._table_names = self._table_names - self._alias_names

    @property
    def tables(self):
        return self._table_names

    @property
    def limit(self):
        return self._limit

    def is_select(self):
        return self._parsed[0].get_type() == "SELECT"

    def is_explain(self):
        return self.stripped().upper().startswith("EXPLAIN")

    def is_readonly(self):
        return self.is_select() or self.is_explain()

    def stripped(self):
        return self.sql.strip(";")

    def get_statements(self):
        statements = []
        for statement in self._parsed:
            if statement:
                sql = str(statement).strip(" ;	")
                if sql:
                    statements.append(sql)
        return statements

    @staticmethod
    def __precedes_table_name(token_value):
        for keyword in PRECEDES_TABLE_NAME:
            if keyword in token_value:
                return True
        return False

    @staticmethod
    def get_full_name(identifier):
        if len(identifier.tokens) > 1 and identifier.tokens[1].value == ".":
            return "{}.{}".format(identifier.tokens[0].value, identifier.tokens[2].value)
        return identifier.get_real_name()

    @staticmethod
    def __is_result_operation(keyword):
        for operation in RESULT_OPERATIONS:
            if operation in keyword.upper():
                return True
        return False

    @staticmethod
    def __is_identifier(token):
        return isinstance(token, (IdentifierList, Identifier))

    def __process_identifier(self, identifier):
        if "(" not in "{}".format(identifier):
            self._table_names.add(self.get_full_name(identifier).upper())
            return

        # store aliases
        if hasattr(identifier, "get_alias"):
            if identifier.get_alias() is None:
                None
            else:
                self._alias_names.add(identifier.get_alias())
        # some aliases are not parsed properly
        if hasattr(identifier, "tokens"):
            if identifier.tokens[0].ttype == Name:
                self._alias_names.add((identifier.tokens[0].value).upper())
        self.__extract_from_token(identifier)

    def as_create_table(self, table_name, overwrite=False):
        exec_sql = ""
        sql = self.stripped()
        if overwrite:
            exec_sql = "DROP TABLE IF EXISTS {};".format(table_name)
            exec_sql += "CREATE TABLE {} AS {}".format(table_name, sql)
        return exec_sql

    def __extract_from_token(self, token):
        if not hasattr(token, "tokens"):
            return

        table_name_preceding_token = False

        for item in token.tokens:
            if item.is_group and not self.__is_identifier(item):
                self.__extract_from_token(item)

            if item.ttype in Keyword:
                if self.__precedes_table_name(item.value.upper()):
                    table_name_preceding_token = True
                    continue

            if not table_name_preceding_token:
                continue

            if item.ttype in Keyword or item.value == ",":
                if (self.__is_result_operation(item.value)
                or item.value.upper() == ON_KEYWORD):
                    table_name_preceding_token = False
                    continue
                # FROM clause is over
                break

            if isinstance(item, Identifier):
                self.__process_identifier(item)

            if isinstance(item, IdentifierList):
                for token in item.tokens:
                    if self.__is_identifier(token):
                        self.__process_identifier(token)

    def _get_limit_from_token (self, token):
        if token.ttype == sqlparse.tokens.Literal.Number.Integer:
            return int(token.value)
        elif token.is_group:
            return int(token.get_token_at_offset(1).value)

    def _extract_limit_from_query(self, statement):
        limit_token = None
        for pos, item in enumerate(statement.tokens):
            if item.ttype in Keyword and item.value.lower() == "limit":
                limit_token = statement.tokens[pos + 2]
                return self._get_limit_from_token(limit_token)

    def get_query_with_new_limit(self, new_limit):
        if not self._limit:
            return self.sql + " LIMIT " + str(new_limit)
        limit_pos = None
        tokens = self._parsed[0].tokens
        # Add all items to before_str until there is a limit
        for pos, item in enumerate(tokens):
            if item.ttype in Keyword and item.value.lower() == "limit":
                limit_pos = pos
                break
        limit = tokens[limit_pos + 2]
        if limit.ttype == sqlparse.tokens.Literal.Number.Integer:
            tokens[limit_pos + 2].value = new_limit
        elif limit.is_group:
            tokens[limit_pos + 2].value = (
                "{}, {}".format(next(limit.get_identifiers()), new_limit)
            )

        str_res = ""
        for i in tokens:
            str_res += str(i.value)
            return str_res

    def _extrac_special_tab(self, token):
        statement_str = ''
        for tok in token.tokens:
            statement_str += tok.value

        for lin in statement_str.splitlines(True):
            if 'MERGE' in lin.upper() and 'INTO' in lin.upper():
                merge_tb_name = re.findall(r".*INTO (.*?)USING.*", lin.upper())
                split_tb_name = (str(merge_tb_name[0]).strip()).split()

                if len(split_tb_name) == 1 or '.' in split_tb_name[0]:
                    self._table_names.add((split_tb_name[0]).upper())
                else:
                    None

        tokens = re.split(r"[\s)(;]+", statement_str)
        get_next = False
        for token in tokens:
            if get_next:
                if token.lower() not in ["", "select"]:
                    self._table_names.add(token.upper())
                get_next = False
            get_next = token.lower() in ["from", "join"]



class SqlExtractor(BaseExtractor):
    """提取sql语句"""

    @staticmethod
    def get_full_name(identifier, including_dbs=False):
        if len(identifier.tokens) == 1 :
            full_name = identifier.tokens[0].value
            return full_name

        elif len(identifier.tokens) > 1 and identifier.tokens[1].value == ".":
            a = identifier.tokens[0].value
            b = identifier.tokens[2].value
            full_tree = "{}.{}".format(a, b)
            if len(identifier.tokens) == 3:
                return full_tree
            else:
                i = identifier.tokens[3].value
                c = identifier.tokens[4].value
                if i == " ":
                    return full_tree
                full_tree = "{}.{}.{}".format(a, b, c)
                return full_tree

        else:
            tb_name = identifier.tokens[0].value
            return tb_name