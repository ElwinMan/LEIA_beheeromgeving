<script lang="ts">
  import type { Project } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { updateProject, fetchLayers } from '$lib/api';
  import type { Layer } from '$lib/types/layer';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import { onMount } from 'svelte';

  export let project: Project | null = null;
  let modalRef: HTMLDialogElement;

  let name = '';
  let description = '';
  let polygon = '';
  let selectedLayers: string[] = [];
  let x = 0;
  let y = 0;
  let z = 0;
  let heading = 0;
  let pitch = 0;
  let duration = 0;

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let availableLayers: Layer[] = [];

  const dispatch = createEventDispatcher();

  onMount(async () => {
    try {
      availableLayers = await fetchLayers();
    } catch (error) {
      console.error('Failed to fetch layers:', error);
    }
  });

  export function showModal(p: Project) {
    project = p;
    name = p.name || '';
    description = p.description || '';
    
    // Parse content if it exists
    if (p.content) {
      polygon = p.content.polygon ? JSON.stringify(p.content.polygon, null, 2) : '';
      selectedLayers = p.content.layers || [];
      if (p.content.cameraPosition) {
        x = p.content.cameraPosition.x || 0;
        y = p.content.cameraPosition.y || 0;
        z = p.content.cameraPosition.z || 0;
        heading = p.content.cameraPosition.heading || 0;
        pitch = p.content.cameraPosition.pitch || 0;
        duration = p.content.cameraPosition.duration || 0;
      } else {
        x = y = z = heading = pitch = duration = 0;
      }
    } else {
      polygon = '';
      selectedLayers = [];
      x = y = z = heading = pitch = duration = 0;
    }
    
    errorBanner?.hide?.();
    successBanner?.hide?.();
    modalRef.showModal();
  }

  function handleLayerChange(layerTitle: string, checked: boolean) {
    if (checked) {
      selectedLayers = [...selectedLayers, layerTitle];
    } else {
      selectedLayers = selectedLayers.filter(l => l !== layerTitle);
    }
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!project) return;

    let polygonData;
    try {
      if (polygon.trim()) {
        polygonData = JSON.parse(polygon);
      }
    } catch (error) {
      errorBanner?.show();
      console.error('Invalid polygon JSON:', error);
      return;
    }

    const content = {
      polygon: polygonData,
      layers: selectedLayers,
      cameraPosition: {
        x,
        y,
        z,
        heading,
        pitch,
        duration
      }
    };

    const payload = {
      name,
      description,
      content
    };

    try {
      const updated = await updateProject(String(project.id), payload);
      dispatch('updated', updated);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Update failed', error);
    }
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Project succesvol bijgewerkt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Er is een fout opgetreden bij het bijwerken van het project!"
  />

  <form on:submit|preventDefault={handleSubmit} class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4">
    <h3 class="col-span-4 mb-4 text-lg font-bold">Project bewerken</h3>

    <label for="name" class="pr-4 text-right font-semibold">Naam:</label>
    <input id="name" type="text" class="input input-bordered col-span-3 w-full" bind:value={name} required />

    <label for="description" class="pr-4 text-right font-semibold">Beschrijving:</label>
    <input id="description" type="text" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <label for="polygon" class="pr-4 text-right font-semibold">Polygon (JSON):</label>
    <textarea 
      id="polygon" 
      class="textarea textarea-bordered col-span-3 w-full h-32" 
      bind:value={polygon} 
      placeholder='[
  [4.9000, 52.39961],
  [4.91807, 52.39961],
  [4.9193, 52.38107],
  [4.9000, 52.38575]
]'
    ></textarea>

    <div class="pr-4 text-right font-semibold">Lagen:</div>
    <div class="col-span-3 max-h-32 overflow-y-auto border border-base-300 rounded-lg p-2">
      {#each availableLayers as layer}
        <label class="flex items-center gap-2 cursor-pointer">
          <input 
            type="checkbox" 
            class="checkbox checkbox-sm"
            checked={selectedLayers.includes(layer.title)}
            on:change={(e) => handleLayerChange(layer.title, e.currentTarget.checked)}
          />
          <span class="text-sm">{layer.title}</span>
        </label>
      {/each}
    </div>

    <!-- Camera Position fields -->
    <h4 class="col-span-4 mt-4 font-semibold">Camera Positie</h4>

    <!-- X, Y, Z coordinates row -->
    <label for="x" class="pr-4 text-right font-semibold">Coördinaten (X, Y, Z):</label>
    <div class="col-span-3 flex gap-2">
      <input id="x" type="number" step="any" class="input input-bordered w-full" bind:value={x} required placeholder="X-coördinaat" />
      <input id="y" type="number" step="any" class="input input-bordered w-full" bind:value={y} required placeholder="Y-coördinaat" />
      <input id="z" type="number" step="any" class="input input-bordered w-full" bind:value={z} required placeholder="Z-coördinaat" />
    </div>

    <!-- Heading, Pitch, Duration row -->
    <label for="heading" class="pr-4 text-right font-semibold">Oriëntatie & Duur:</label>
    <div class="col-span-3 flex gap-2">
      <input id="heading" type="number" step="any" class="input input-bordered w-full" bind:value={heading} required placeholder="Heading (graden)" />
      <input id="pitch" type="number" step="any" class="input input-bordered w-full" bind:value={pitch} required placeholder="Pitch (graden)" />
      <input id="duration" type="number" step="any" class="input input-bordered w-full" bind:value={duration} required placeholder="Duur (seconden)" />
    </div>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>