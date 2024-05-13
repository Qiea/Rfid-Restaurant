<template>
  <!-- 可滚动大屏 -->
  <view class="scroll-screen">
  	<swiper 
  		class="scroll-screen" 
  		:vertical="false" 
  		:circular="true" 
  		:disable-touch="false" 
  		:autoplay="true">
		<swiper-item v-for="(item, index) in 5" :key="index" class="swiper-item">
			<image :src="`/static/news/${index}.jpg`" class="swiper-image"/>
		</swiper-item>

  	 </swiper>
	</view>
   
    <!-- 公告栏 -->
<view class="announcement-bar">
  <!-- 公告内容 -->
  <text>欢迎光临！今日特价菜品：红烧肉。</text>
</view>

<!-- 热门菜品列表 -->
<view class="menu-list" style="margin: 10px;">
  <view style="text-align: center;font-size: 17px;margin-bottom: 5%;font-weight: bold;">热门菜品</view>
  <view v-for="(item, index) in sortedItems.slice(0, 5)" :key="index" class="menu-item">
	<image :src="`/static/images/${item.name}.jpg`" class="item-image"/>
	<view class="item-info">
	  <text class="item-name">{{ item.name }}</text>
	  <text class="item-count">热度🔥: {{ item.count }}</text>
	</view>
  </view>
</view>

</template>


<script>
	
export default {
  data() {
    return {
      orders: [],
      sortedItems: []
    };
  },
  mounted() {
    this.fetchOrderData();
  },
  methods: {
    fetchOrderData() {
      wx.request({
        url: 'https://qiea.cc:3000/api/find/history', // 替换为您的实际API地址
        method: 'GET',
        success: res => {
          this.orders = res.data.map(order => JSON.parse(order.json_data));
          this.countItems();
        }
      });
    },
    countItems() {
      let itemCounts = {};
      this.orders.forEach(order => {
        for (let item in order.all_items) {
          if (!itemCounts[item]) {
            itemCounts[item] = 0;
          }
          itemCounts[item] += order.all_items[item];
        }
      });
      this.sortedItems = Object.keys(itemCounts).map(key => {
        return { name: key, count: itemCounts[key] };
      }).sort((a, b) => b.count - a.count);
    }
  }
};
</script>

<style>

.scroll-screen {
  width: 100%;
  height: calc((100vw * 533) / 800); /* 16:9 宽高比 */
  white-space: nowrap;
  overflow-x: scroll;
}

.announcement-bar {
  width: 100%;
  height: 50px; /* 根据需要调整高度 */
  background-color: #f2f2f2; /* 背景颜色，可自定义 */
  text-align: center;
  line-height: 50px; /* 使文字垂直居中 */
  margin-bottom: 10px; /* 与菜品列表的间距 */
}
	
.menu-list {
  display: flex;
  flex-direction: column;
}
.menu-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.item-image {
  width: 100px;
  height: 80px;
  margin-right: 10px;
}
.item-info {
  display: flex;
  flex-direction: column;
}
.item-name {
  font-size: 16px;
  font-weight: bold;
}
.item-count {
  font-size: 14px;
}
.swiper-item {
    /* 设置 swiper-item 的宽度和高度 */
    width: 100%;
    height: 100%;
}

.swiper-image {
    /* 继承 swiper-item 的宽度和高度 */
    width: 100%;
    height: 100%;
}

</style>
