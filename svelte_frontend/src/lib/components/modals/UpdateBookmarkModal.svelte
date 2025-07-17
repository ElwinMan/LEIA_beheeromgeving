<script lang="ts">
  import type { Bookmark } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { updateBookmark } from '$lib/api';

  export let bookmark: Bookmark | null = null;
  let modalRef: HTMLDialogElement;

  let title = '';
  let description = '';
  let content = '';

  const dispatch = createEventDispatcher();

  export function showModal(b: Bookmark) {
    bookmark = b;
    title = b.title || '';
    description = b.description || '';
    content = b.content || '';
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!bookmark) return;

    try {
      const updated = await updateBookmark(String(bookmark.id), {
        title,
        description,
        content
      });
      dispatch('updated', updated);
      modalRef.close();
    } catch (error) {
      console.error('Update failed', error);
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form on:submit|preventDefault={handleSubmit} class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4">
    <h3 class="col-span-4 mb-4 text-lg font-bold">Bookmark bewerken</h3>

    <label for="title" class="pr-4 text-right font-semibold">Titel:</label>
    <input id="title" type="text" class="input input-bordered col-span-3 w-full" bind:value={title} required />

    <label for="description" class="pr-4 text-right font-semibold">Beschrijving:</label>
    <input id="description" type="text" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <label for="content" class="pr-4 text-right font-semibold">Content:</label>
    <textarea id="content" class="textarea textarea-bordered col-span-3 w-full" bind:value={content}></textarea>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>