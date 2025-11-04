<template>
  <div class="commit-scroller">
    <h2>🏆 Top Contributors</h2>
    <div class="scroller-container" v-if="contributors.length > 0">
      <transition-group name="slide" tag="div" class="contributor-list">
        <div 
          v-for="contributor in visibleContributors" 
          :key="contributor.email"
          class="contributor-card"
        >
          <div class="rank">#{{ contributor.rank }}</div>
          <div class="avatar">👤</div>
          <div class="info">
            <div class="name">{{ contributor.name }}</div>
            <div class="email">{{ contributor.email }}</div>
          </div>
          <div class="commits">
            <span class="count">{{ contributor.commits }}</span>
            <span class="label">commits</span>
          </div>
        </div>
      </transition-group>
    </div>
    <div class="no-data" v-else>
      <p>暂无贡献者数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Contributor } from '../typings'

const props = defineProps<{
  contributors: Contributor[]
}>()

const currentIndex = ref(0)
const pageSize = 6 // 每页显示 6 个

// 当前可见的贡献者
const visibleContributors = computed(() => {
  if (props.contributors.length === 0) return []
  
  const start = currentIndex.value
  const end = start + pageSize
  
  // 如果不够一页，从头补充
  if (end <= props.contributors.length) {
    return props.contributors.slice(start, end)
  } else {
    const firstPart = props.contributors.slice(start)
    const remaining = pageSize - firstPart.length
    const secondPart = props.contributors.slice(0, remaining)
    return [...firstPart, ...secondPart]
  }
})

// 自动滚动
let scrollTimer: number

const autoScroll = () => {
  currentIndex.value += 1
  
  // 循环滚动
  if (currentIndex.value >= props.contributors.length) {
    currentIndex.value = 0
  }
}

onMounted(() => {
  if (props.contributors.length > pageSize) {
    // 每 3 秒滚动一次
    scrollTimer = setInterval(autoScroll, 3000) as unknown as number
  }
})

onUnmounted(() => {
  if (scrollTimer) {
    clearInterval(scrollTimer)
  }
})
</script>

<style lang="scss" scoped>
.commit-scroller {
  width: 100%;
  height: 100%;
  background-color: #212121;
  padding: 30px;
  overflow: hidden;
  
  h2 {
    font-size: 2em;
    text-align: center;
    margin-bottom: 30px;
    color: #de335e;
    text-shadow: 6px 6px 0px rgba(0, 0, 0, 0.2);
    font-family: 'vcr-osd', monospace;
  }
  
  .scroller-container {
    height: calc(100% - 100px);
    overflow: hidden;
  }
  
  .contributor-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .contributor-card {
    display: flex;
    align-items: center;
    background-color: #2a2a2a;
    padding: 20px 30px;
    box-shadow: 8px 8px 0px rgba(0, 0, 0, 0.2);
    border: 2px solid #444;
    transition: all 0.3s;
    
    &:hover {
      transform: translateX(10px);
      border-color: #de335e;
    }
    
    .rank {
      font-size: 2em;
      font-family: 'vcr-osd', monospace;
      color: #de335e;
      min-width: 80px;
      text-align: center;
    }
    
    .avatar {
      font-size: 3em;
      margin: 0 30px;
    }
    
    .info {
      flex: 1;
      
      .name {
        font-size: 1.5em;
        color: #fff;
        margin-bottom: 8px;
      }
      
      .email {
        font-size: 0.9em;
        color: #999;
      }
    }
    
    .commits {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-left: 30px;
      
      .count {
        font-size: 2.5em;
        font-family: 'vcr-osd', monospace;
        color: #4CAF50;
        font-weight: bold;
      }
      
      .label {
        font-size: 0.9em;
        color: #999;
        margin-top: 5px;
      }
    }
  }
  
  .no-data {
    height: calc(100% - 100px);
    display: flex;
    align-items: center;
    justify-content: center;
    
    p {
      font-size: 1.5em;
      color: #999;
    }
  }
}

// 滑动动画
.slide-enter-active,
.slide-leave-active {
  transition: all 0.5s ease;
}

.slide-enter-from {
  transform: translateY(100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>

