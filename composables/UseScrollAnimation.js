export function useScrollAnimation() {
  const animateOnScroll = (elements, options = { threshold: 0.2 }) => {
    if (!elements || !elements.length) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('visible')
        })
      },
      options
    )

    elements.forEach(el => observer.observe(el))
  }

  return { animateOnScroll }
}
