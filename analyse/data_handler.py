#_*_coding:utf-8_*_
__author__ = 'Alex Li'
import json,time,random
from analyse import models
from django.core.exceptions import ObjectDoesNotExist
from TengLan import settings
from  analyse.backends import ip_lookup


class DataProcess(object):
    '''
    负责把用户发来的统计数据进行验证\分析\清洗并存储
    '''
    __collection_items = ('firstPaint','domReadyTime','lookupDomainTime',
                          'requestTime','loadTime','redirectTime',
                          )
    def __init__(self,request,redis_obj,region_realtime_watching_q,ip_db_data):
        self.request = request
        self.redis = redis_obj
        self.region_realtime_watching_q = region_realtime_watching_q
        self.ip_db_data = ip_db_data


    def is_valid(self):
        '''
        检测数据是否合法
        :return:
        '''

        try:
            data = json.loads(self.request.GET.get('data'))
        except Exception as e:
            print("error:",e)
            return
        print("-->data",data)
        if data.get('times') and  data.get('resources_load_time') and data.get('site_id'):
            for key in data.get('times'):
                print(key,data['times'][key])
            print('resource load time'.center(40,'-'))
            for k,v in data.get('resources_load_time').items():
                print(k,v)

            #测试请求navigator类型
            navigator_type =  data['times']['navigationType']
            #if navigator_type != 0: #只有等于0时才是新请求,等于1是reload,2是回退
            if navigator_type != 0: #只有等于0时才是新请求,等于1是reload,2是回退
                print("not a new request", navigator_type)
                return False

            #确保必要的参数都 存在
            for key in self.__collection_items:
                if  data['times'].get(key) is None:
                    print("lack of mandatory arg of [%s]" % key )
                    return False
            #确保站点名在数据库里已经配置
            try:
                site_obj = models.Site.objects.get(id=data.get('site_id'))
                print('site:',site_obj)
                if site_obj.enabled !=True:
                    return False #站点监测未启用
                self.site_obj = site_obj
            except ObjectDoesNotExist as e:
                print("无此站点",e)
                return False
            self.data = data
            return True
    def save(self):
        '''
        把数据保存到redis里
        :return:
        '''
        self.process()

        #如果 some region openning the realtime watching , should dispatch all this region's report to that queue

        self.dispatch_realtime_region_watching()

    def dispatch_realtime_region_watching(self):
        '''
        先检测有没有区域开启了实时监测,如果有,就对所有汇报过来的数据进行分析 ,把属于指定区域的数据放到相应的queue
        :return:
        '''
        if self.region_realtime_watching_q:#如果不为空就代表 有用户开启了实时监控
            client_ip = '123.133.157.27' #得到测试ip
            ip_lookup_obj = ip_lookup.IPLookup(ip_db_data=self.ip_db_data)
            lookup_res = ip_lookup_obj.lookpup(client_ip)
            if lookup_res:
                print('ip res:',lookup_res)
                province_objs = models.Region.objects.filter(name__startswith=lookup_res.get('province'))
                city_objs = models.Region.objects.filter(name__startswith=lookup_res.get('city'))

                if province_objs and city_objs:
                    q_key = 'queue_%s_%s_%s' %(self.site_obj.id,province_objs[0].id,city_objs[0].id)

                    if q_key in self.region_realtime_watching_q:#这个地区开启了实时分析 监测
                        print("region[%s][%s] has opened realtime watching....:" %(province_objs[0].name,city_objs[0].name))
                        self.region_realtime_watching_q[q_key].put([self.data,client_ip])
    def process(self):
        '''
        把数据提取出来
        :return:
        '''
        #redis_key_format = "www.baidu.com__first_paint__1822" 18:22分
        #print("client ip:",self.get_client_ip(self.request) )
        #client_ip = self.get_client_ip(self.request)
        #client_ip = self.get_client_ip_test(self.request) #得到测试ip
        client_ip = '123.133.157.27' #得到测试ip
        print("测试client ip:",client_ip)
        c_time = time.localtime()
        for key in self.__collection_items:
            redis_key = "%s__%s__%s%s" %(self.site_obj.id,key,c_time.tm_hour,c_time.tm_min)
            print(redis_key)
            val = self.data['times'][key]
            self.redis.rpush(redis_key, json.dumps([val,time.time(),client_ip]) )
            self.redis.expire(redis_key,60*60)


        #save resource load times
        #format = www.baidu.com__resources_custom.css__1105
        for k,v in self.data.get('resources_load_time').items():
            print(k,v)
            key = k.split("/")[-1]
            redis_key = "%s__resources__%s__%s%s" %(self.site_obj.id,key,c_time.tm_hour,c_time.tm_min)
            print(redis_key)
            self.redis.rpush(redis_key,json.dumps([v,time.time(),client_ip]))
            self.redis.expire(redis_key,60*60)

    def get_client_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_client_ip_test(self,request):
        '''
        为了测试不同地区的访问而生成 的测试ip
        :param request:
        :return:
        '''
        db_file = "%s/analyse/backends/src/ipdb-20140902-99884.txt" %settings.BASE_DIR
        with open(db_file) as f:
            random_line = random.randrange(50000)
            line_count = 0
            for line in f:
                line_count +=1
                if line_count == random_line:
                    random_ip = line.split('|')[0]
                    return random_ip
