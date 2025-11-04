declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'chart.xkcd' {
  export const Bar: any
  export const Pie: any
  export default {
    Bar: any
    Pie: any
  }
}

