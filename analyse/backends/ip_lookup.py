#_*_coding:utf-8_*_
__author__ = 'Alex Li'
import socket,struct


class IPLookup(object):
    def __init__(self,ip_db_filename=None,ip_db_data=None):
        '''

        :param ip_db_filename: 如果不为空,代表需要把文件里的ip库转成内存的数据格式
        :param ip_db_data: 如果不为空,代表传进来的就是ip库
        :return:
        '''

        if  ip_db_filename == None and ip_db_data == None: #至少有一个不能为空
            raise KeyError
        if ip_db_filename != None and ip_db_data != None: #只能有一个不为空
            raise KeyError
        if ip_db_data:
            self.ip_db_data = ip_db_data
        elif ip_db_filename:
            db_data = self.load_db_from_file(ip_db_filename)
            self.ip_db_data = db_data


    def load_db_from_file(self,ip_db_filename):
        db_dic = {'data':{},'keys':[]}
        with open(ip_db_filename,'r') as f:
            for line in f:
                ip_range_start,ip_range_end,ip_range_start_int,ip_range_end_int,country,province,city,district,isp,code \
                = line.split('|')
                #print(ip_range_end)

                db_dic['data'][int(ip_range_start_int)] = {
                    'ip_range_start':ip_range_start,
                    'ip_range_end'  :ip_range_end,
                    'ip_range_end_int': int(ip_range_end_int),
                    'country':country,
                    'province': province,
                    'city': city,
                    'district':district,
                    'isp':isp,
                    'code':code
                }

            db_dic['keys'] = list(db_dic['data'].keys() )
            db_dic['keys'] = list(map(lambda x:int(x),db_dic['keys']) )
            db_dic['keys'].sort()
            #print(len(db_dic['keys']) )
        return  db_dic
    def lookpup(self,ip_addr):
        print("\033[31;1mlooking for ip:%s\033[0m" %ip_addr)
        ip_to_asic = socket.inet_aton(ip_addr)
        ip_int = struct.unpack('!L', ip_to_asic)[0]
        #ip_int = 975201280
        print(ip_to_asic,ip_int)

        #start binary search
        key_list = self.ip_db_data['keys']
        left_pos = 0
        right_pos = len(key_list) -1

        while left_pos <= right_pos:#左边与右边没碰面
            mid_pos = int((left_pos + right_pos) /2 )

            if ip_int < key_list[mid_pos] : #代表ip_int在列表中mid_pos的值左边
                right_pos = mid_pos -1 #使下一次loop在左边的列表中开始找
                print("going to find in left part,", left_pos,right_pos,key_list[mid_pos])
            elif ip_int > key_list[mid_pos]: #代表ip_int在列表中mid_pos的值右边
                left_pos = mid_pos+1
                print("going to find in right part,",left_pos,right_pos,key_list[mid_pos])
            else:#只能相等了
                print("find mid == your looking for value", key_list[mid_pos])
                print(self.ip_db_data['data'][key_list[mid_pos]])
                print("%s %s %s" %(self.ip_db_data['data'][key_list[mid_pos]]['province'],
                      self.ip_db_data['data'][key_list[mid_pos]]['city'],
                      self.ip_db_data['data'][key_list[mid_pos]]['district'],
                           ))  #找到了
                return self.ip_db_data['data'][key_list[mid_pos]] #找到了
                break
        else:
            print("没直接找到,试试db_dic")
            closest_item = self.ip_db_data['data'][key_list[mid_pos]]
            #print(closest_item)
            ip_range_end_int = closest_item['ip_range_end_int']
            if ip_int> key_list[mid_pos]  and ip_range_end_int >= ip_int:
                print("找到了 %s" % closest_item)
                return closest_item
            else:
                print("数据库里没这个IP")
if __name__ == '__main__':
    obj = IPLookup(ip_db_filename='src/ipdb-20140902-99884.txt')

    obj.lookpup('123.131.134.50')
    #obj.lookpup('8.8.8.8')