class LatestStatisticData(object):
    __collection_items = ('firstPaint','domReadyTime','lookupDomainTime',
                          'requestTime','loadTime','redirectTime',
                          )
    def __init__(self,site_id,redis_obj):
        self.site_id = site_id
        self.redis = redis_obj

        self.data = {
            'country_map':[],
            'fastest_regions':[],
            'slowest_regions':[],
            'load_time_range':[],
            'load_resources':[],
            'latest_60mins_trends':None

        }
    def get_latest_data(self):
        self.get_latest_60mins_trends()

        return self.data
    def get_latest_60mins_trends(self):
        tmp_data = {} #把数据从redis里先取出来,放在这个dict里
        #c_time = time.localtime(time.time()-3600)
        for key in self.__collection_items:
            tmp_data[key] = []
            #每个指标都要取出最近61分钟的数据
            time_counter = 3600

            while time_counter >0:
                time_stamp = time.time()-time_counter
                time_ticker = time.localtime(time_stamp)
                redis_key = "%s__%s__%s%s" %(self.site_id,key,time_ticker.tm_hour,time_ticker.tm_min)
                data = self.redis.lrange(redis_key,0,-1)
                print('--data>',redis_key,data)
                #[max,min,avg,mid,tp90] 求这几个值
                each_minute_data =[json.loads(data_point.decode())[0]  for data_point in data ]
                each_minute_data = list(filter(lambda x:x>0,each_minute_data) if each_minute_data else each_minute_data ) #filter out the nagative data
                #for data_point in data:
                #    print("----each min:",data_point,type(data_point))
                #    json.loads(data_point)
                #print("each min data:",each_minute_data)
                #each_minute_data =[json.loads(data_point)[0] for data_point in data]
                #for point in each_minute_data:
                tmp_data[key].append([self._get_max(each_minute_data),
                                      self._get_avg(each_minute_data),
                                      self._get_min(each_minute_data),
                                      self._get_mid(each_minute_data),
                                      self._get_tp90(each_minute_data),
                                      time_stamp
                                      ])
                time_counter -= 60
                #print(key,tmp_data[key])
            else:
                print(data)
        self.data['latest_60mins_trends'] = tmp_data
    def _get_max(self,data_set):
        print("max:",data_set)
        if data_set:
            return max(data_set)
    def _get_min(self,data_set):
        if data_set:
            return min(data_set)
    def _get_avg(self,data_set):
        if data_set:
            #print('avg--:',type(data_set))
            print("\033[41;1mdataset:\033[0m",data_set)
            return (sum(data_set) / len(data_set))*5
        #return  random.randrange(50)
    def _get_mid(self,data_set):
        data_set.sort()
        if data_set:
            return data_set[int(len(data_set)/2)]
    def _get_tp90(self,data_set):
        if len(data_set) > 10:
            data_set.sort()
            return  data_set[int(len(data_set)*0.9)]


