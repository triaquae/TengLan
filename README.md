# TengLan
基于用户视角的网站访问质量分析监测项目

#安装使用

服务器端
python manage.py runserver 0.0.0.0:9000 
python manage.py run_analyzer #实时后台分析程序

客户端
在你想要监测的网站首页文件底部加入以下代码:
    <script src="/static/analyse_node/tenglan.js"></script>

    <!-- TengLan Analytics -->

    <script>
    sniffer.report_url = 'http://127.0.0.1:9000/api/data/report/';
    sniffer.bandwith_test_img = 'http://www.baidu.com';
    sniffer.site_id = 1;
    sniffer.bandwith_test_img_size = 2500;

    sniffer.collect(sniffer);
    </script>




