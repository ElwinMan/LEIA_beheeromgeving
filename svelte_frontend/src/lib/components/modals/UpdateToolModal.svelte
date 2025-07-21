<script lang="ts">
  import type { Tool } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { updateTool } from '$lib/api';

  export let tool: Tool | null = null;
  let modalRef: HTMLDialogElement;

  let name = '';
  let content = '';

  const dispatch = createEventDispatcher();

  export function showModal(t: Tool) {
    tool = t;
    name = t.name || '';
    content = t.content ? JSON.stringify(t.content, null, 2) : '';
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!tool) return;

    let payload: any = { name };
    if (content && content.trim() !== '') {
      try {
        payload.content = JSON.parse(content);
      } catch (e) {
        alert('Content moet geldig JSON zijn!');
        return;
      }
    }

    try {
      const updated = await updateTool(String(tool.id), payload);
      dispatch('updated', updated);
      modalRef.close();
    } catch (error) {
      console.error('Update failed', error);
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form on:submit|preventDefault={handleSubmit} class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4">
    <h3 class="col-span-4 mb-4 text-lg font-bold">Tool bewerken</h3>

    <label for="name" class="pr-4 text-right font-semibold">Naam:</label>
    <input id="name" type="text" class="input input-bordered col-span-3 w-full" bind:value={name} required />

    <label for="content" class="pr-4 text-right font-semibold">Content:</label>
    <textarea
      id="content"
      class="textarea textarea-bordered col-span-3 w-full min-h-[12rem]"
      bind:value={content}
      rows="10"
    ></textarea>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>