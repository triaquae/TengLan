
from django.conf.urls import url,include

from analyse import views
urlpatterns = [
    url(r'data/report/',views.data_report),
    url(r'data/get_latest_analysis_data/',views.get_latest_analysis_data, name='get_latest_analysis_data'),
    url(r'data/latest_country_map_view/',views.get_latest_country_map_view, name='get_latest_country_map_view'),
    url(r'region_list',views.get_region_list, name='get_region_list'),
    url(r'region_trends_data',views.get_region_trends_data, name='get_region_trends_data'),
    url(r'region_realtime_output',views.get_region_realtime_output, name='get_region_realtime_output'),
]
