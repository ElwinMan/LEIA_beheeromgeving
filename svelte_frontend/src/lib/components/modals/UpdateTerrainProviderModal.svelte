<script lang="ts">
  import type { TerrainProvider } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { updateTerrainProvider } from '$lib/api';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';

  export let terrainProvider: TerrainProvider | null = null;
  let modalRef: HTMLDialogElement;

  let title = '';
  let url = '';
  let vertexNormals = false;

  const dispatch = createEventDispatcher();

  let missingFields: string[] = [];

  function resetModal() {
    title = '';
    url = '';
    vertexNormals = false;
    missingFields = [];
  }

  export function showModal(tp: TerrainProvider) {
    terrainProvider = tp;
    title = tp.title || '';
    url = tp.url || '';
    vertexNormals = !!tp.vertexNormals;
    missingFields = [];
    modalRef.showModal();
  }

  function getMissingRequiredFields(): string[] {
    const fields: { label: string; value: any }[] = [
      { label: 'Title', value: title },
      { label: 'URL', value: url }
    ];
    return fields.filter(f => !f.value || (typeof f.value === 'string' && !f.value.trim())).map(f => f.label);
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!terrainProvider) return;

    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) return;

    try {
      const updated = await updateTerrainProvider(String(terrainProvider.id), {
        title,
        url,
        vertexNormals,
        last_updated: new Date().toISOString()
      });
      dispatch('updated', updated);
      modalRef.close();
      resetModal();
    } catch (error) {
      console.error('Update failed', error);
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form
    onsubmit={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <div class="form-control mb2 col-span-4">
      <h3 class="mb-4 text-lg font-bold">Terrain Provider bewerken</h3>
      <MissingRequiredFields {missingFields} />
    </div>

    <label for="title" class="pr-4 text-right font-semibold">
      Title <span class="text-error">*</span>:
      <HelpTooltip tip="De naam van de terrain provider." position="right" />
    </label>
    <input
      id="title"
      type="text"
      class="input input-bordered col-span-3 w-full"
      bind:value={title}
    />

    <label for="url" class="pr-4 text-right font-semibold">
      URL <span class="text-error">*</span>:
      <HelpTooltip tip="De URL van de terrain provider service. Dit is het endpoint waar de terrein data wordt opgehaald." position="right" />
    </label>
    <input
      id="url"
      type="text"
      class="input input-bordered col-span-3 w-full"
      bind:value={url}
    />

    <label for="vertexNormals" class="pr-4 text-right font-semibold">
      Vertex Normals:
      <HelpTooltip tip="Bepaalt of vertex normals worden gebruikt voor de terrain rendering." position="right" />
    </label>
    <input
      id="vertexNormals"
      type="checkbox"
      class="checkbox checkbox-primary"
      bind:checked={vertexNormals}
    />

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" onclick={() => { modalRef.close(); resetModal(); }}>
        Annuleren
      </button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>