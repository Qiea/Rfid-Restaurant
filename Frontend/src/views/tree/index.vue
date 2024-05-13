<template>
  <div v-show="showOrders" style="margin: 20px 5px 30px 5px;">
    <table v-if="orders.length" style="text-align: center; border-collapse: collapse; width: 90%;margin-left: 5%; margin-top: 5%; border: 1px solid #ddd;">
      <thead>
        <tr style="background-color: #f2f2f2;">
          <th style="border: 1px solid #ddd; padding: 8px;">订单时间</th>
          <th style="border: 1px solid #ddd; padding: 8px;">菜品</th>
          <th style="border: 1px solid #ddd; padding: 8px;">数量</th>
          <th style="border: 1px solid #ddd; padding: 8px;">总金额</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(order, index) in orders.slice().reverse()" :key="index" style="border: none;">
          <td style="border: none; padding: 0; border-bottom: 1px solid #ddd;">
            {{ JSON.parse(order.json_data).order_time }}
          </td>
          <td style="border: none; padding: 0; border-left: 1px solid #ddd; border-bottom: 1px solid #ddd;">
            <table style="border-collapse: collapse; width: 100%; margin: 0;">
              <tr v-for="(value, key, index) in JSON.parse(order.json_data).all_items" :key="value">
                <td :style="{ 'border': 'none', 'padding': '4px', 'border-bottom': index === Object.keys(JSON.parse(order.json_data).all_items).length - 1 ? 'none' : '1px solid #ddd' }">{{ key }}</td>
              </tr>
            </table>
          </td>
          <td style="border: none; padding: 0; border-left: 1px solid #ddd; border-bottom: 1px solid #ddd;">
            <table style="border-collapse: collapse; width: 100%; margin: 0;">
              <tr v-for="(value, key, index) in JSON.parse(order.json_data).all_items" :key="value">
                <td :style="{ 'border': 'none', 'padding': '4px', 'border-bottom': index === Object.keys(JSON.parse(order.json_data).all_items).length - 1 ? 'none' : '1px solid #ddd' }">{{ value }}</td>
              </tr>
            </table>
          </td>
          <td style="border: none; padding: 0; border-bottom: 1px solid #ddd;border-left: 1px solid #ddd;">{{ JSON.parse(order.json_data).allmoney }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else style="text-align: center;">No data available</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      showOrders: true,
      orders: []
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      axios.get('https://qiea.cc:3000/api/find/history')
        .then(response => {
          this.orders = response.data
        })
        .catch(error => {
          console.error('Error fetching data:', error)
        })
    }
  }
}
</script>
