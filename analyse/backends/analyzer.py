#_*_coding:utf-8_*_
__author__ = 'Alex Li'

'''
对收集的数据进行实时分析
'''
import time,json,functools
from  TengLan import settings
from  analyse import models
from analyse.backends import ip_lookup
class Analyzer(object):
    def __init__(self,redis_obj):
        self.redis_obj = redis_obj
        self.time_range = 900 #数据 分析时间范围
        self.report_items = settings.REPORT_ITEMS
        self.ip_data_db = ip_lookup.IPLookup(ip_db_filename=settings.IP_DB_FILE).ip_db_data
    def start(self):
        '''
        不间断的运行
        :return:
        '''
        self.exit_flag = False

        while not self.exit_flag:
            site_objs = models.Site.objects.all()
            for site in site_objs:
                self.get_country_angle_data(site)
                self.get_region_ranking(site)
                time.sleep(60)
    def get_region_ranking(self,site):
        '''
        找出速度最快和最慢的20个访问地区
        :param site:
        :return:
        '''
        city_dic = {}
        province_objs = models.Region.objects.filter(region_type='city')
        for city in province_objs:
            city_dic[city.id] = {'name':city.name,'id':city.id,'indexs':{}}
            for index in self.report_items:
                city_dic[city.id]['indexs'][index] = {"data":[],
                                                        "avg":None,
                                                        "max":None,
                                                        "min":None,
                                                        "tp99":None,
                                                        "mid":None}

        for index in self.report_items:
            time_counter = self.time_range
            time_range_data = [] #把最近5分钟的数据汇集起来
            while time_counter >0:
                time_obj = time.localtime(time.time()-time_counter)
                redis_key = "%s__%s__%s%s" %(site.id,index,time_obj.tm_hour,time_obj.tm_min)
                print(redis_key)
                time_counter -=60

                data = self.redis_obj.lrange(redis_key,0,-1)
                #print('--data>',redis_key,data)
                #[max,min,avg,mid,tp90] 求这几个值
                each_minute_data =[json.loads(data_point.decode())  for data_point in data ]
                each_minute_data = list(filter(lambda x:x[0]>0,each_minute_data) if each_minute_data else each_minute_data ) #filter out the nagative data
                time_range_data.extend(each_minute_data)
                print("each min data:",each_minute_data)
            #else:
            #    print()
            print('\033[42;1mtime range data:%s\033[0m'%time_range_data)
            self.dispatch_by_city(time_range_data,city_dic,index) #把这些数据按地区维度进行分类清洗

        #开始做最终的聚合运算
        for k in city_dic:
            #print(k,country_dic[k])
            for index,v in city_dic[k]['indexs'].items():
                print("cacl index-->",index)
                avg_res = self._get_avg(v['data'])
                mid_res = self._get_mid(v['data'])
                min_res = self._get_min(v['data'])
                max_res = self._get_max(v['data'])
                tp99_res = self._get_tp90(v['data'])
                city_dic[k]['indexs'][index]['avg']=avg_res
                city_dic[k]['indexs'][index]['mid']=mid_res
                city_dic[k]['indexs'][index]['min']=min_res
                city_dic[k]['indexs'][index]['max']=max_res
                city_dic[k]['indexs'][index]['tp99']=tp99_res
                if avg_res:
                    print(city_dic[k]['name'])
                    print("index val:",city_dic[k]['indexs'][index])
        #写入redis
        #写入redis前确保数据符合前端画图的数据格式
        city_data = []
        data_point_count = 0
        for k,v in city_dic.items():

            v['value'] =  v['indexs']['requestTime']['avg']
            v['data_count'] =  len(v['indexs']['requestTime']['data'])
            data_point_count += v['data_count']
            if v['value'] : #没值 就不要放了
                city_data.append(v)
        #print(city_data)
        city_data = sorted(city_data,key=lambda x:x['value'])

        city_rank_dic= {'fastest':{'names':[],'values':[]},
                        'slowest':{'names':[],'values':[]},
                        }
        for index,data_point  in enumerate(city_data):
            if index <20:
                fast_order_item = city_data[index]
                city_rank_dic['fastest']['names'].append(fast_order_item['name'])
                city_rank_dic['fastest']['values'].append(fast_order_item['value'])

                if index ==0:  #最慢地区取值 不能是-0呀
                    continue
                slow_order_item = city_data[-index]

                city_rank_dic['slowest']['names'].append(slow_order_item['name'])
                city_rank_dic['slowest']['values'].append(slow_order_item['value'])



        redis_key = "site__%s__latest_region_ranking" %site.id
        self.redis_obj.set(redis_key, json.dumps([city_rank_dic,time.time()]) )

    def get_country_angle_data(self,site):
        '''
        从全国各省的角度来分析
        :return:
        '''
        print(self.report_items)
        country_dic = {}
        province_objs = models.Region.objects.filter(region_type='province')
        for pro in province_objs:
            country_dic[pro.id] = {'name':pro.name,'id':pro.id,'indexs':{}}
            for index in self.report_items:
                country_dic[pro.id]['indexs'][index] = {"data":[],
                                                        "avg":None,
                                                        "max":None,
                                                        "min":None,
                                                        "tp99":None,
                                                        "mid":None}

        for index in self.report_items:
            time_counter = self.time_range
            time_range_data = [] #把最近5分钟的数据汇集起来
            while time_counter >0:
                time_obj = time.localtime(time.time()-time_counter)
                redis_key = "%s__%s__%s%s" %(site.id,index,time_obj.tm_hour,time_obj.tm_min)
                print(redis_key)
                time_counter -=60

                data = self.redis_obj.lrange(redis_key,0,-1)
                #print('--data>',redis_key,data)
                #[max,min,avg,mid,tp90] 求这几个值
                each_minute_data =[json.loads(data_point.decode())  for data_point in data ]
                each_minute_data = list(filter(lambda x:x[0]>0,each_minute_data) if each_minute_data else each_minute_data ) #filter out the nagative data
                time_range_data.extend(each_minute_data)
                print("each min data:",each_minute_data)
            print('\033[42;1mtime range data:%s\033[0m'%time_range_data)
            self.dispatch_by_province(time_range_data,country_dic,index) #把这些数据按省维度进行分类清洗
        #开始做最终的聚合运算
        for k in country_dic:
            #print(k,country_dic[k])
            for index,v in country_dic[k]['indexs'].items():
                print("cacl index-->",index)
                avg_res = self._get_avg(v['data'])
                mid_res = self._get_mid(v['data'])
                min_res = self._get_min(v['data'])
                max_res = self._get_max(v['data'])
                tp99_res = self._get_tp90(v['data'])
                country_dic[k]['indexs'][index]['avg']=avg_res
                country_dic[k]['indexs'][index]['mid']=mid_res
                country_dic[k]['indexs'][index]['min']=min_res
                country_dic[k]['indexs'][index]['max']=max_res
                country_dic[k]['indexs'][index]['tp99']=tp99_res
                if avg_res:
                    print(country_dic[k]['name'])
                    print("index val:",country_dic[k]['indexs'][index])
        #写入redis
        #写入redis前确保数据符合前端画图的数据格式
        country_data = []
        data_point_count = 0
        for k,v in country_dic.items():
            v['value'] =  v['indexs']['requestTime']['avg']
            v['data_count'] =  len(v['indexs']['requestTime']['data'])
            data_point_count += v['data_count']
            country_data.append(v)
        redis_key = "site__%s__latest_country_map_view" % site.id
        self.redis_obj.set(redis_key, json.dumps([country_data,data_point_count,time.time()]) )

    def dispatch_by_city(self,time_range_data,city_dic,index): #把这些数据按地区维度进行分类清洗
        '''
        把time_range_data中的数据依次取出来,放到每个city中
        :param time_range_data: [[4, 1465715088.137754, u'127.0.0.1'], [5, 1465715202.913715, u'127.0.0.1']]
        :param city_dic:
        :param index:
        :return:
        '''
        for data_point in time_range_data:
            value,timestamp,ip_addr = data_point
            ip_lookup_obj = ip_lookup.IPLookup(ip_db_data=self.ip_data_db)
            lookup_res = ip_lookup_obj.lookpup(ip_addr)
            if lookup_res:
                print(lookup_res)
                #print("%s :%s %s %s" %(ip_addr,lookup_res['province'],lookup_res['city'],lookup_res['district'] ))
                for k,v in city_dic.items():
                    #print(v['name'],type(v['name']),lookup_res['province'],type(lookup_res['province']))
                    if v['name'].startswith(lookup_res['city']):
                        print("match:",v,v['name'])
                        city_dic[k]['indexs'][index]['data'].append(data_point)
                        print("city dic data:",city_dic[k]['indexs'][index]['data'])
                        break
                else:
                    print("\033[31;1m没找到匹配的地区\033[0m")
    def dispatch_by_province(self,time_range_data,country_dic,index):
        '''
        把time_range_data中的数据依次取出来,放到每个province中
        :param time_range_data: :[[4, 1465715088.137754, u'127.0.0.1'], [5, 1465715202.913715, u'127.0.0.1']]
        :param country_dic:
        :param index: like "redirectTime" ...
        :return:
        '''

        for data_point in time_range_data:
            value,timestamp,ip_addr = data_point
            ip_lookup_obj = ip_lookup.IPLookup(ip_db_data=self.ip_data_db)
            lookup_res = ip_lookup_obj.lookpup(ip_addr)
            if lookup_res:
                print(lookup_res)
                #print("%s :%s %s %s" %(ip_addr,lookup_res['province'],lookup_res['city'],lookup_res['district'] ))
                for k,v in country_dic.items():
                    #print(v['name'],type(v['name']),lookup_res['province'],type(lookup_res['province']))
                    if v['name'].startswith(lookup_res['province']):
                        print("match:",v,v['name'])
                        data_point.append(lookup_res) #把解析结果也返回给前台
                        country_dic[k]['indexs'][index]['data'].append(data_point)
                        print("country dic data:",country_dic[k]['indexs'][index]['data'])
                        break
                else:
                    print("\033[31;1m没找到匹配的省\033[0m")
    def _get_max(self,data_set):
        data_set = list(map(lambda x:x[0],data_set))
        print("max:",data_set)
        if data_set:
            return max(data_set)
    def _get_min(self,data_set):
        data_set = list(map(lambda x:x[0],data_set))
        if data_set:
            return min(data_set)
    def _get_avg(self,data_set):
        print("calc agv:",data_set)
        if data_set:
            #print('avg--:',type(data_set))
            print("\033[41;1mdataset:\033[0m",data_set)
            sum_res = sum(list(map(lambda x:x[0],data_set)))
            print("sum res:",sum_res)
            return (sum_res / len(data_set))*5 #这个5在这只是为了测试哈,因为本机速度太快了
        #return  random.randrange(50)
    def _get_mid(self,data_set):
        data_set = list(map(lambda x:x[0],data_set))
        data_set.sort()
        if data_set:
            return data_set[int(len(data_set)/2)]
    def _get_tp90(self,data_set):
        data_set = list(map(lambda x:x[0],data_set))
        if len(data_set) > 10:
            data_set.sort()
            return  data_set[int(len(data_set)*0.9)]

