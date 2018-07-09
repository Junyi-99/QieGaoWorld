function abs(number){
    return number < 0 ? -number : number;
}
function test(text){
    alert(text);
}
var config0 = {
    type: 'doughnut',
    data: {
        datasets: [{
            data: [
                abs(randomScalingFactor()%5),
                abs(randomScalingFactor())
            ],
            backgroundColor: [
                window.chartColors.red,
                window.chartColors.green
            ],
            label: 'Online Users'
        }],
        labels: [
            "离线用户",
            "在线用户"
        ]
    },
    options: {
        responsive: true,
        legend: {
            display: false
        },
        title: {
            display: false
        },
        animation: {
            animateScale: true,
            animateRotate: true
        }
    },
    plugins: [{
        beforeDraw: function(chart) {
            return;
            var width = chart.chart.width,
                height = chart.chart.height,
                ctx = chart.chart.ctx;

            ctx.restore();
            var fontSize = (height / 114).toFixed(2);
            ctx.font = fontSize + "em Verdana";

            ctx.textBaseline = "middle";

            var text = "99%",
                textX = Math.round((width - ctx.measureText(text).width) / 2),
                textY = height / 2;

            var gradient=ctx.createLinearGradient(0,0,chart.width,0);
            gradient.addColorStop("0","green");
            gradient.addColorStop("1.0", "#32d296");
            ctx.fillStyle = gradient;
            ctx.fillText(text, textX, textY);
            ctx.save();
          }
    }]
};
var barChartData = {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: [{
        backgroundColor: [
            window.chartColors.red,
            window.chartColors.orange,
            window.chartColors.yellow,
            window.chartColors.green,
            window.chartColors.blue,
            window.chartColors.purple,
            window.chartColors.red
        ],
        data: [
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor()
        ]
    }]

};
var config1 = {
    type: 'line',
    data: {
        labels: ["大大前天", "大前天", "前天", "昨天", "今天"],
        datasets: [{
            label: "小电视数量：",
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor())
            ],
            fill: false,
        },{
            label: "领取量",
            backgroundColor: window.chartColors.blue,
            borderColor: window.chartColors.blue,
            data: [
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor())
            ],
            fill: false,
        }]
    },
    options: {
        responsive: true,
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
            xAxes: [{
                display: false
            }],
            yAxes: [{
                display: false
            }]
        },
        legend: {
            display: false
        },
        layout: {
            padding: {
                left: 10,
                right: 10,
                top: 10,
                bottom: 10
            }
        }
    }
};
var config2 = {
    type: 'bar',
    data: barChartData,
    options: {
        responsive: true,
        title:{
            display:false,
        },
        legend: {
            display: false
        },
        tooltips: {
            display: false,
            mode: 'index',
            intersect: true
        },
        scales: {
            xAxes: [{
                display: false
            }],
            yAxes: [{
                display: false
            }]
        }
    }
};
var config3 = {
    type: 'line',
    data: {
        labels: ["大大前天", "大前天", "前天", "昨天", "今天"],
        datasets: [{
            label: "领取辣条",
            backgroundColor: window.chartColors.green,
            borderColor: window.chartColors.green,
            data: [
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor())
            ],
            fill: false,
        },{
            label: "领取活动礼物",
            backgroundColor: window.chartColors.purple,
            borderColor: window.chartColors.purple,
            data: [
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor()),
                abs(randomScalingFactor())
            ],
            fill: false,
        }]
    },
    options: {
        responsive: true,
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
            xAxes: [{
                display: false
            }],
            yAxes: [{
                display: false
            }]
        },
        legend: {
            display: false
        },
        layout: {
            padding: {
                left: 10,
                right: 10,
                top: 10,
                bottom: 10
            }
        }
    }
};
function chart_init() {
    var ctx0 = document.getElementById("chart-0");
    var ctx1 = document.getElementById("chart-1");
    var ctx2 = document.getElementById("chart-2");
    var ctx3 = document.getElementById("chart-3");
    if(ctx0 != null)
        var myChart0 = new Chart(ctx0, config0);
    if(ctx1 != null)
        var myChart1 = new Chart(ctx1, config1);
    if(ctx2 != null)
        var myChart2 = new Chart(ctx2, config2);
    if(ctx3 != null)
        var myChart3 = new Chart(ctx3, config3);
}