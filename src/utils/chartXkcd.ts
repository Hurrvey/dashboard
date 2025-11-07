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
  legendScale?: number
  legendFontSize?: number
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

const SVG_NS = 'http://www.w3.org/2000/svg'

const LEGEND_SCALE_ATTR = 'data-legend-orig-'

const cacheNumericAttr = (element: Element, attr: string): number | null => {
  const cacheAttr = `${LEGEND_SCALE_ATTR}${attr}`
  let value = element.getAttribute(cacheAttr)
  if (value === null) {
    value = element.getAttribute(attr)
    if (value === null) {
      return null
    }
    element.setAttribute(cacheAttr, value)
  }

  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : null
}

const setScaledAttr = (element: Element, attr: string, scale: number, override?: number | null) => {
  const original = cacheNumericAttr(element, attr)
  if (original === null) {
    return
  }

  const value = override ?? original * scale
  element.setAttribute(attr, Number.isFinite(value) ? value.toFixed(2).replace(/\.00$/, '') : String(value))
}

const cacheFontSize = (element: SVGTextElement): number | null => {
  const cacheAttr = `${LEGEND_SCALE_ATTR}font-size`
  let value = element.getAttribute(cacheAttr)
  if (value === null) {
    const styleValue = element.style.fontSize || element.getAttribute('font-size') || element.getAttribute('style')?.match(/font-size:\s*([0-9.]+)/)?.[1]
    if (!styleValue) {
      return null
    }
    value = styleValue
    element.setAttribute(cacheAttr, value)
  }

  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : null
}

const findLegendSvg = (container: HTMLElement): SVGElement | null => {
  const svgElements = Array.from(container.querySelectorAll('svg')) as SVGElement[]
  for (const svg of svgElements.reverse()) {
    if (svg.querySelector('rect[fill-opacity]')) {
      return svg
    }
  }
  return null
}

const applyLegendEnhancements = (container: HTMLElement | null, options?: PatchedOptions) => {
  if (!container || !options) {
    return
  }

  const legendScale = Number(options.legendScale ?? 1)
  const legendFontSize = Number(options.legendFontSize ?? 0)

  if (legendScale === 1 && legendFontSize <= 0) {
    return
  }

  const legendRoot = findLegendSvg(container)
  if (!legendRoot) {
    return
  }

  const previousScale = Number(legendRoot.getAttribute('data-legend-applied-scale') ?? '0')
  const previousFont = Number(legendRoot.getAttribute('data-legend-applied-font') ?? '0')
  if (previousScale === legendScale && (legendFontSize <= 0 || previousFont === legendFontSize)) {
    return
  }

  const backgroundRect = legendRoot.querySelector('rect[fill-opacity]') as SVGRectElement | null
  if (!backgroundRect) {
    return
  }

  const colorRects = Array.from(legendRoot.querySelectorAll('rect')).filter(rect => rect !== backgroundRect)
  const texts = Array.from(legendRoot.querySelectorAll('text')) as SVGTextElement[]

  colorRects.forEach(rect => {
    setScaledAttr(rect, 'width', legendScale)
    setScaledAttr(rect, 'height', legendScale)
    setScaledAttr(rect, 'x', legendScale)
    setScaledAttr(rect, 'y', legendScale)
    setScaledAttr(rect, 'rx', legendScale)
    setScaledAttr(rect, 'ry', legendScale)
  })

  texts.forEach(text => {
    setScaledAttr(text, 'x', legendScale)
    setScaledAttr(text, 'y', legendScale)

    const originalFontSize = cacheFontSize(text)
    if (originalFontSize !== null) {
      const value = legendFontSize > 0 ? legendFontSize : originalFontSize * legendScale
      text.style.setProperty('font-size', `${value}px`, 'important')
    }
  })

  setScaledAttr(backgroundRect, 'width', legendScale)
  setScaledAttr(backgroundRect, 'height', legendScale)
  setScaledAttr(backgroundRect, 'x', legendScale)
  setScaledAttr(backgroundRect, 'y', legendScale)
  setScaledAttr(backgroundRect, 'rx', legendScale)
  setScaledAttr(backgroundRect, 'ry', legendScale)
  setScaledAttr(backgroundRect, 'stroke-width', legendScale)

  const originalBackgroundWidth = cacheNumericAttr(backgroundRect, 'width') ?? 0
  const originalBackgroundHeight = cacheNumericAttr(backgroundRect, 'height') ?? 0
  const newBackgroundWidth = Number(backgroundRect.getAttribute('width') ?? originalBackgroundWidth)
  const newBackgroundHeight = Number(backgroundRect.getAttribute('height') ?? originalBackgroundHeight)

  const originalX = cacheNumericAttr(legendRoot, 'x') ?? 0
  const originalY = cacheNumericAttr(legendRoot, 'y') ?? 0

  const alignedRight = Math.abs(originalX) > 0.1
  const alignedBottom = Math.abs(originalY) > 0.1

  if (alignedRight) {
    const newX = originalX + originalBackgroundWidth - newBackgroundWidth
    legendRoot.setAttribute('x', newX.toFixed(2).replace(/\.00$/, ''))
  }

  if (alignedBottom) {
    const newY = originalY + originalBackgroundHeight - newBackgroundHeight
    legendRoot.setAttribute('y', newY.toFixed(2).replace(/\.00$/, ''))
  }

  legendRoot.setAttribute('data-legend-applied-scale', legendScale.toString())
  if (legendFontSize > 0) {
    legendRoot.setAttribute('data-legend-applied-font', legendFontSize.toString())
  }
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

    if (container) {
      window.requestAnimationFrame(() => {
        applyLegendEnhancements(container, this.options as PatchedOptions)
      })
    }

    return result
  }

  proto.__fullSizePiePatched__ = true
}

ensurePiePatched()

export default chartXkcd

