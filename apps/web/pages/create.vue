<template>
  <div class="max-w-4xl mx-auto py-8">
    <div v-if="editor" class="mb-4 bg-white border rounded">
      <div class="p-2 border-b flex gap-2">
        <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'bg-gray-200': editor.isActive('bold') }" class="px-2 py-1 border rounded">粗</button>
        <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'bg-gray-200': editor.isActive('italic') }" class="px-2 py-1 border rounded">斜</button>
      </div>
      <editor-content :editor="editor" class="p-4 min-h-[300px]" />
    </div>
    <div class="mt-4">
      <input v-model="title" placeholder="标题" class="w-full p-2 border rounded mb-2">
      <button @click="saveKnowledge" class="px-4 py-2 bg-blue-600 text-white rounded">保存知识</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'

const title = ref('')
const editor = useEditor({
  content: '',
  extensions: [StarterKit],
})

async function saveKnowledge() {
  const content = editor.value?.getHTML()
  await useFetchApi('/knowledge', {
    method: 'POST',
    body: { title: title.value, content: content, space_id: 1 }
  })
  window.location.href = '/'
}
</script>