class RegionDataHandler(object):
    '''
    把指定的地区指定时间的数据取出\处理\返回
    '''
    def __init__(self,request,redis_obj,ip_db_data):
        self.request = request
        self.redis = redis_obj
        self.errors = {}
        self.ip_db_data = ip_db_data
    def validate_args(self):
        time_range = self.request.GET.get('time_range')
        province_id = self.request.GET.get('province_id')
        city_id = self.request.GET.get('city_id')
        site_id = self.request.GET.get('site_id')
        if site_id and time_range and province_id and city_id:
            self.time_range = time_range
            self.province_id = province_id
            self.site_id = site_id
            self.city_id = city_id
            return True
        else:
            self.errors['msg'] = "lack of request arguments,please check"

    def get_data(self):

        '''__collection_items = ('firstPaint','domReadyTime','lookupDomainTime',
                           'requestTime','loadTime','redirectTime',
                          )'''

        index = 'requestTime' #取什么指标的趋势数据,这个应该是用户最关注的
        index_data = [] #把每分钟来自己于指定区域的数据提取出来,放这里
        time_counter = int(self.time_range) * 60

        while time_counter >0:
            timestamp = time.time()-time_counter
            c_time = time.localtime(timestamp)
            index_redis_key = "%s__%s__%s%s" %(self.site_id,index,c_time.tm_hour,c_time.tm_min)
            raw_data_set = self.redis.lrange(index_redis_key,0,-1)
            #print(index_redis_key,data_set)
            time_counter -=60
            data = [json.loads(data_point.decode())  for data_point in raw_data_set]
            print(index_redis_key,data)
            each_min_data = self.fetch_region_data(data,timestamp)
            index_data.append(each_min_data)
        return index_data
    def fetch_region_data(self,data_set,data_set_timestamp):
        '''
        把data_set里的值每个都遍历一次,对每个值的汇报ip做解析,如果是指定的地区的,就提取出来放 在一个列表里
        :param data_set: [[25, 1466062380.695127, '61.184.33.228'], [28, 1466062381.782367, '124.23.180.0'], [29, 1466062383.278005, '125.72.101.82']]
        :return:
        '''
        data_dic = {'data':[],'avg':None,'mid':None,'min':None,'max':None,'tp90':None,
                    'timestamp':data_set_timestamp}
        if data_set:
            for data_point in data_set:
                val,timestamp,ip_addr = data_point
                ip_lookup_obj = ip_lookup.IPLookup(ip_db_data=self.ip_db_data)
                lookup_res = ip_lookup_obj.lookpup(ip_addr)
                if lookup_res:
                    print('ip res:',lookup_res)
                    province_objs = models.Region.objects.filter(name__startswith=lookup_res.get('province'))
                    if province_objs:
                        if province_objs[0].id  == int(self.province_id):#是属于要监测的省的数据
                            print("match province:")
                            city_objs = models.Region.objects.filter(name__startswith=lookup_res.get('city'))
                            if city_objs:
                                if city_objs[0].id == int(self.city_id):#是属于要监测 的这个城市的
                                    data_dic['data'].append(data_point) #把这个数据加到要监测的地区统计列表里
                                    print("\033[41;1mfind one match in region %s %s:\033[0m" % (lookup_res['province'],lookup_res['city']),data_point)

        if data_dic['data']:#
            only_value_list = [i[0] for i in data_dic['data']] #把指标的值取出来交给下面的去计算平均值 什么的

            data_dic['avg'] = self._get_avg(only_value_list)
            data_dic['max'] = self._get_max(only_value_list)
            data_dic['max'] = self._get_max(only_value_list)
            data_dic['mid'] = self._get_mid(only_value_list)
            data_dic['tp90'] = self._get_tp90(only_value_list)

        return data_dic
    def _get_max(self,data_set):
        print("max:",data_set)
        if data_set:
            return max(data_set)
    def _get_min(self,data_set):
        if data_set:
            return min(data_set)
    def _get_avg(self,data_set):
        if data_set:
            #print('avg--:',type(data_set))
            print("\033[41;1mdataset:\033[0m",data_set)
            return (sum(data_set) / len(data_set))*5
        #return  random.randrange(50)
    def _get_mid(self,data_set):
        data_set.sort()
        if data_set:
            return data_set[int(len(data_set)/2)]
    def _get_tp90(self,data_set):
        if len(data_set) > 10:
            data_set.sort()
            return  data_set[int(len(data_set)*0.9)]

