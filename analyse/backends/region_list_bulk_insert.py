#_*_coding:utf-8_*_
__author__ = 'Alex Li'

import os
import sys

def bulk_insert_province(filename):
    with open(filename) as f:
        for line in f:
            province_id,province_name,abbr = line.split()
            obj = models.Region(
                region_id= province_id,
                region_type = 'province',
                name = province_name
            )
            obj.save()


def bulk_insert_city(filename):
    pro_objs = models.Region.objects.filter(region_type='province')
    pro_id_list = [str(p.region_id) for p in pro_objs]
    #print(pro_id_list)
    with open(filename) as f:
        for line in f:
            line = line.split()
            city_id = line[0]
            city_name = line[1]
            #print(line)
            #print(city_id[:2])
            for pro_id in pro_id_list:
                if pro_id.startswith(city_id[:2]): #this city belongs to this province
                    province_obj = models.Region.objects.get(region_type='province',region_id=pro_id)
                    print(province_obj,line)
                    new_city_obj = models.Region(
                        region_type = 'city',
                        region_id = city_id,
                        name = city_name,
                        child_of = province_obj
                    )
                    new_city_obj.save()
            #province_obj = models.Region.objects.get(region_type='province',region_id__li)
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TengLan.settings")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(BASE_DIR)
    #sys.path.append(BASE_DIR)
    import django
    django.setup()
    from analyse import models
    #bulk_insert_province('%s/src/province_id_list' %BASE_DIR)
    bulk_insert_city("%s/src/city_id_list" % BASE_DIR)