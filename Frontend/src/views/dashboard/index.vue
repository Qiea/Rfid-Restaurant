<template>
  <div>
    <div style="text-align: center">
      <h1 style="text-align: center">订单列表</h1>
      <button style="margin: 10px" @click="toggleOrdersVisibility">切换订单列表显示/隐藏</button>
    </div>

    <div v-show="showOrders">
      <div v-if="orders.length">
        <table style="border-collapse: collapse; width: 90%;margin-left: 5%; margin-top: 5%; border: 1px solid #ddd;margin-bottom: 50px">
          <thead>
            <tr style="background-color: #f2f2f2;">
              <th style="border: 1px solid #ddd; padding: 8px;">订单时间</th>
              <th style="border: 1px solid #ddd; padding: 8px;">菜品</th>
              <th style="border: 1px solid #ddd; padding: 8px;">数量</th>
              <th style="border: 1px solid #ddd; padding: 8px;">总金额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(order, index) in orders.slice().reverse()" :key="index" style="border: 1px solid #ddd;">
              <td style="border: 1px solid #ddd; padding: 8px;">{{ JSON.parse(order.json_data).order_time }}</td>
              <td style="border: 1px solid #ddd; padding: 8px;">
                <table style="border-collapse: collapse; width: 100%;">
                  <tr v-for="(value, key) in JSON.parse(order.json_data).all_items" :key="value">
                    <td style="border: 0; padding: 4px;">{{ key }}</td>
                  </tr>
                </table>
              </td>
              <td style="border: 1px solid #ddd; padding: 8px;">
                <table style="border-collapse: collapse; width: 100%;">
                  <tr v-for="(value) in JSON.parse(order.json_data).all_items" :key="value">
                    <td style="border: 0; padding: 4px;">{{ value }}</td>
                  </tr>
                </table>
              </td>
              <td style="border: 1px solid #ddd; padding: 8px;">{{ JSON.parse(order.json_data).allmoney }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else style="text-align: center;">No data available</p>
    </div>

    <!-- 订单金额统计图表容器 -->
    <div ref="orderChart" class="charts" style="margin-top: 30px" />
    <!-- 店内财务统计图表容器 -->
    <div ref="financeChart" class="charts" />
    <!-- 菜单统计图表容器 -->
    <div ref="menuChart" class="charts" />
    <!-- 最受欢迎菜品统计图表容器 -->
    <div ref="popularMenuChart" class="charts" />

    <div style="height: 170px;text-align: center">
      <img src="/wxapp.jpg" alt="图片" style="width: 100px;height: 100px">
      <div style="padding-top: 15px">扫描二维码进入小程序</div>
    </div>
  </div>

</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  data() {
    return {
      orders: [],
      showOrders: false // 控制订单列表显示/隐藏的变量
    }
  },
  mounted() {
    this.fetchData()
    setInterval(this.fetchData, 1000) // 每秒钟更新一次数据
  },
  methods: {
    fetchData() {
      axios.get('https://qiea.cc:3000/api/find/history')
        .then(response => {
          this.orders = response.data
          this.drawOrderChart()
          this.drawFinanceChart()
          this.drawMenuChart()
          this.drawPopularMenuChart()
        })
        .catch(error => {
          console.error('Error fetching data:', error)
        })
    },

    drawOrderChart() {
      const chartData = this.orders.map(order => {
        const jsonData = JSON.parse(order.json_data)
        return {
          orderTime: jsonData.order_time,
          totalMoney: jsonData.allmoney
        }
      })
      const chart = echarts.init(this.$refs.orderChart)

      const option = {
        grid: {
          top: 70,
          left: 10,
          right: 10,
          width: 'auto',
          height: '70%',
          containLabel: true // 确保标签完全显示
        },
        title: {
          text: '近期订单概览',
          left: 'center',
          textStyle: {
            color: '#c23531' // 标题颜色
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross', // 十字准星指示器
            label: {
              backgroundColor: '#6a7985'
            }
          },
          textStyle: {
            width: 160,
            height: 250,
            lineHeight: 24,
            color: '#000',
            fontSize: '14'
          },
          formatter: function(params) {
            const dataIndex = params[0].dataIndex
            const orderDetails = JSON.parse(this.orders[dataIndex].json_data)
            let tooltipText = '订单时间: ' + orderDetails.order_time + '<br>'
            tooltipText += '订单详情:<br>'
            Object.entries(orderDetails.all_items).forEach(([itemName, quantity]) => {
              tooltipText += itemName + '：' + quantity + '份<br>'
            })
            tooltipText += '总金额: ' + orderDetails.allmoney + '￥'
            return tooltipText
          }.bind(this)
        },
        visualMap: { // 数据视觉映射组件
          top: 50,
          right: 30,
          pieces: [{
            gt: 0,
            lte: 99,
            color: '#096'
          }, {
            gt: 100,
            lte: 499,
            color: '#ffde33'
          }, {
            gt: 500,
            lte: 999,
            color: '#ff9933'
          }, {
            gt: 1000,
            color: '#cc0033'
          }],
          outOfRange: {
            color: '#999'
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false, // 坐标轴两边留白策略
          data: chartData.map(item => item.orderTime)
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value} ￥'
          }
        },
        series: [{
          data: chartData.map(item => item.totalMoney),
          type: 'line',
          areaStyle: { // 区域填充样式
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
              offset: 0,
              color: 'rgba(255, 0, 0, 0.5)' // 渐变起始颜色
            }, {
              offset: 1,
              color: 'rgba(255, 255, 0, 0.2)' // 渐变结束颜色
            }])
          },
          smooth: true, // 曲线平滑
          symbol: 'circle', // 标记的图形为实心圆
          symbolSize: 10, // 标记的大小
          showSymbol: false, // 鼠标悬停时才显示标记
          itemStyle: {
            normal: {
              color: 'rgba(255, 0, 0, 1)', // 折线点的颜色
              shadowBlur: 5, // 阴影大小
              shadowColor: 'rgba(255, 255, 255, 1)' // 阴影颜色
            }
          },
          markPoint: { // 标注
            data: [
              { type: 'max', name: '最大值' },
              { type: 'min', name: '最小值' }
            ]
          }
        }]
      }

      chart.setOption(option)
      window.addEventListener('resize', function() {
        chart.resize()
      })
    },
    drawFinanceChart() {
      // 提取订单中的总金额和日期
      const financeData = this.orders.map(order => {
        const jsonData = JSON.parse(order.json_data)
        return {
          date: jsonData.order_time,
          totalMoney: jsonData.allmoney
        }
      })

      // 根据日期对订单进行分组，计算每日总销售额
      const financeChartData = {}
      financeData.forEach(item => {
        const date = item.date.split(' ')[0] // 提取日期，去除时间
        if (!financeChartData[date]) {
          financeChartData[date] = 0
        }
        financeChartData[date] += parseFloat(item.totalMoney)
      })

      // 转换成 ECharts 需要的数据格式
      const xAxisData = Object.keys(financeChartData)
      const seriesData = Object.values(financeChartData)

      // 初始化 ECharts 实例
      const financeChart = echarts.init(this.$refs.financeChart)

      // 配置项
      const option = {
        grid: {
          top: 70,
          left: 10,
          right: 10,
          width: 'auto',
          height: '70%',
          containLabel: true // 确保标签完全显示
        },
        color: ['#3398DB'], // 设置图表主题色
        title: {
          text: '店内财务统计',
          left: 'center',
          textStyle: {
            color: '#c23531', // 设置标题颜色
            fontWeight: 'bold', // 设置标题字体粗细
            fontFamily: 'Arial', // 设置标题字体
            fontSize: 18 // 设置标题字体大小
          }
        },
        tooltip: {
          trigger: 'axis',
          textStyle: {
            width: 160,
            height: 250,
            lineHeight: 24,
            color: '#000',
            fontSize: '14'
          },
          axisPointer: {
            type: 'shadow' // 设置指示器类型为阴影
          },
          formatter: '{b}<br/>总共: {c}￥'
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          axisTick: {
            alignWithLabel: true // 确保刻度线和标签对齐
          },
          axisLabel: {
            textStyle: {
              fontSize: 12 // 设置标签字体大小
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            textStyle: {
              fontSize: 12 // 设置标签字体大小
            },
            formatter: '{value}￥' // 设置标签格式
          },
          splitLine: {
            lineStyle: {
              color: '#444' // 设置分割线颜色
            }
          }
        },
        series: [{
          name: '总销售额',
          type: 'bar',
          barWidth: '60%', // 设置柱状图宽度
          data: seriesData,
          itemStyle: {
            barBorderRadius: 5, // 设置柱状图圆角
            color: new echarts.graphic.LinearGradient( // 设置柱状图渐变色
              0, 0, 0, 1,
              [
                { offset: 0, color: '#83bff6' },
                { offset: 0.5, color: '#188df0' },
                { offset: 1, color: '#188df0' }
              ]
            )
          },
          emphasis: {
            focus: 'series' // 设置高亮策略为聚焦当前系列
          },
          animationDelay: function(idx) {
            return idx * 10 // 设置动画延迟效果
          },
          label: {
            show: true, // 显示标签
            position: 'top', // 位置
            color: '#000', // 颜色
            fontSize: 12, // 字体大小
            borderWidth: 1, // 边框宽度
            borderColor: '#fff', // 边框颜色
            backgroundColor: '#eeeeee', // 背景颜色
            padding: [4, 8], // 内边距
            borderRadius: 4, // 边框圆角
            formatter: '{c}￥' // 自定义标签内容，在数据后加上 '￥'
          }
        }],
        animationEasing: 'elasticOut'
      }

      // 渲染图表
      financeChart.setOption(option)
      window.addEventListener('resize', function() {
        financeChart.resize()
      })
    },
    drawMenuChart() {
      // 提取订单中的菜品信息
      const menuData = this.orders.reduce((accumulator, order) => {
        const jsonData = JSON.parse(order.json_data)
        Object.entries(jsonData.all_items).forEach(([itemName, quantity]) => {
          if (!accumulator[itemName]) {
            accumulator[itemName] = 0
          }
          accumulator[itemName] += parseInt(quantity)
        })
        return accumulator
      }, {})
      const menuChartData = Object.entries(menuData).sort((a, b) => b[1] - a[1])
      const menuChart = echarts.init(this.$refs.menuChart)
      const option = {
        grid: {
          top: 70,
          left: 10,
          right: 10,
          width: 'auto',
          height: '70%',
          containLabel: true // 确保标签完全显示
        },
        title: {
          text: '菜品总出售数',
          left: 'center',
          textStyle: {
            color: '#c23531', // 标题颜色
            fontWeight: 'bold'
          }
        },
        color: ['#c23531', '#2f4554', '#61a0a8', '#d48265', '#91c7ae', '#749f83', '#ca8622', '#bda29a', '#6e7074', '#546570', '#c4ccd3'], // 自定义系列颜色
        xAxis: {
          type: 'category',
          data: menuChartData.map(item => item[0])
        },
        yAxis: {
          type: 'value'
        },
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}份',
          backgroundColor: 'rgba(255,255,255,1)', // 提示框背景色
          borderColor: '#333', // 提示框边框色
          borderWidth: 0,
          textStyle: {
            width: 160,
            height: 250,
            lineHeight: 24,
            color: '#000',
            fontSize: '14'
          }
        },
        series: [{
          data: menuChartData.map(item => item[1]),
          type: 'bar',
          showBackground: true, // 显示背景色
          backgroundStyle: {
            color: 'rgba(180, 180, 180, 0.2)' // 背景色
          },
          itemStyle: {
            barBorderRadius: 5, // 柱状图圆角
            shadowBlur: 10, // 阴影模糊大小
            shadowColor: 'rgba(0, 0, 0, 0.5)' // 阴影颜色
          },
          animationEasing: 'elasticOut', // 动画效果
          animationDelay: function(idx) {
            return idx * 50 // 动画延迟
          }
        }]
      }
      menuChart.setOption(option)
      window.addEventListener('resize', function() {
        menuChart.resize()
      })
    },
    drawPopularMenuChart() {
      // 提取订单中的菜品信息
      const menuData = this.orders.reduce((accumulator, order) => {
        const jsonData = JSON.parse(order.json_data)
        Object.entries(jsonData.all_items).forEach(([itemName]) => {
          if (!accumulator[itemName]) {
            accumulator[itemName] = 0
          }
          accumulator[itemName]++
        })
        return accumulator
      }, {})

      // 按照菜品出现次数排序
      const sortedMenuData = Object.entries(menuData).sort((a, b) => b[1] - a[1])

      // 取出前几名的菜品和销量
      const topItems = sortedMenuData.slice(0, 5)

      // 初始化 ECharts 实例
      const popularMenuChart = echarts.init(this.$refs.popularMenuChart)

      // 配置项
      const option = {
        grid: {
          top: 70,
          left: 10,
          right: 10,
          width: 'auto',
          height: '70%',
          containLabel: true // 确保标签完全显示
        },
        title: {
          text: '最受欢迎菜品统计',
          subtext: '菜品出现在单个菜单上的次数',
          left: 'center',
          top: 0,
          textStyle: {
            color: '#c23531', // 标题颜色
            fontWeight: 'bold'
          }
        },
        tooltip: {
          textStyle: {
            width: 160,
            height: 250,
            lineHeight: 24,
            color: '#000',
            fontSize: '14'
          },
          trigger: 'axis',
          axisPointer: {
            type: 'shadow' // 提示框指针类型
          },
          formatter: '{b}: {c}次'
        },
        xAxis: {
          type: 'category',
          data: topItems.map(item => item[0]),
          axisTick: {
            alignWithLabel: true
          },
          axisLine: {
          }
        },
        yAxis: {
          type: 'value',
          axisLine: {
          },
          splitLine: {
            lineStyle: {
              color: '#bdbdbd', // 分割线颜色
              type: 'dashed' // 分割线类型
            }
          }
        },
        series: [{
          name: '销量',
          data: topItems.map(item => item[1]),
          type: 'bar',
          barWidth: '60%',
          itemStyle: {
            normal: {
              color: new echarts.graphic.LinearGradient( // 柱状图渐变色
                0, 0, 0, 1,
                [
                  { offset: 0, color: '#ff9e80' }, // 0% 处的颜色
                  { offset: 1, color: '#ff3d00' } // 100% 处的颜色
                ]
              ),
              shadowColor: 'rgba(0, 0, 0, 0.4)', // 阴影颜色
              shadowBlur: 10 // 阴影模糊大小
            }
          },
          emphasis: {
            focus: 'series',
            itemStyle: {
              color: '#d50000' // 高亮时的颜色
            }
          },
          animationEasing: 'bounceOut', // 动画效果
          animationDelay: function(idx) {
            return idx * 100 // 动画延迟
          }
        }]
      }

      // 渲染图表
      popularMenuChart.setOption(option)
      window.addEventListener('resize', function() {
        popularMenuChart.resize()
      })
    },

    toggleOrdersVisibility() {
      this.showOrders = !this.showOrders
    }
  }
}
</script>

<style>
.charts {
  width: 95%;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  margin: 20px;
}
</style>
