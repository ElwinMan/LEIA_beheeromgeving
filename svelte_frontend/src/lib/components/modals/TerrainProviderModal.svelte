<script lang="ts">
  import type { TerrainProvider } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  // You need to implement updateTerrainProvider in your api.ts
  import { updateTerrainProvider } from '$lib/api';

  export let terrainProvider: TerrainProvider | null = null;
  let modalRef: HTMLDialogElement;

  let title = '';
  let url = '';
  let vertexNormals = false;

  const dispatch = createEventDispatcher();

  export function showModal(tp: TerrainProvider) {
    terrainProvider = tp;
    title = tp.title || '';
    url = tp.url || '';
    vertexNormals = !!tp.vertexNormals;
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!terrainProvider) return;

    try {
      const updated = await updateTerrainProvider(String(terrainProvider.id), {
        title,
        url,
        vertexNormals
      });
      dispatch('updated', updated);
      modalRef.close();
    } catch (error) {
      console.error('Update failed', error);
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form
    on:submit|preventDefault={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <h3 class="col-span-4 mb-4 text-lg font-bold">Terrain Provider bewerken</h3>

    <label for="title" class="pr-4 text-right font-semibold">Title:</label>
    <input
      id="title"
      type="text"
      class="input input-bordered col-span-3 w-full"
      bind:value={title}
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

    <label for="vertexNormals" class="pr-4 text-right font-semibold">Vertex Normals:</label>
    <input
      id="vertexNormals"
      type="checkbox"
      class="checkbox"
      bind:checked={vertexNormals}
    />

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>
        Annuleren
      </button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>