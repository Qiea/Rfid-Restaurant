<template>
  <div class="container">
    <div class="top">
		<div class="title" style="font-size: 18px; font-weight: bold; text-align: center; padding: 10px; background-color: #f0f0f0; border-bottom: 3px solid #ccc;">
			<div>
				订单页面
			</div>
		</div>
	</div>
	
  <div class="bottom">
	<div v-if="order && !isOrderExpired" style="border: 0px solid #ccc; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
	  <p style="font-weight: bold;">订单时间：{{ order.order_time }}</p>
	  <p style="font-weight: bold;">总金额：{{ order.allmoney }}</p>
	  <p style="font-weight: bold;">商品详情：</p>
	  <ul>
		<li v-for="(count, item) in order.all_items" :key="item" style="list-style: none; margin-left: 0; padding-left: 0;">- {{ item }}: {{ count }}</li>
	  </ul>
	</div>

    <div v-else>
      <p v-if="isOrderExpired">还未点单</p>
      <p v-else>暂无数据</p>
    </div>
  </div>
  
  
  
  
  
  </div>
  
  
  
  
</template>

<script>
	
export default {
  data() {
    return {
      order: null
    };
  },
  mounted() {
    // 从API获取数据
    this.fetchOrderData();
  },
  computed: {
      isOrderExpired() {
        if (this.order) {
          const orderTime = new Date(this.order.order_time);
          const currentTime = new Date();
          const twoHoursInMillis = 2 * 60 * 60 * 1000; // 2 hours in milliseconds
          return currentTime - orderTime > twoHoursInMillis;
        }
        return false;
      }
    },
  methods: {
    fetchOrderData() {
      // 使用wx.request发送请求
      wx.request({
        url: 'https://qiea.cc:3000/api/find/history', // 替换为您的实际API地址
        method: 'GET',
        success: res => {
          // 假设res.data包含订单数据
          if (Array.isArray(res.data) && res.data.length > 0) {
            // 取数组中的第一个元素作为订单数据
			const lastOrder = JSON.parse(res.data[res.data.length - 1].json_data);
			
            this.order = lastOrder;
			
          } else {
            console.error("未找到订单数据");
          }
        },
        fail: err => {
          console.error("获取订单数据时出错:", err);
        }
      });
    }
  }
};


</script>

<style scoped>
.container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.top {
  background-color: #FF5733; /* 你希望的上半部分颜色 */
}

.bottom {
  background-color: #fff; /* 你希望的下半部分颜色 */
  height: 90%;
}
.tabbar-text {
  font-size: 16px;
  text-align: center;
  line-height: 50px; /* tabBar 的默认高度一般为 50px，这里用来垂直居中 */
}

</style>
