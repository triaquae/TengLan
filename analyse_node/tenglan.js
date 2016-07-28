/**
 * Created by jieli on 5/30/16.
 */





var sniffer ={
    'report_url':null,
    'bandwith_test_img':null,
    'site_id':null,
    'collect': PerformanceCollect,
}
var PerformanceData = {} //store all the performance data


//获取所有css,js,img文件的加载速度
function resourceTiming()
{
    PerformanceData['resources_load_time'] = {}
   var resourceList = window.performance.getEntriesByType("resource");
   for (i = 0; i < resourceList.length; i++)
   {
      /*if (resourceList[i].initiatorType == "img")
      {
         alert("End to end resource fetch: "+ resourceList[i].responseEnd - resourceList[i].startTime);
      }*/
      console.log(resourceList[i].name + ":" + (resourceList[i].responseEnd - resourceList[i].startTime) ) ;
       PerformanceData['resources_load_time'][resourceList[i].name] = resourceList[i].responseEnd - resourceList[i].startTime;
   }
}
resourceTiming(); //get each resource

//collect timming

(function(window) {
    'use strict';

    /**
     * Navigation Timing API helpers
     * timing.getTimes();
     **/
    window.timing = window.timing || {
        /**
         * Outputs extended measurements using Navigation Timing API
         * @param  Object opts Options (simple (bool) - opts out of full data view)
         * @return Object      measurements
         */
        getTimes: function(opts) {
            var performance = window.performance || window.webkitPerformance || window.msPerformance || window.mozPerformance;

            if (performance === undefined) {
                return false;
            }

            var timing = performance.timing;
            var api = {};
            opts = opts || {};

            if (timing) {
                if(opts && !opts.simple) {
                    for (var k in timing) {
                        if (timing.hasOwnProperty(k)) {
                            api[k] = timing[k];
                        }
                    }
                }

                // Time to first paint
                if (api.firstPaint === undefined) {
                    // All times are relative times to the start time within the
                    // same objects
                    var firstPaint = 0;

                    // Chrome
                    if (window.chrome && window.chrome.loadTimes) {
                        // Convert to ms
                        firstPaint = window.chrome.loadTimes().firstPaintTime * 1000;
                        api.firstPaintTime = firstPaint - (window.chrome.loadTimes().startLoadTime*1000);
                    }
                    // IE
                    else if (typeof window.performance.timing.msFirstPaint === 'number') {
                        firstPaint = window.performance.timing.msFirstPaint;
                        api.firstPaintTime = firstPaint - window.performance.timing.navigationStart;
                    }
                    // Firefox
                    // This will use the first times after MozAfterPaint fires
                    //else if (window.performance.timing.navigationStart && typeof InstallTrigger !== 'undefined') {
                    //    api.firstPaint = window.performance.timing.navigationStart;
                    //    api.firstPaintTime = mozFirstPaintTime - window.performance.timing.navigationStart;
                    //}
                    if (opts && !opts.simple) {
                        api.firstPaint = firstPaint;
                    }
                }

                // Total time from start to load
                api.loadTime = timing.loadEventEnd - timing.fetchStart;
                // Time spent constructing the DOM tree
                api.domReadyTime = timing.domComplete - timing.domInteractive;
                // Time consumed preparing the new page
                api.readyStart = timing.fetchStart - timing.navigationStart;
                // Time spent during redirection
                api.redirectTime = timing.redirectEnd - timing.redirectStart;
                // AppCache
                api.appcacheTime = timing.domainLookupStart - timing.fetchStart;
                // Time spent unloading documents
                api.unloadEventTime = timing.unloadEventEnd - timing.unloadEventStart;
                // DNS query time
                api.lookupDomainTime = timing.domainLookupEnd - timing.domainLookupStart;
                // TCP connection time
                api.connectTime = timing.connectEnd - timing.connectStart;
                // Time spent during the request
                api.requestTime = timing.responseEnd - timing.requestStart;
                // Request to completion of the DOM loading
                api.initDomTreeTime = timing.domInteractive - timing.responseEnd;
                // Load event time
                api.loadEventTime = timing.loadEventEnd - timing.loadEventStart;
                //below customization
                //navi type
                api.navigationType = window.performance.navigation.type;
            }
            PerformanceData.times = api; //把数据 存到全局数组
            return api;
        },
        /**
         * Uses console.table() to print a complete table of timing information
         * @param  Object opts Options (simple (bool) - opts out of full data view)
         */
        printTable: function(opts) {
            var table = {};
            var data  = this.getTimes(opts) || {};
            Object.keys(data).sort().forEach(function(k) {
                table[k] = {
                    ms: data[k],
                    s: +((data[k] / 1000).toFixed(2))
                };
            });
            console.table(table);
        },
        /**
         * Uses console.table() to print a summary table of timing information
         */
        printSimpleTable: function() {
            this.printTable({simple: true});
        }
    };

})(this);


//for native ajax request

var xmlHttp;
function createxmlHttpRequest() {
    if (window.ActiveXObject) {
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    } else if (window.XMLHttpRequest) {
        xmlHttp = new XMLHttpRequest();
    }
}

function doPost(url,data){
    // 注意在传参数值的时候最好使用encodeURI处理一下，以防出现乱码
    createxmlHttpRequest();
    xmlHttp.open("POST",url);
    xmlHttp.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
    xmlHttp.send(data);
    xmlHttp.onreadystatechange = function() {
        if ((xmlHttp.readyState == 4) && (xmlHttp.status == 200)) {
            alert('success');
        } else {
            alert('fail');
        }
    }
}

//end native ajax request

//for jsonp
function $(str){
        return document.getElementById(str)
    }
function CreateScript(src) {
    var Scrip=document.createElement('script');
    console.log('src:' + src);
    Scrip.src=src;
    //document.body.appendChild(Scrip);
    document.body.appendChild(Scrip);

}
function jsonpcallback(json) {
        console.log(json.Remark);//Object { email="中国", email2="中国222"}
}
function do_jsonp(url,data){
  console.log("-->",url);
  var data_json = JSON.stringify(data);
  var url_with_data = url + "?callback=jsonpcallback" + "&data="+ data_json;
  //var url_with_data ="http://localhost:9000/api/data/report/?callback=jsonpcallback"
  //CreateScript(url_with_data);
  CreateScript(url_with_data)
}
//end jsonp

//do_jsonp();
//end jsonp

function PerformanceCollect(configs){
    console.log(configs);
    resourceTiming();
    console.log('====');
    timing.getTimes();
    //
    PerformanceData.site_id = configs.site_id; //汇报前带上站点id
    console.log(PerformanceData);
    //doPost(configs.report_url,{'data':'test'})
    do_jsonp(configs.report_url,PerformanceData);
}