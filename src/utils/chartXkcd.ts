import chartXkcd from 'chart.xkcd'

type MarginConfig = {
  top?: number
  right?: number
  bottom?: number
  left?: number
}

interface PatchedOptions {
  chartMargins?: MarginConfig
  margins?: MarginConfig
}

type AnyChart = {
  svgEl?: {
    attr: (name: string, value?: any) => any
    node?: () => SVGSVGElement | null
  }
  chart?: {
    attr: (name: string, value?: any) => any
  }
  width: number
  height: number
  options?: PatchedOptions
  render?: (...args: any[]) => any
}

const extractTranslate = (transform: string | undefined | null) => {
  if (!transform) return { x: 0, y: 0 }
  const match = transform.match(/translate\(([^,]+),\s*([^)]+)\)/)
  if (!match) return { x: 0, y: 0 }
  const [, x, y] = match
  return {
    x: Number.parseFloat(x) || 0,
    y: Number.parseFloat(y) || 0,
  }
}

const ensurePatched = () => {
  const proto = chartXkcd.Bar?.prototype as AnyChart & { __fullSizePatched__?: boolean }
  if (!proto || proto.__fullSizePatched__) {
    return
  }

  const originalRender = proto.render as (...args: any[]) => any

  proto.render = function patchedRender(this: AnyChart, ...args: any[]) {
    const svgSelection = this.svgEl as AnyChart['svgEl']
    const chartSelection = this.chart as AnyChart['chart']

    if (svgSelection && svgSelection.node && chartSelection && chartSelection.attr) {
      const svgNode = svgSelection.node?.()
      const container = svgNode?.parentElement ?? null

      const declaredWidth = Number(svgSelection.attr('width')) || 0
      const declaredHeight = Number(svgSelection.attr('height')) || 0

      const desiredWidth = container?.clientWidth || declaredWidth
      const desiredHeight = container?.clientHeight || declaredHeight || (desiredWidth ? (desiredWidth * 2) / 3 : 0)

      const translation = extractTranslate(chartSelection.attr('transform') as unknown as string)

      const totalHorizontalMargin = declaredWidth > 0 ? declaredWidth - this.width : translation.x * 2
      const totalVerticalMargin = declaredHeight > 0 ? declaredHeight - this.height : translation.y * 2

      const currentRight = totalHorizontalMargin - translation.x
      const currentBottom = totalVerticalMargin - translation.y

      const marginOption: MarginConfig | undefined = this.options?.chartMargins || this.options?.margins

      const margins = {
        left: marginOption?.left ?? translation.x,
        right: marginOption?.right ?? currentRight,
        top: marginOption?.top ?? translation.y,
        bottom: marginOption?.bottom ?? currentBottom,
      }

      const safeWidth = Math.max(desiredWidth, 0)
      const safeHeight = Math.max(desiredHeight, 0)

      const usableWidth = Math.max(safeWidth - (margins.left + margins.right), 10)
      const usableHeight = Math.max(safeHeight - (margins.top + margins.bottom), 10)

      svgSelection.attr('width', safeWidth)
      svgSelection.attr('height', safeHeight)
      chartSelection.attr('transform', `translate(${margins.left},${margins.top})`)

      this.width = usableWidth
      this.height = usableHeight
    }

    return originalRender.apply(this, args)
  }

  proto.__fullSizePatched__ = true
}

ensurePatched()

const ensurePiePatched = () => {
  const proto = chartXkcd.Pie?.prototype as AnyChart & { __fullSizePiePatched__?: boolean }
  if (!proto || proto.__fullSizePiePatched__) {
    return
  }

  const originalRender = proto.render as (...args: any[]) => any
  if (typeof originalRender !== 'function') {
    return
  }

  proto.render = function patchedPieRender(this: AnyChart, ...args: any[]) {
    const svgSelection = this.svgEl as AnyChart['svgEl']
    const chartSelection = this.chart as AnyChart['chart']

    const marginOption: MarginConfig | undefined = this.options?.chartMargins || this.options?.margins
    const marginLeft = marginOption?.left ?? 0
    const marginRight = marginOption?.right ?? 0
    const marginTop = marginOption?.top ?? 0
    const marginBottom = marginOption?.bottom ?? 0

    let safeWidth = 0
    let safeHeight = 0

    const svgNode = svgSelection?.node?.() ?? null
    const container = svgNode?.parentElement ?? null

    const declaredWidth = Number(svgSelection?.attr?.('width')) || 0
    const declaredHeight = Number(svgSelection?.attr?.('height')) || 0

    if (container?.clientWidth) {
      safeWidth = container.clientWidth
    } else if (declaredWidth) {
      safeWidth = declaredWidth
    }

    if (container?.clientHeight) {
      safeHeight = container.clientHeight
    } else if (declaredHeight) {
      safeHeight = declaredHeight
    }

    if (!safeWidth) {
      safeWidth = Math.max(this.width + marginLeft + marginRight, 1)
    }

    if (!safeHeight) {
      safeHeight = safeWidth
    }

    safeWidth = Math.max(safeWidth, 1)
    safeHeight = Math.max(safeHeight, 1)

    const availableWidth = Math.max(safeWidth - (marginLeft + marginRight), 10)
    const availableHeight = Math.max(safeHeight - (marginTop + marginBottom), 10)
    const innerSize = Math.max(Math.min(availableWidth, availableHeight), 10)

    this.width = innerSize
    this.height = innerSize

    if (svgSelection?.attr) {
      svgSelection.attr('width', safeWidth)
      svgSelection.attr('height', safeHeight)
    }

    svgNode?.setAttribute('viewBox', `0 0 ${safeWidth} ${safeHeight}`)

    const result = originalRender.apply(this, args)

    if (chartSelection?.attr) {
      const translateX = marginLeft + innerSize / 2
      const translateY = marginTop + innerSize / 2
      chartSelection.attr('transform', `translate(${translateX},${translateY})`)
    }

    return result
  }

  proto.__fullSizePiePatched__ = true
}

ensurePiePatched()

export default chartXkcd

