<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createBookmark } from '$lib/api';
  import type { Bookmark } from '$lib/types/tool';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Bookmark }>();

  let title = '';
  let description = '';
  let content = '';

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  const jsonPlaceholder = `{
  "key": "value",
  "anotherKey": 123,
  "array": [
    { "itemKey": "itemValue" }
  ]
}`;

  export function showModal() {
    title = '';
    description = '';
    content = '';
    errorBanner?.hide?.();
    successBanner?.hide?.();
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    let payload: any = { title, description };
    if (content && content.trim() !== '') {
      try {
        payload.content = JSON.parse(content);
      } catch (e) {
        errorBanner?.show();
        return;
      }
    }

    try {
      const newBookmark = await createBookmark(payload);
      dispatch('created', newBookmark);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Bookmark creation failed', error);
    }
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Bookmark succesvol aangemaakt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Content moet geldig JSON zijn!"
  />

  <form
    on:submit|preventDefault={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <h3 class="col-span-4 mb-4 text-lg font-bold">Nieuwe Bookmark Aanmaken</h3>

    <label for="title" class="pr-4 text-right font-semibold">Titel:</label>
    <input id="title" class="input input-bordered col-span-3 w-full" bind:value={title} required />

    <label for="description" class="pr-4 text-right font-semibold">Beschrijving:</label>
    <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <label for="content" class="pr-4 text-right font-semibold">Content (JSON):</label>
    <textarea
      id="content"
      class="textarea textarea-bordered col-span-3 w-full min-h-[12rem]"
      bind:value={content}
      rows="10"
      placeholder={jsonPlaceholder}
    ></textarea>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>