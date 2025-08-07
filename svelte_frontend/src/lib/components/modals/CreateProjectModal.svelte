<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createProject, fetchLayers } from '$lib/api';
  import type { Project } from '$lib/types/tool';
  import type { Layer } from '$lib/types/layer';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import PolygonDrawing from '$lib/components/PolygonDrawing.svelte';
  import { onMount } from 'svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Project }>();

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

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;
  let availableLayers: Layer[] = [];

  onMount(async () => {
    try {
      availableLayers = await fetchLayers();
    } catch (error) {
      console.error('Failed to fetch layers:', error);
    }
  });

  export function showModal() {
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

    const content = {
      polygon: polygonData.length > 0 ? polygonData : null,
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
      const newProject = await createProject(payload);
      dispatch('created', newProject);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Project creation failed', error);
    }
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
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Project succesvol aangemaakt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Er is een fout opgetreden bij het aanmaken van het project!"
  />

  <form
    on:submit|preventDefault={handleSubmit}
    class="modal-box grid w-full max-w-4xl max-h-[90vh] grid-cols-4 items-center gap-4 overflow-y-auto"
  >
    <h3 class="col-span-4 mb-4 text-lg font-bold">Nieuw Project Aanmaken</h3>

    <label for="name" class="pr-4 text-right font-semibold">Naam:</label>
    <input id="name" class="input input-bordered col-span-3 w-full" bind:value={name} required />

    <label for="description" class="pr-4 text-right font-semibold">Beschrijving:</label>
    <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

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
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>