# Copyright (C) 2017 Baofeng Dong
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.


import csv, os

from sqlalchemy import func, desc, distinct, cast, Integer
from flask import current_app

from dashboard import Session as Session
from dashboard import debug


app = current_app


DIRPATH = os.path.dirname(os.path.realpath(__file__))


class Helper(object):

    # return total number of records for each route being surveyed
    @staticmethod
    def summary_status_query():
        # TODO add union for streetcar data
        ret_val = []
      
        # get count and target for each route
        web_session = Session()
        query = web_session.execute("""
            SELECT 
                rte,
                rte_desc,
                sum(count) AS count,
                sum(target) AS target
            FROM summary
            GROUP BY rte, rte_desc
            ORDER BY rte;""")
        
        # indexes for tuples returned by query
        RTE = 0
        RTE_DESC = 1
        COUNT = 2
        TARGET = 3

        # build data for each route
        # and add to ret_val list
        # sorted by route number
        for record in query:
            data = {}
            data['rte'] = str(record[RTE])
            data['rte_desc'] = record[RTE_DESC]
            data['count'] = float(record[COUNT])
            data['target'] = float(record[TARGET])
            ret_val.append(data)
        web_session.close()

        return ret_val

    @staticmethod
    def query_route_status(rte_desc=''):
        # set rte_desc to wildcard to query
        # if no route was specified
        ret_val = {}
      
        # query web database
        # using helper views
       
        web_session = Session()
        if rte_desc:
            query = web_session.execute("""
                SELECT s.rte,s.rte_desc,s.dir,s.dir_desc,s.time_period,
                        s.count, s.target * .1
                FROM
                odk.summary_long s
                WHERE s.rte_desc = :rte_desc
                ORDER BY s.rte, s.dir,
                    CASE s.time_period
                        WHEN 'AM Peak' THEN 1
                        WHEN 'Midday' THEN 2
                        WHEN 'PM Peak' THEN 3
                        WHEN 'Evening' THEN 4
                        WHEN 'Total' THEN 5
                    ELSE 6
                    END;""", {'rte_desc':rte_desc})
            ret_val = Helper.build_response_route_status(query)

        else:
            # query web database
            # using helper views
            query = web_session.execute("""
                SELECT s.rte,s.rte_desc,s.dir,s.dir_desc,s.time_period,
                        s.count, s.target * .1
                FROM
                odk.summary_long s
                ORDER BY s.rte, s.dir,
                    CASE s.time_period
                        WHEN 'AM Peak' THEN 1
                        WHEN 'Midday' THEN 2
                        WHEN 'PM Peak' THEN 3
                        WHEN 'Evening' THEN 4
                        WHEN 'Total' THEN 5
                    ELSE 6
                    END;""")
            ret_val = Helper.build_response_summary_status(query)
        web_session.close()
        debug(ret_val)
        return ret_val

    @staticmethod
    def query_routes_summary():
        ret_val = {}
      
        # query web database
        # using helper views
       
        web_session = Session()
        query = web_session.execute("""
            SELECT s.rte, s.rte_desc, sum(s.count) AS count,sum(s.target)*0.1
            FROM odk.summary_long s
            GROUP BY s.rte,s.rte_desc
            ORDER BY s.rte;""")

        for record in query:
            rte_desc = record[1]
            count = int(record[2])
            target = int(record[3])
            ret_val[rte_desc] = {"count":count, "target":target}
        debug(ret_val)

        return ret_val

    @staticmethod
    def build_response_summary_status(query):
        ret_val = {}
        
        for record in query:
            if not record[0]: continue
            rte = int(record[0])
            rte_desc = record[1]
            dir = int(record[2])
            dir_desc = record[3]
            time = record[4]
            count = int(record[5])
            target = int(record[6])

            data = {}
            data['target'] = target
            data['count'] = count

            if rte_desc not in ret_val:
                ret_val[rte_desc] = {}

            # set up each time period of this direction
            # populate later when that record is fetched
            if str(dir) not in ret_val[rte_desc]:
                ret_val[rte_desc][str(dir)] = Helper.build_shell(dir_desc)
   
            if target == 0:
                data = {}

            ret_val[rte_desc][str(dir)][time] = data
            debug(ret_val)
        return ret_val

    @staticmethod
    def build_response_route_status(query):
        ret_val = {}

        # look through query results
        # and build response
        for record in query:
            rte = int(record[0])
            rte_desc = record[1]
            dir = int(record[2])
            dir_desc = record[3]
            time = record[4]
            count = int(record[5])
            target = int(record[6])
            
            data = {}
            data['target'] = target
            data['count'] = count

            # add route description
            # only executes in first loop
            if 'rte_desc' not in ret_val:
                ret_val['rte_desc'] = rte_desc
            
            # build dictionary for each time period
            if str(dir) not in ret_val:
                ret_val[str(dir)] = Helper.build_shell(dir_desc)
            
            # set target and count data into correct
            # direction and time period
            if target == 0:
                data = {}
            
            ret_val[str(dir)][time] = data
        
        return ret_val

    @staticmethod
    def build_shell(dir_desc):
        ret_val = {}
        ret_val['dir_desc'] = dir_desc
        ret_val['AM Peak'] = {}
        ret_val['Midday'] = {}
        ret_val['PM Peak'] = {}
        ret_val['Evening'] = {}
        return ret_val

    @staticmethod
    def get_routes():
        ret_val = []
        
        web_session = Session()
        routes = web_session.execute("""
            SELECT rte, rte_desc
            FROM orange_route_direction
            ORDER BY route_sort_order;""")

        RTE = 0
        RTE_DESC = 1
        ret_val = [ {'rte':str(route[RTE]), 'rte_desc':route[RTE_DESC]}
            for route in routes ]
        web_session.close()
        
        return ret_val

    @staticmethod
    def get_directions():
        ret_val = []
        web_session = Session()
        directions = web_session.execute("""
            SELECT rte, rte_desc, dir, dir_desc
            FROM lookup_dir
            ORDER BY rte, dir;""")

        RTE = 0
        RTE_DESC = 1
        DIR = 2
        DIR_DESC = 3

        ret_val = [ {'rte':str(direction[RTE]), 'rte_desc':direction[RTE_DESC],
            'dir':int(direction[DIR]), 'dir_desc':direction[DIR_DESC]}
            for direction in directions ]
        web_session.close()
        return ret_val




    @staticmethod
    def query_route_data(user='', rte_desc='', dir_desc='', csv=False):
        ret_val = []
        query_args = {}
        where = ""

        if user: user = "%" + user + "%"
        user_filter = " first_name LIKE :user "
        rte_desc_filter = " rte_desc = :rte_desc "
        dir_desc_filter = " dir_desc = :dir_desc "
        
        def construct_where(string, param, filt_name):
            if not param:
                return string

            if filt_name == "user": filt = user_filter
            elif filt_name == "rte_desc": filt = rte_desc_filter
            else: filt = dir_desc_filter

            if string:
                return string + " AND " + filt
            else:
                return string + filt
      
        # build where clause
        debug(where)
        for param in [(user, 'user'),(rte_desc, 'rte_desc'),(dir_desc, 'dir_desc')]:
            where = construct_where(where, param[0], param[1])
            debug(where)
            query_args[param[1]] = param[0]
        if where:
            where = " WHERE " + where
        
        limit = "LIMIT 300;"
        if csv:
            # add headers to csv data
            ret_val.append(
                ['date','time','user','rte_desc','dir_desc','on_stop', 'off_stop', 'hop'])
            
            limit = ";"

        query_string = """
            SELECT rte_desc, dir_desc, date, time, first_name,
                on_stop, off_stop, hop
            FROM odk.long_display_data """

        query_string += where 
        query_string += " ORDER BY date DESC, time DESC "
        query_string += limit

        debug(query_string)

        web_session = Session()
        query = web_session.execute(query_string, query_args)
        # convert query object to list
        result = [r for r in query]

        RTE_DESC = 0
        DIR_DESC = 1
        DATE = 2
        TIME = 3
        USER = 4
        ON_STOP = 5
        OFF_STOP = 6
        HOP = 7

        # each record will be converted as json
        # and sent back to page
        for record in result:
            if csv:
                data = []
                data.append(str(record[DATE]))
                data.append(str(record[TIME]))
                data.append(record[USER])
                data.append(record[RTE_DESC])
                data.append(record[DIR_DESC])
                data.append(record[ON_STOP])
                data.append(record[OFF_STOP])
                data.append(record[HOP])
            else:
                data = {}
                data['date'] = str(record[DATE])
                data['time'] = str(record[TIME])
                data['user'] = record[USER]
                data['rte_desc'] = record[RTE_DESC]
                data['dir_desc'] = record[DIR_DESC]
                data['on_stop'] = record[ON_STOP]
                data['off_stop'] = record[OFF_STOP]
                data['hop'] = record[HOP]
            ret_val.append(data)

        web_session.close()
        return ret_val

    @staticmethod
    def current_users(date):
        ret_val = {}
        
        web_session = Session()
        results = web_session.execute("""
            SELECT u.rte_desc, u.time_period, u.user_id, u.rte
            FROM
            (SELECT * from users_tod_ts
            UNION
            SELECT * from users_tod) u
            WHERE u.date = :date
            ORDER BY
                    CASE u.time_period
                        WHEN 'AM Peak' THEN 1
                            WHEN 'Midday' THEN 2
                            WHEN 'PM Peak' THEN 3
                            WHEN 'Evening' THEN 4
                            WHEN 'Total' THEN 5
                        ELSE 6
                    END, u.rte;""",{'date':date})

            
        for result in results:
            
            rte_desc = result[0]
            time_period = result[1]
            
            user = ", ".join(
                sorted(list(set([user.strip() for user in result[2].split(",")]))))
            
            #list1 = result[2].split(",")
            #list2 = set(list1)
            #list3 = ", ".join(list2)
            #debug(list1)
            #debug(list2)
            #debug(list3)
            #user = ", ".join(list(set(result[2].split(","))))
            #debug(user)
            if time_period not in ret_val:
                ret_val[time_period] = []
            
            data = {'rte_desc':rte_desc, 'user':user}
            ret_val[time_period].append(data)
        web_session.close() 
        debug(ret_val)
        return ret_val

    @staticmethod
    def get_users():
        users = []
        web_session = Session()
        results = web_session.execute("""
            SELECT first
            FROM users
            WHERE first IS NOT NULL
            ORDER BY first;""")


        for result in results:
            #print((dict(result)))
            #print("Type:", type(dict(result)))
            user_dict = dict(result)
            #print(user_dict)
            user = user_dict.get('first')
            users.append(str(user))

        web_session.close()
        return users






