<script lang="ts">
  import type { Layer } from '$lib/types/layer';
  import { updateLayer } from '$lib/api';
  import { createEventDispatcher } from 'svelte';

  export let layer: Layer | null = null;
  let modalRef: HTMLDialogElement;

  // Local copies of editable fields
  let title = '';
  let type = '';
  let url = '';
  let featureName = '';
  let isBackground = false;

  const dispatch = createEventDispatcher();

  export function showModal(l: Layer) {
    layer = l;
    title = layer.title || '';
    type = layer.type || '';
    url = layer.url || '';
    featureName = layer.featureName || '';
    isBackground = layer.isBackground || false;
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    if (!layer) return;

    try {
      const updated = await updateLayer(String(layer.id), {
        title,
        type,
        url,
        featureName,
        isBackground
      });
      dispatch('updated', updated); // notify parent if needed

      modalRef.close();
    } catch (error) {
      console.error('Update failed', error);
      // Optionally show error to user
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form
    on:submit|preventDefault={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <h3 class="col-span-4 mb-4 text-lg font-bold">Laag details bewerken</h3>

    <label for="title" class="pr-4 text-right font-semibold">Title:</label>
    <input
      id="title"
      type="text"
      class="input input-bordered col-span-3 w-full"
      bind:value={title}
      required
    />

    <label for="type" class="pr-4 text-right font-semibold">Type:</label>
    <input
      id="type"
      type="text"
      class="input input-bordered col-span-3 w-full"
      bind:value={type}
      required
    />

    <label for="url" class="pr-4 text-right font-semibold">URL:</label>
    <input
      id="url"
      type="text"
      class="input input-bordered col-span-3 w-full"
      bind:value={url}
      required
    />

    <label for="featureName" class="pr-4 text-right font-semibold">Feature Name:</label>
    <input
      id="featureName"
      type="text"
      class="input input-bordered col-span-3 w-full"
      bind:value={featureName}
    />

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>
        Annuleren
      </button>
      <button type="submit" class="btn btn-primary"> Opslaan </button>
    </div>
  </form>
</dialog>
