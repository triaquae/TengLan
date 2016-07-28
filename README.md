# TengLan
基于用户视角的网站访问质量分析监测项目

#安装使用

服务器端:
   python manage.py runserver 0.0.0.0:9000 
   python manage.py run_analyzer #实时后台分析程序

客户端:
在你想要监测的网站首页文件底部加入以下代码:
    <script src="/static/analyse_node/tenglan.js"></script> #监测代码

    <!-- TengLan Analytics -->

    <script>
    sniffer.report_url = 'http://127.0.0.1:9000/api/data/report/'; #监测结果汇报地址
    sniffer.bandwith_test_img = 'http://www.baidu.com'; #如果要测试用户带宽，指定下载测试图片
    sniffer.site_id = 1; #这是在服务器端帮这个站点分配的站点id
    sniffer.bandwith_test_img_size = 2500; #写清楚你要测试下载的图片大小，不测试带宽的话不需要

    sniffer.collect(sniffer); #开始收集数据并向服务器端汇报
    </script>


项目截图:
*注:由于是课件，所以未完全实现


