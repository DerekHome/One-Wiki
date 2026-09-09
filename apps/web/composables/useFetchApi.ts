import type { UseFetchOptions } from 'nuxt/app'

export function useFetchApi<T>(url: string, options: UseFetchOptions<T> = {}) {
  const config = useRuntimeConfig()
  return useFetch(url, {
    ...options,
    baseURL: config.public.apiBase as string,
  })
}
