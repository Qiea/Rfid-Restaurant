<template>
  <div>

    <div style="margin: 15px">
      <!-- 设备在线检测 -->
      <div ref="buttons">
        <div style="display: flex; align-items: center;flex-wrap: wrap">
          <div class="state">
            <el-button v-if="isDeviceOnline" type="success" style="pointer-events: none;">设备在线</el-button>
            <el-button v-else type="danger" disabled style="pointer-events: none;">设备离线</el-button>
          </div>
          <div class="state">
            <el-button v-if="isProcessesOnline" type="success" style="pointer-events: none">读卡器在线</el-button>
            <el-button v-else type="danger" disabled style="pointer-events: none">读卡器离线</el-button>
          </div>
          <div class="state" v-if="isProcessesOnline">
            <el-button v-if="Devicetemp < 60" type="success" style="pointer-events: none">设备温度:{{ Devicetemp }}℃</el-button>
            <el-button v-else type="danger" style="pointer-events: none">设备温度:{{ Devicetemp }}℃</el-button>
          </div>

          <div v-if="showFlexGrow" style="flex-grow: 1" />
          <div class="state">
            <el-button type="danger" plain @click="closeProcesses">关闭读卡器</el-button>
          </div>
          <div class="state" style="margin-right: 0">
            <el-button type="danger" plain @click="restartProcesses">重启读卡器</el-button>
          </div>
        </div>
      </div>

      <!-- 日志条目 -->
      <div v-for="(entry, index) in logEntries" :key="index" class="log-entry">
        <!-- 使用 v-html 指令渲染 HTML -->
        <span v-html="formatLog(entry.log)" />
      </div>
    </div>
    <div id="cc-myssl-id" style="position: fixed;right: 0;bottom: 0;width: 65px;height: 65px;z-index: 99;">
      <a href="https://myssl.com/rfid.qiea.cc?from=mysslid"><img src="https://static.myssl.com/res/images/myssl-id.png" alt="" style="width:100%;height:100%"></a>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

var DHB
var PHB

export default {
  data() {
    return {
      logEntries: [],
      DeviceofflineCounter: 0, // 新增离线计数器
      ProcessesofflineCounter: 0, // 新增离线计数器
      isDeviceOnline: 0, // 新增设备在线状态
      isProcessesOnline: 0, // 新增设备在线状态
      Devicetemp: 0,
      showFlexGrow: false
    }
  },
  mounted() {
    this.fetchData()
    setInterval(this.fetchData, 100) // 每秒钟更新一次数据
    this.checkParentHeight() // 组件挂载时检查高度
    window.addEventListener('resize', this.checkParentHeight) // 监听窗口调整大小事件
  },
  methods: {
    checkParentHeight() {
      const buttonsDiv = this.$refs.buttons // 获取父级 div "buttons" 的引用
      this.showFlexGrow = buttonsDiv.clientHeight < 87
    },
    async fetchData() {
      try {
        const response = await axios.get('https://qiea.cc:3000/api/find/log')
        this.logEntries = response.data

        // 检测设备在线状态
        const heartbeats = this.logEntries.map(entry => entry.HeartBeat)
        const deviceheartbeats = this.logEntries.map(entry => entry.DeviceHeartBeat)
        const temp = this.logEntries.map(entry => entry.Temp)

        if (deviceheartbeats[0] === 1) {
          this.isDeviceOnline = 1
          this.DeviceofflineCounter = 0 // 如果检测到设备在线，将计数器重置为0
        } else {
          this.DeviceofflineCounter++ // 如果设备离线，则增加计数器
          if (this.DeviceofflineCounter > 70) {
            this.isDeviceOnline = 0 // 如果连续三次检测到设备离线，则将设备标记为离线
          }
        }
        // 更新离线计数器
        if (heartbeats[0] === 1) {
          this.isProcessesOnline = 1
          this.ProcessesofflineCounter = 0 // 如果检测到设备在线，将计数器重置为0
        } else {
          this.ProcessesofflineCounter++ // 如果设备离线，则增加计数器
          if (this.ProcessesofflineCounter > 50) {
            this.isProcessesOnline = 0 // 如果连续三次检测到设备离线，则将设备标记为离线
          }
        }
        this.Devicetemp = temp[0]
        DHB = this.isDeviceOnline
        PHB = this.isProcessesOnline
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    },
    closeProcesses() {
      if (DHB === 0 && PHB === 0) {
        this.$message({
          message: '请先启动设备!',
          type: 'error'
        })
      }
      if (DHB === 1 && PHB === 0) {
        this.$message({
          message: '请先启动读卡器!',
          type: 'error'
        })
      }
      if (DHB === 1 && PHB === 1) {
        this.$message({
          message: '读卡器正在关闭中...',
          type: 'success'
        })
        axios.get('https://qiea.cc:3000/api/set/killprogress')
          .then(response => {
            console.log('Processes closed successfully:', response.data)
          // You can perform additional actions if needed
          })
          .catch(error => {
            console.error('Error closing processes:', error)
          })
      }
    },
    restartProcesses() {
      if (DHB === 0) {
        this.$message({
          message: '请先启动设备!',
          type: 'error'
        })
      }
      if (DHB === 1) {
        this.$message({
          message: '读卡器正在重启中...',
          type: 'success'
        })
        axios.get('https://qiea.cc:3000/api/set/restartprogress')
          .then(response => {
            console.log('Processes restarted successfully:', response.data)
            // You can perform additional actions if needed
          })
          .catch(error => {
            console.error('Error restarting processes:', error)
          })
      }
    },
    formatLog(log) {
      // 将 \n 替换为 HTML 换行符 <br>
      return log.replace(/\n/g, '<br>')
    }
  }
}
</script>

<style>
.log-entry {
  margin-top: 10px;
  padding: 5px;
  border-radius: 5px; /* 圆角 */
  overflow: hidden; /* 防止内容溢出 */
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); /* 阴影效果 */
}

.state {
  margin:0 8px 8px 0;
}
</style>
