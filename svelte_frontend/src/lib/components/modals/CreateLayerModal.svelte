<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createLayer } from '$lib/api';
  import type { Layer } from '$lib/types/layer';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Layer }>();

  let title = '';
  let type = '';
  let url = '';
  let featureName = '';
  let isBackground = false;

  export let isBackgroundPage: boolean = false;

  export function showModal() {
    resetForm();
    modalRef?.showModal();
  }

  function resetForm() {
    title = '';
    type = '';
    url = '';
    featureName = '';
    isBackground = isBackgroundPage;
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    try {
      const newLayer = await createLayer({
        title,
        type,
        url,
        featureName,
        isBackground
      });

      dispatch('created', newLayer);
      modalRef.close();
    } catch (error) {
      console.error('Layer creation failed', error);
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form
    on:submit|preventDefault={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <h3 class="col-span-4 mb-4 text-lg font-bold">Nieuwe Layer Aanmaken</h3>

    <label for="title" class="pr-4 text-right font-semibold">Title:</label>
    <input id="title" class="input input-bordered col-span-3 w-full" bind:value={title} required />

    <label for="type" class="pr-4 text-right font-semibold">Type:</label>
    <input id="type" class="input input-bordered col-span-3 w-full" bind:value={type} required />

    <label for="url" class="pr-4 text-right font-semibold">URL:</label>
    <input id="url" class="input input-bordered col-span-3 w-full" bind:value={url} required />

    <label for="featureName" class="pr-4 text-right font-semibold">Feature Name:</label>
    <input id="featureName" class="input input-bordered col-span-3 w-full" bind:value={featureName} />

    <label for="isBackground" class="text-right font-semibold">Is Background:</label>
    <input
      type="checkbox"
      class="checkbox col-span-3 checkbox-primary"
      bind:checked={isBackground}
      disabled
    />

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>