import { useEffect, useRef, useState } from 'react'

export default function ScrollReveal({
    children,
    className = '',
    variant = 'up', // 'up', 'down', 'left', 'right', 'scale'
    delay = 0,
    threshold = 0.1,
    once = true
}) {
    const ref = useRef(null)
    const [isRevealed, setIsRevealed] = useState(false)

    useEffect(() => {
        const element = ref.current
        if (!element) return

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        setIsRevealed(true)
                    }, delay)

                    if (once) {
                        observer.unobserve(element)
                    }
                } else if (!once) {
                    setIsRevealed(false)
                }
            },
            { threshold }
        )

        observer.observe(element)

        return () => observer.disconnect()
    }, [delay, threshold, once])

    const variantClasses = {
        up: 'scroll-reveal',
        down: 'scroll-reveal-down',
        left: 'scroll-reveal-left',
        right: 'scroll-reveal-right',
        scale: 'scroll-reveal-scale',
    }

    return (
        <div
            ref={ref}
            className={`${variantClasses[variant]} ${isRevealed ? 'revealed' : ''} ${className}`}
        >
            {children}
        </div>
    )
}

// Stagger wrapper for multiple children
export function ScrollRevealStagger({
    children,
    className = '',
    staggerDelay = 100
}) {
    const ref = useRef(null)
    const [isRevealed, setIsRevealed] = useState(false)

    useEffect(() => {
        const element = ref.current
        if (!element) return

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsRevealed(true)
                    observer.unobserve(element)
                }
            },
            { threshold: 0.1 }
        )

        observer.observe(element)

        return () => observer.disconnect()
    }, [])

    return (
        <div ref={ref} className={`stagger-children ${className}`}>
            {Array.isArray(children)
                ? children.map((child, index) => (
                    <div
                        key={index}
                        className={`scroll-reveal ${isRevealed ? 'revealed' : ''}`}
                        style={{ transitionDelay: `${index * staggerDelay}ms` }}
                    >
                        {child}
                    </div>
                ))
                : children
            }
        </div>
    )
}
