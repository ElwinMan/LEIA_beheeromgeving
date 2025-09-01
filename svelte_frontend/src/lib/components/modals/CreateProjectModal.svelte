<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createProject, fetchLayers } from '$lib/api';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';
  import type { Project } from '$lib/types/tool';
  import type { Layer } from '$lib/types/layer';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import PolygonDrawing from '$lib/components/PolygonDrawing.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';
  import { onMount } from 'svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Project }>();

  let name = '';
  let description = '';
  let polygonData: number[][] = [];
  let selectedLayers: string[] = [];
  let activeLayerTab = 0;
  let layerCatalogSearchTerm = '';
  let startPosition = {
    x: 0,
    y: 0,
    z: 0,
    heading: 0,
    pitch: 0,
    duration: 0
  };
  let missingFields: string[] = [];

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

  function resetModal() {
    name = '';
    description = '';
    polygonData = [];
    selectedLayers = [];
    activeLayerTab = 0;
    layerCatalogSearchTerm = '';
    startPosition = {
      x: 0,
      y: 0,
      z: 0,
      heading: 0,
      pitch: 0,
      duration: 0
    };
    missingFields = [];
    errorBanner?.hide?.();
    successBanner?.hide?.();
  }

  export function showModal() {
    resetModal();
    modalRef.showModal();
  }

  function handleLayerChange(layerTitle: string, checked: boolean) {
    if (checked) {
      selectedLayers = [...selectedLayers, layerTitle];
    } else {
      selectedLayers = selectedLayers.filter(l => l !== layerTitle);
    }
  }

  function getMissingRequiredFields(): string[] {
    const requiredFields = [
      { label: 'Naam', value: name },
      { label: 'X-coördinaat', value: startPosition.x },
      { label: 'Y-coördinaat', value: startPosition.y },
      { label: 'Z-coördinaat', value: startPosition.z },
      { label: 'Heading', value: startPosition.heading },
      { label: 'Pitch', value: startPosition.pitch },
      { label: 'Duur', value: startPosition.duration }
    ];
    return requiredFields.filter(field => field.value === '' || field.value === null || (typeof field.value === 'string' && !field.value.toString().trim())).map(field => field.label);
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) return;

    const content = {
      polygon: polygonData.length > 0 ? polygonData : null,
      layers: selectedLayers,
      cameraPosition: { ...startPosition }
    };

    const payload = {
      name,
      description,
      content,
      last_updated: new Date().toISOString()
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
    // Update camera coordinates as a whole object
    startPosition = {
      x: data.x ?? 0,
      y: data.y ?? 0,
      z: data.z ?? 0,
      heading: data.heading ?? 0,
      pitch: data.pitch ?? 0,
      duration: data.duration ?? 0
    };
    // Update polygon if provided (from PositionSelector component)
    if (data.polygon) {
      polygonData = [...data.polygon];
    }
  }

  function handlePolygonSelected(event: CustomEvent) {
    const data = event.detail;
    // Update polygon data only
    if (data.polygon) {
      polygonData = [...data.polygon];
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
    onsubmit={handleSubmit}
    class="modal-box grid w-full max-w-4xl max-h-[90vh] grid-cols-4 items-center gap-4 overflow-y-auto"
  >
    <div class="form-control mb2 col-span-4">
      <h3 class="text-lg font-bold">Nieuw Project Aanmaken</h3>
      <MissingRequiredFields {missingFields} />
    </div>

    <label for="name" class="pr-4 text-right font-semibold">
      Naam <span class="text-error">*</span>:
      <HelpTooltip tip="De naam van het project. Deze moet uniek zijn." position="right" />
    </label>
    <input id="name" class="input input-bordered col-span-3 w-full" bind:value={name} />

    <label for="description" class="pr-4 text-right font-semibold">
      Beschrijving:
      <HelpTooltip tip="Een optionele beschrijving van het project." position="right" />
    </label>
    <input id="description" class="input input-bordered col-span-3 w-full" bind:value={description} />

    <!-- Camera Position fields -->
    <h4 class="col-span-4 mt-4 font-semibold">Camera Positie</h4>

    <!-- Camera Position Selection -->
    <span class="pr-4 text-right font-semibold">
      Camera Positie Selecteren:
      <HelpTooltip tip="Gebruik de kaart om een camera positie te selecteren. Dit vult automatisch de coördinaten in." position="right" />
    </span>
    <div class="col-span-3">
      <PositionSelector 
        title="Camera Positie Selecteren"
        buttonText="Selecteer camera positie op kaart"
        initialPosition={startPosition}
        on:coordinatesSelected={handleCoordinatesSelected}
      />
    </div>

    <!-- X, Y, Z coordinates row with labels above each input -->
    <div></div>
    <div class="col-span-3 flex gap-2">
      <div class="flex flex-col w-full">
        <label for="x" class="block text-xs font-medium mb-1">
          X
          <HelpTooltip tip="X-coördinaat (longitude) van de camera positie." />
        </label>
        <input id="x" type="number" step="any" class="input input-bordered w-full" bind:value={startPosition.x} placeholder="X-coördinaat" />
      </div>
      <div class="flex flex-col w-full">
        <label for="y" class="block text-xs font-medium mb-1">
          Y
          <HelpTooltip tip="Y-coördinaat (latitude) van de camera positie." />
        </label>
        <input id="y" type="number" step="any" class="input input-bordered w-full" bind:value={startPosition.y} placeholder="Y-coördinaat" />
      </div>
      <div class="flex flex-col w-full">
        <label for="z" class="block text-xs font-medium mb-1">
          Z
          <HelpTooltip tip="Z-coördinaat (hoogte) van de camera positie." />
        </label>
        <input id="z" type="number" step="any" class="input input-bordered w-full" bind:value={startPosition.z} placeholder="Z-coördinaat" />
      </div>
    </div>

    <!-- Heading, Pitch, Duration row with labels above each input -->
    <div></div>
    <div class="col-span-3 flex gap-2">
      <div class="flex flex-col w-full">
        <label for="heading" class="block text-xs font-medium mb-1">
          Heading
          <HelpTooltip tip="De richting waarin de camera kijkt (in graden)." />
        </label>
        <input id="heading" type="number" step="any" class="input input-bordered w-full" bind:value={startPosition.heading} placeholder="Heading (graden)" />
      </div>
      <div class="flex flex-col w-full">
        <label for="pitch" class="block text-xs font-medium mb-1">
          Pitch
          <HelpTooltip tip="De kantelhoek van de camera (omhoog/omlaag in graden)." />
        </label>
        <input id="pitch" type="number" step="any" class="input input-bordered w-full" bind:value={startPosition.pitch} placeholder="Pitch (graden)" />
      </div>
      <div class="flex flex-col w-full">
        <label for="duration" class="block text-xs font-medium mb-1">
          Duur
          <HelpTooltip tip="De duur van de camera animatie in seconden." />
        </label>
        <input id="duration" type="number" step="any" class="input input-bordered w-full" bind:value={startPosition.duration} placeholder="Duur (seconden)" />
      </div>
    </div>

    <div class="pr-4 text-right font-semibold">
      Project Gebied:
      <HelpTooltip tip="Het geografische gebied van het project, gedefinieerd als een polygon." position="right" />
    </div>
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
    </div>

    <!-- Polygon Drawing -->
    <span class="pr-4 text-right font-semibold">
      Project Gebied Tekenen:
      <HelpTooltip tip="Gebruik de kaart om een polygon te tekenen die het projectgebied definieert." position="right" />
    </span>
    <div class="col-span-3">
      <PolygonDrawing 
        title="Project Gebied Tekenen"
        buttonText="Teken project gebied op kaart"
        initialPosition={startPosition}
        initialPolygon={polygonData}
        on:coordinatesSelected={handlePolygonSelected}
      />
    </div>

    <!-- JSON input field for manual polygon editing -->
    <span class="pr-4 text-right font-semibold">
      Polygon coördinaten (JSON-array):
      <HelpTooltip tip="Handmatig bewerken van de polygon coördinaten in JSON formaat." position="right" />
    </span>
    <div class="col-span-3">
      <textarea 
        id="polygonJson"
        class="textarea textarea-bordered w-full h-20 text-xs font-mono"
        placeholder="[[longitude, latitude], [longitude, latitude], ...]"
        value={JSON.stringify(polygonData)}
        oninput={(e) => {
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

    <div class="col-span-4">
    <label for="layerCatalogSearch" class="block text-left font-semibold mb-2">
      Lagen:
      <HelpTooltip tip="Selecteer de lagen die deel uitmaken van dit project." position="right" />
    </label>
      <div class="grid grid-cols-5 gap-4" style="min-height: 200px;">
        <!-- Catalogus (left, 2/5) -->
        <div class="col-span-2 border border-base-300 rounded-lg p-2 h-full max-h-64 overflow-y-auto flex flex-col">
          <h5 class="font-semibold mb-2">Catalogus</h5>
          <input
            id="layerCatalogSearch"
            type="text"
            class="input input-bordered w-full mb-2"
            placeholder="Zoek laag..."
            bind:value={layerCatalogSearchTerm}
          />
          <div class="flex-1 overflow-y-auto">
            {#each availableLayers.filter(layer =>
              !selectedLayers.includes(String(layer.id)) &&
              (layerCatalogSearchTerm.trim() === '' || layer.title.toLowerCase().includes(layerCatalogSearchTerm.trim().toLowerCase()))
            ) as layer}
              <div class="flex items-center gap-2 mb-2">
                <span>{layer.title}</span>
                <button type="button" class="btn btn-xs btn-primary" onclick={() => selectedLayers = [...selectedLayers, String(layer.id)]}>+</button>
              </div>
            {/each}
          </div>
        </div>
        <!-- Toegevoegde lagen (right, 3/5) -->
        <div class="col-span-3 border border-base-300 rounded-lg p-2 h-full max-h-64 overflow-y-auto flex flex-col">
          <h5 class="font-semibold mb-2">Toegevoegde lagen</h5>
          <div class="flex-1 overflow-y-auto">
            {#if selectedLayers.length === 0}
              <div class="text-sm text-gray-500">Geen lagen toegevoegd.</div>
            {:else}
              {#each selectedLayers as layerId, i}
                {#if availableLayers.find(l => String(l.id) === layerId)}
                  <div class="flex items-center gap-4 mb-2 w-full">
                    <span class="flex-1 truncate font-medium">{availableLayers.find(l => String(l.id) === layerId)?.title}</span>
                    <button type="button" class="btn btn-xs btn-error" onclick={() => selectedLayers = selectedLayers.filter(l => l !== layerId)} title="Verwijder">x</button>
                  </div>
                {/if}
              {/each}
            {/if}
          </div>
        </div>
      </div>
    </div>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" onclick={() => { modalRef.close(); resetModal(); }}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>