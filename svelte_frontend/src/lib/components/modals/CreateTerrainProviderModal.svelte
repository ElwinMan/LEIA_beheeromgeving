<script lang="ts">
  import type { TerrainProvider } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { createTerrainProvider } from '$lib/api';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: TerrainProvider }>();

  let title = '';
  let url = '';
  let vertexNormals = false;

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  export function showModal() {
    title = '';
    url = '';
    vertexNormals = false;
    errorBanner?.hide?.();
    successBanner?.hide?.();
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    try {
      const newTerrainProvider = await createTerrainProvider({
        title,
        url,
        vertexNormals
      });
      dispatch('created', newTerrainProvider);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('TerrainProvider creation failed', error);
    }
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="TerrainProvider succesvol aangemaakt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Aanmaken mislukt!"
  />

  <form
    on:submit|preventDefault={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <h3 class="col-span-4 mb-4 text-lg font-bold">Nieuwe Terrain Provider Aanmaken</h3>

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
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>