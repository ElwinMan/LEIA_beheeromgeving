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
        isBackground,
      }
	);
    dispatch('updated', updated); // notify parent if needed

      modalRef.close();
    } catch (error) {
      console.error('Update failed', error);
      // Optionally show error to user
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
	<form on:submit|preventDefault={handleSubmit} class="modal-box w-full max-w-4xl grid grid-cols-4 gap-4 items-center">
		<h3 class="col-span-4 text-lg font-bold mb-4">Laag details bewerken</h3>

		<label for="title" class="text-right pr-4 font-semibold">Title:</label>
		<input id="title" type="text" class="input input-bordered w-full col-span-3" bind:value={title} required/>

		<label for="type" class="text-right pr-4 font-semibold">Type:</label>
		<input id="type" type="text" class="input input-bordered w-full col-span-3" bind:value={type} required/>

		<label for="url" class="text-right pr-4 font-semibold">URL:</label>
		<input id="url" type="text" class="input input-bordered w-full col-span-3" bind:value={url} required/>

		<label for="featureName" class="text-right pr-4 font-semibold">Feature Name:</label>
		<input id="featureName" type="text" class="input input-bordered w-full col-span-3" bind:value={featureName} />

		<label for="isBackground" class="text-right pr-4 font-semibold">Achtergrond:</label>
		<input id="isBackground" type="checkbox" class="checkbox checkbox-primary" bind:checked={isBackground} />

		<div class="col-span-4 mt-6 flex justify-end gap-2">
			<button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>
			Annuleren
			</button>
			<button type="submit" class="btn btn-primary">
			Opslaan
			</button>
		</div>
	</form>
</dialog>