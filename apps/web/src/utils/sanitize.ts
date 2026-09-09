const ALLOWED_TAGS = new Set([
  'a', 'abbr', 'b', 'blockquote', 'br', 'code', 'del', 'em', 'h1', 'h2', 'h3', 'h4',
  'hr', 'i', 'li', 'ol', 'p', 'pre', 's', 'strong', 'sub', 'sup', 'table', 'tbody',
  'td', 'th', 'thead', 'tr', 'u', 'ul'
])
const ALLOWED_ATTRIBUTES = new Set([
  'aria-label', 'class', 'colspan', 'href', 'id', 'rel', 'role', 'rowspan', 'start',
  'target', 'title'
])

function safeUrl(value: string): boolean {
  const normalized = value.trim().toLowerCase()
  return normalized.startsWith('/') || normalized.startsWith('#') ||
    normalized.startsWith('./') || normalized.startsWith('../') ||
    normalized.startsWith('https://') || normalized.startsWith('http://') ||
    normalized.startsWith('mailto:')
}

/** Browser-side allowlist sanitizer for imported HTML and Markdown output. */
export function sanitizeHtml(input: string): string {
  if (typeof DOMParser === 'undefined') return input.replace(/[<>]/g, (char) => char === '<' ? '&lt;' : '&gt;')
  const document = new DOMParser().parseFromString(input, 'text/html')
  const walk = (root: ParentNode) => {
    Array.from(root.childNodes).forEach((node) => {
      if (node.nodeType === Node.ELEMENT_NODE) {
        const element = node as HTMLElement
        if (!ALLOWED_TAGS.has(element.tagName.toLowerCase())) {
          if (['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT', 'EMBED', 'SVG', 'MATH'].includes(element.tagName)) {
            element.remove()
            return
          }
          const fragment = document.createDocumentFragment()
          while (element.firstChild) fragment.appendChild(element.firstChild)
          element.replaceWith(fragment)
          walk(root)
          return
        }
        Array.from(element.attributes).forEach((attribute) => {
          const name = attribute.name.toLowerCase()
          if (name.startsWith('on') || !ALLOWED_ATTRIBUTES.has(name) ||
              (name === 'href' && !safeUrl(attribute.value))) {
            element.removeAttribute(attribute.name)
          }
        })
        if (element.tagName === 'A' && element.getAttribute('target') === '_blank') {
          element.setAttribute('rel', 'noopener noreferrer')
        }
        walk(element)
      } else if (node.nodeType === Node.COMMENT_NODE) {
        node.remove()
      }
    })
  }
  walk(document.body)
  return document.body.innerHTML
}
