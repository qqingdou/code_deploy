# /usr/bin/python
# -*- coding:utf-8 -*-

import MySQLdb
import git_web_hooks.settings

class MySQL:

    table = None
    _cursor = None
    _conn = None
    '''
    初始化
    '''
    def __init__(self, config=None):
        if config is None:
            config = git_web_hooks.settings.DATABASES['default']

        if self._conn is None:

            self._conn = MySQLdb.connect(host=config['HOST'],
                                         user=config['USER'],
                                         passwd=config['PASSWORD'],
                                         port=int(config['PORT']),
                                         db=config['NAME'],
                                         charset='utf8')
            self._cursor = self._conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def fetch_one(self, fields='*', condition=None):
        """
        获取单条记录
        :param fields:
        :param condition:
        :return:
        """
        result = self.fetch_all(fields, condition, order=None, limit='1')
        if not result or result is None:
            return None
        return result[0]

    def fetch_all(self, fields='*', condition=None, order=None, limit=None, group=None):
        """
        获取列表
        :param fields:
        :param condition:
        :param order:
        :param limit:
        :param group:
        :return:
        """
        params = ()
        where = group_str = order_str = limit_str = ''
        condition_format, condition_val = self._parse_sql(condition)
        if condition_val is not None:
            params += condition_val
        if condition_format is not None:
            where = ' '.join(('WHERE', condition_format))
        if order is not None:
            order_str = ' '.join(('ORDER BY', order))
        if limit is not None:
            limit_str = ' '.join(('LIMIT', limit))
        if group is not None:
            group_str = ' GROUP BY '.join(group)
        sql = ' '.join(('SELECT', fields, 'FROM', self.table, where, group_str, order_str, limit_str))
        self._cursor.execute(sql, params)
        results = self._cursor.fetchall()
        return results

    def add(self, data):
        """
        插入数据
        :param data:
        :return:
        """
        sql = ''
        params = None
        if isinstance(data, dict):
            params = tuple(data.values())
            dict_keys = data.keys()
            sql = ''.join(('INSERT INTO ', self.table, '(`', '`,`'.join(dict_keys), '`)', 'VALUES', '(', ','.join(['%s' for x in range(len(dict_keys))]), ')'))
        elif isinstance(data, str):
            sql = data
        else:
            return None

        result = None

        try:
            result = self._cursor.execute(sql, params)
            self._conn.commit()
        except:
            self._conn.rollback()
        finally:
            return result

    def save(self, condition, data):
        """
        保存
        :param condition:
        :param data:
        :return:
        """
        data_format, data_value = self._parse_sql(data)
        condition_format, condition_value = self._parse_sql(condition)
        sql = ''.join(('UPDATE ', self.table, ' SET ', data_format, ' WHERE ', condition_format))
        params = None
        if data_value is not None:
            params = data_value
        if condition_value is not None:
            if data_value is not None:
                params = params + condition_value
            else:
                params = condition_value

        result = None

        try:
            result = self._cursor.execute(sql, params)
            self._conn.commit()
        except:
            self._conn.rollback()
        finally:
            return result
    '''
    析构
    '''
    def __delete__(self, instance):
        self.close()
    '''
    关闭
    '''
    def close(self):
        self._cursor.close()
        self._conn.close()
        self._cursor = None
        self._conn = None
    '''
    分析SQL语句
    '''
    def _parse_sql(self, condition):
        if isinstance(condition, str):
            return condition, None
        elif isinstance(condition, dict):
            where_list = []
            for key in condition:
                where_list.append(''.join(('`', key, '`', '=%s')))
            return ','.join(where_list), tuple(condition.values())
        else:
            return None, None



