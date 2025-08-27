<script lang="ts">
  import type { Project } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { updateProject, fetchLayers } from '$lib/api';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';
  import type { Layer } from '$lib/types/layer';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import PolygonDrawing from '$lib/components/PolygonDrawing.svelte';
  import { onMount } from 'svelte';

  export let project: Project | null = null;
  let modalRef: HTMLDialogElement;

  let name = '';
  let description = '';
  let polygonData: number[][] = [];
  let selectedLayers: string[] = [];
  let x = 0;
  let y = 0;
  let z = 0;
  let heading = 0;
  let pitch = 0;
  let duration = 0;
  let missingFields: string[] = [];

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

  function resetModal() {
    name = '';
    description = '';
    polygonData = [];
    selectedLayers = [];
    x = 0;
    y = 0;
    z = 0;
    heading = 0;
    pitch = 0;
    duration = 0;
    missingFields = [];
    errorBanner?.hide?.();
    successBanner?.hide?.();
  }

  export function showModal(p: Project) {
    project = p;
    name = p.name || '';
    description = p.description || '';
    // Parse content if it exists
    if (p.content) {
      polygonData = p.content.polygon || [];
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
      polygonData = [];
      selectedLayers = [];
      x = y = z = heading = pitch = duration = 0;
    }
    missingFields = [];
    errorBanner?.hide?.();
    successBanner?.hide?.();
    modalRef.showModal();
  }
  function getMissingRequiredFields(): string[] {
    const requiredFields = [
      { label: 'Naam', value: name },
      { label: 'X-coördinaat', value: x },
      { label: 'Y-coördinaat', value: y },
      { label: 'Z-coördinaat', value: z },
      { label: 'Heading', value: heading },
      { label: 'Pitch', value: pitch },
      { label: 'Duur', value: duration }
    ];
    return requiredFields.filter(field => field.value === '' || field.value === null || (typeof field.value === 'string' && !field.value.trim())).map(field => field.label);
  }

  function handleLayerChange(layerTitle: string, checked: boolean) {
    if (checked) {
      selectedLayers = [...selectedLayers, layerTitle];
    } else {
      selectedLayers = selectedLayers.filter(l => l !== layerTitle);
    }
  }

  function handlePositionUpdate(event: CustomEvent) {
    x = event.detail.x;
    y = event.detail.y;
    z = event.detail.z;
    heading = event.detail.heading;
    pitch = event.detail.pitch;
    duration = event.detail.duration;
  }

  function handlePolygonUpdate(event: CustomEvent) {
    polygonData = [...event.detail];
  }

  function handleCoordinatesSelected(event: CustomEvent) {
    const data = event.detail;
    
    // Update camera coordinates
    x = data.x || 0;
    y = data.y || 0;
    z = data.z || 0;
    heading = data.heading || 0;
    pitch = data.pitch || 0;
    duration = data.duration || 0;
    
    // Update polygon if provided (from PolygonDrawing component)
    if (data.polygon) {
      polygonData = [...data.polygon];
    }
  }

  function handlePolygonSelected(event: CustomEvent) {
    console.log('handlePolygonSelected called with:', event.detail);
    const data = event.detail;
    
    // Update polygon data only
    if (data.polygon) {
      console.log('Updating polygon data with', data.polygon.length, 'points');
      polygonData = [...data.polygon];
    } else {
      console.warn('No polygon data in event');
    }
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!project) return;
    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) return;

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
      content,
      last_updated: new Date().toISOString()
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

  <form 
    on:submit|preventDefault={handleSubmit} 
    class="modal-box grid w-full max-w-4xl max-h-[90vh] grid-cols-4 items-center gap-4 overflow-y-auto"
  >
    <div class="form-control mb2 col-span-4">
      <h3 class="text-lg font-bold">Project bewerken</h3>
      <MissingRequiredFields {missingFields} />
    </div>

    <label for="name" class="pr-4 text-right font-semibold">Naam <span class="text-error">*</span>:</label>
    <input id="name" type="text" class="input input-bordered col-span-3 w-full" bind:value={name} />

    <label for="description" class="pr-4 text-right font-semibold">Beschrijving:</label>
    <input id="description" type="text" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <!-- Camera Position fields -->
    <h4 class="col-span-4 mt-4 font-semibold">Camera Positie</h4>

    <!-- X, Y, Z coordinates row -->
    <label for="x" class="pr-4 text-right font-semibold">Coördinaten (X, Y, Z) <span class="text-error">*</span>:</label>
    <div class="col-span-3 flex gap-2">
      <input id="x" type="number" step="any" class="input input-bordered w-full" bind:value={x} placeholder="X-coördinaat" />
      <input id="y" type="number" step="any" class="input input-bordered w-full" bind:value={y} placeholder="Y-coördinaat" />
      <input id="z" type="number" step="any" class="input input-bordered w-full" bind:value={z} placeholder="Z-coördinaat" />
    </div>

    <!-- Heading, Pitch, Duration row -->
    <label for="heading" class="pr-4 text-right font-semibold">Oriëntatie & Duur <span class="text-error">*</span>:</label>
    <div class="col-span-3 flex gap-2">
      <input id="heading" type="number" step="any" class="input input-bordered w-full" bind:value={heading} placeholder="Heading (graden)" />
      <input id="pitch" type="number" step="any" class="input input-bordered w-full" bind:value={pitch} placeholder="Pitch (graden)" />
      <input id="duration" type="number" step="any" class="input input-bordered w-full" bind:value={duration} placeholder="Duur (seconden)" />
    </div>

    <!-- Camera Position Selection -->
    <div class="pr-4 text-right font-semibold"></div>
    <div class="col-span-3">
      <PositionSelector 
        title="Camera Positie Selecteren"
        buttonText="Selecteer camera positie op kaart"
        initialPosition={{ x, y, z, heading, pitch, duration }}
        on:coordinatesSelected={handleCoordinatesSelected}
      />
    </div>

    <div class="pr-4 text-right font-semibold">Project Gebied:</div>
    <div class="col-span-3">
      {#if polygonData.length > 0}
        <div class="mb-2 p-2 bg-green-50 border border-green-200 rounded">
          <span class="text-sm text-green-700">Polygon getekend met {polygonData.length} punten</span>
        </div>
      {:else}
        <div class="mb-2 p-2 bg-gray-50 border border-gray-200 rounded">
          <span class="text-sm text-gray-600">Geen polygon getekend - gebruik de kaart hieronder</span>
        </div>
      {/if}
      
    <!-- JSON input field for manual polygon editing -->
      <div class="mt-2">
        <label for="polygonJson" class="block text-sm font-medium text-gray-700 mb-1">
          Polygon coördinaten (JSON):
        </label>
        <textarea 
          id="polygonJson"
          class="textarea textarea-bordered w-full h-20 text-xs font-mono"
          placeholder="[[longitude, latitude], [longitude, latitude], ...]"
          value={JSON.stringify(polygonData)}
          on:input={(e) => {
            try {
              const parsed = JSON.parse(e.currentTarget.value);
              if (Array.isArray(parsed)) {
                polygonData = [...parsed];
              }
            } catch (error) {
              // Invalid JSON, ignore
            }
          }}
        ></textarea>
      </div>
    </div>
    
    <!-- Polygon Drawing -->
    <div class="pr-4 text-right font-semibold"></div>
    <div class="col-span-3">
      <PolygonDrawing 
        title="Project Gebied Tekenen"
        buttonText="Teken project gebied op kaart"
        initialPosition={{ x, y, z, heading, pitch, duration }}
        initialPolygon={polygonData}
        on:coordinatesSelected={handlePolygonSelected}
      />
    </div>

    <div class="pr-4 text-right font-semibold">Lagen:</div>
    <div class="col-span-3 max-h-32 overflow-y-auto border border-base-300 rounded-lg p-2">
      {#each availableLayers as layer}
        <label class="flex items-center gap-2 cursor-pointer">
          <input 
            type="checkbox" 
            class="checkbox checkbox-primary"
            checked={selectedLayers.includes(layer.title)}
            on:change={(e) => handleLayerChange(layer.title, e.currentTarget.checked)}
          />
          <span class="text-sm">{layer.title}</span>
        </label>
      {/each}
    </div>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => { modalRef.close(); resetModal(); }}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Bijwerken</button>
    </div>
  </form>
</dialog>