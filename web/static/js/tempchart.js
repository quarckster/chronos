AmCharts.makeChart("chartdiv",
        {
            "type": "serial",
            "dataLoader": {
                "url": "chart_data",
                "format": "json",
                "reload": 60
            },
            "pathToImages": "http://cdn.amcharts.com/lib/3/images/",
            "categoryField": "date",
            "dataDateFormat": "YYYY-MM-DD HH:NN",
            "categoryAxis": {
                "minPeriod": "mm",
                "parseDates": true
            },
            "chartCursor": {
                "categoryBalloonDateFormat": "JJ:NN"
            },
            "graphs": [
                {
                    "bullet": "round",
                    "id": "AmGraph-1",
                    "title": "Water Outlet",
                    "valueField": "column-1"
                },
                {
                    "bullet": "square",
                    "id": "AmGraph-2",
                    "title": "Water Inlet",
                    "valueField": "column-2"
                }
            ],
            "legend": {
                "useGraphSettings": true
            },
            "valueAxes": [
                {
                    "id": "ValueAxis-1",
                    "title": "Temperature"
                }
            ]
        })