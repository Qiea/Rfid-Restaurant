<template>
  <div style="margin-bottom: 30px">
    <!-- 表格部分 -->
    <table>
      <thead>
        <tr>
          <th>菜品ID</th>
          <th>菜品名字</th>
          <th>菜品价格</th>
          <th>菜品数量</th>
          <th>菜品种类</th>
          <th>EPC数据</th>
          <th style="width: 101px;min-width: 101px;">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(dish, index) in dishes" :key="index">
          <td>{{ dish.菜品ID }}</td>
          <td>{{ dish.菜品名字 }}</td>
          <td>{{ dish.菜品价格 }}</td>
          <td>{{ dish.菜品数量 }}</td>
          <td>{{ dish.菜品种类 }}</td>
          <td>{{ dish.EPC数据 }}</td>
          <td style="padding: 0">
            <el-button style="border-radius: 0;padding: 0 7px 0 15px;border: 0;width: 50px;float: left" plain @click="modifyDish(index)">修改</el-button>
            <el-button style="border-radius: 0;padding: 0 7px 0 0;border: 0;width: 50px;float: left;margin-left: 0" plain @click="confirmDelete(index)">删除</el-button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 删除确认对话框 -->
    <el-dialog
      title="确认删除"
      :visible.sync="deleteDialogVisible"
      width="260px"
      center>
      <span style="margin: 35px">是否确认删除该菜品？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="deleteDishConfirmed">确认删除</el-button>
      </span>
    </el-dialog>

    <el-button style="margin-left: 5%; margin-top: 5%;width: 100px;" @click="modifyAdd(index)">添加数据</el-button>

    <!-- 修改菜品模态框 -->
    <div v-if="showEditModal">
      <div style="margin-top: 5%;margin-left: 5%;margin-right: 5%;">
        <!-- 表单内容 -->
        <label>菜品名字:</label>
        <input v-model="editedDish.菜品名字" type="text">
        <label>菜品价格:</label>
        <input v-model="editedDish.菜品价格" type="number">
        <label>菜品数量:</label>
        <input v-model="editedDish.菜品数量" type="number">
        <label>菜品种类:</label>
        <input v-model="editedDish.菜品种类" type="text">
        <label>EPC数据:</label>
        <input v-model="editedDish.EPC数据" type="text">

        <!-- 确认和取消按钮 -->
        <button @click="confirmEdit">确认</button>
        <button @click="cancelEdit">取消</button>

      </div>
    </div>

    <!-- 添加新菜品模态框 -->
    <div v-if="showAddModal">
      <div style="margin-top: 5%;margin-left: 5%;margin-right: 5%;">
        <!-- 表单内容 -->
        <label>菜品名字:</label>
        <input v-model="newDish.菜品名字" type="text">
        <label>菜品价格:</label>
        <input v-model="newDish.菜品价格" type="number">
        <label>菜品数量:</label>
        <input v-model="newDish.菜品数量" type="number">
        <label>菜品种类:</label>
        <input v-model="newDish.菜品种类" type="text">
        <label>EPC数据:</label>
        <input v-model="newDish.EPC数据" type="text">

        <!-- 确认和取消按钮 -->
        <button @click="confirmAdd">确认</button>
        <button @click="cancelAdd">取消</button>

      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      dishes: [],
      showEditModal: false,
      showAddModal: false,
      editedDish: {},
      newDish: {
        菜品名字: '',
        菜品价格: 0,
        菜品数量: 0,
        菜品种类: '',
        EPC数据: ''
      },
      deleteDialogVisible: false,
      deleteIndex: null // 保存要删除的菜品的索引
    }
  },
  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get('https://qiea.cc:3000/api/find/menu')
        this.dishes = response.data
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    },
    modifyDish(index) {
      // 将选定菜品的信息加载到表单中
      this.editedDish = { ...this.dishes[index] }
      this.showEditModal = true
    },
    modifyAdd(index) {
      this.showAddModal = true
    },
    async confirmEdit() {
      try {
        // 将修改后的菜品信息提交到后端
        await axios.post('https://qiea.cc:3000/api/update/menu', {
          id: this.editedDish.菜品ID, // 将菜品ID作为id属性发送到后端
          菜品名字: this.editedDish.菜品名字,
          菜品价格: this.editedDish.菜品价格,
          菜品数量: this.editedDish.菜品数量,
          菜品种类: this.editedDish.菜品种类,
          EPC数据: this.editedDish.EPC数据
        })
        // 关闭模态框并重新加载数据
        this.showEditModal = false
        this.fetchData()
      } catch (error) {
        console.error('Error updating dish:', error)
      }
    },
    cancelEdit() {
      // 关闭模态框
      this.showEditModal = false
    },
    async confirmAdd() {
      try {
        // 将新菜品信息提交到后端
        await axios.post('https://qiea.cc:3000/api/add/menu', {
          菜品名字: this.newDish.菜品名字,
          菜品价格: this.newDish.菜品价格,
          菜品数量: this.newDish.菜品数量,
          菜品种类: this.newDish.菜品种类,
          EPC数据: this.newDish.EPC数据
        })
        // 关闭模态框并重新加载数据
        this.showAddModal = false
        this.fetchData()
      } catch (error) {
        console.error('Error adding dish:', error)
      }
    },
    cancelAdd() {
      // 关闭模态框
      this.showAddModal = false
    },
    confirmDelete(index) {
      this.deleteIndex = index
      this.deleteDialogVisible = true
    },
    deleteDishConfirmed() {
      const dishId = this.dishes[this.deleteIndex].菜品ID
      axios.delete(`https://qiea.cc:3000/api/delete/menu/${dishId}`)
        .then(() => {
          this.fetchData()
        })
        .catch((error) => {
          console.error('Error deleting dish:', error)
        })
      this.deleteDialogVisible = false
    }
  }
}
</script>

<style>
/* 可以添加一些样式来美化表格 */
table {
  text-align: center;
  border-collapse: collapse;
  margin: 20px 20px 0 20px;
  width: 90%;
}

th, td {
  border: 1px solid #dddddd;
  padding: 8px;
  height: 40px;
}

th {
  background-color: #f2f2f2;
}
</style>
