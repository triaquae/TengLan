#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TengLan.settings")

    from django.core.management import execute_from_command_line
    if len(sys.argv)>1 and sys.argv[1] == 'graph_test':
        import django
        django.setup()
        from analyse.views import REDIS_OBJ
        from analyse import data_handler
        obj = data_handler.LatestStatisticData(1,REDIS_OBJ)
        obj.get_latest_60mins_trends()
    if len(sys.argv)>1 and sys.argv[1] == 'run_analyzer':
        import django
        django.setup()
        from analyse.views import REDIS_OBJ
        from analyse.backends import analyzer
        analyzer_obj = analyzer.Analyzer(REDIS_OBJ)
        analyzer_obj.start()
        exit()

    execute_from_command_line(sys.argv)
