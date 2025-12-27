import { useEffect, useRef, useState } from 'react'

export default function AnimatedCounter({
    end,
    duration = 2000,
    prefix = '',
    suffix = '',
    className = '',
    decimals = 0
}) {
    const [count, setCount] = useState(0)
    const ref = useRef(null)
    const hasAnimated = useRef(false)

    useEffect(() => {
        const element = ref.current
        if (!element) return

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !hasAnimated.current) {
                    hasAnimated.current = true
                    animateCount()
                }
            },
            { threshold: 0.5 }
        )

        observer.observe(element)

        return () => observer.disconnect()
    }, [end])

    const animateCount = () => {
        const startTime = Date.now()
        const startValue = 0

        const animate = () => {
            const elapsed = Date.now() - startTime
            const progress = Math.min(elapsed / duration, 1)

            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3)

            const currentValue = startValue + (end - startValue) * easeOut
            setCount(currentValue)

            if (progress < 1) {
                requestAnimationFrame(animate)
            } else {
                setCount(end)
            }
        }

        requestAnimationFrame(animate)
    }

    const formatNumber = (num) => {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M'
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K'
        }
        return decimals > 0 ? num.toFixed(decimals) : Math.round(num)
    }

    return (
        <span ref={ref} className={className}>
            {prefix}{formatNumber(count)}{suffix}
        </span>
    )
}
