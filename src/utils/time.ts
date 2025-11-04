/**
 * 格式化时间
 */
export function formatTime(date: Date): string {
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

/**
 * 获取当前时间字符串
 */
export function getCurrentTimeString(): string {
  return formatTime(new Date())
}

