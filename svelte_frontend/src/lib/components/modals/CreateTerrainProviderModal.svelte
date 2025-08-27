<script lang="ts">
  import type { TerrainProvider } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { createTerrainProvider } from '$lib/api';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: TerrainProvider }>();

  let title = '';
  let url = '';
  let vertexNormals = false;

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  let missingFields: string[] = [];

  function resetModal() {
    title = '';
    url = '';
    vertexNormals = false;
    missingFields = [];
    errorBanner?.hide?.();
    successBanner?.hide?.();
  }

  export function showModal() {
    resetModal();
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
    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) return;

    try {
      const newTerrainProvider = await createTerrainProvider({
        title,
        url,
        vertexNormals,
        last_updated: new Date().toISOString()
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
    onsubmit={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <div class="form-control mb2 col-span-4">
      <h3 class="mb-4 text-lg font-bold">Nieuwe Terrain Provider Aanmaken</h3>
      <MissingRequiredFields {missingFields} />
    </div>

    <label for="title" class="pr-4 text-right font-semibold">Title <span class="text-error">*</span>:</label>
    <input
      id="title"
      type="text"
      class="input input-bordered col-span-3 w-full"
      bind:value={title}
    />

    <label for="url" class="pr-4 text-right font-semibold">URL <span class="text-error">*</span>:</label>
    <input
      id="url"
      type="text"
      class="input input-bordered col-span-3 w-full"
      bind:value={url}
    />

    <label for="vertexNormals" class="pr-4 text-right font-semibold">Vertex Normals:</label>
    <input
      id="vertexNormals"
      type="checkbox"
      class="checkbox"
      bind:checked={vertexNormals}
    />

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" onclick={() => { modalRef.close(); resetModal(); }}>
        Annuleren
      </button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>