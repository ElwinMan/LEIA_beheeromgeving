<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { 
    Viewer,
    Cartographic, 
    Ellipsoid,
    Math as CesiumMath
  } from 'cesium';
  import CesiumBaseMap from './CesiumBaseMap.svelte';

  export let title = 'Selecteer Positie';
  export let buttonText = 'Selecteer positie op kaart';
  export let initialPosition: {
    x?: number;
    y?: number;
    z?: number;
    heading?: number;
    pitch?: number;
    roll?: number;
    duration?: number;
  } | null = null;

  const dispatch = createEventDispatcher();

  let isVisible = false;
  let viewer: Viewer | null = null;
  let cesiumBaseMap: CesiumBaseMap;

  function handleViewerReady(event: CustomEvent) {
    viewer = event.detail.viewer;
  }

  function handleClose() {
    isVisible = false;
    dispatch('close');
  }

  function handleOpen() {
    isVisible = true;
  }

  function handleSaveCurrentView() {
    if (!viewer) return;

    try {
      // Get current camera position
      const camera = viewer.camera;
      const position = camera.position;
      
      const cartographic = Cartographic.fromCartesian(position, Ellipsoid.WGS84);
      const longitude = CesiumMath.toDegrees(cartographic.longitude);
      const latitude = CesiumMath.toDegrees(cartographic.latitude);
      const height = cartographic.height;

      const heading = CesiumMath.toDegrees(camera.heading);
      const pitch = CesiumMath.toDegrees(camera.pitch);
      const roll = CesiumMath.toDegrees(camera.roll);

      const currentDuration = initialPosition?.duration ?? 0;
      const duration = currentDuration === 0 ? 2.0 : currentDuration;

      const result = {
        longitude,
        latitude,
        height,
        heading,
        pitch,
        roll,
        x: longitude,
        y: latitude,
        z: height,
        duration
      };

      dispatch('coordinatesSelected', result);
      isVisible = false;
    } catch (error) {
      console.error('Error capturing current view:', error);
    }
  }
</script>

<!-- Button to open position selector -->
<button 
  type="button"
  class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-sm font-medium transition-colors shadow-sm"
  on:click={handleOpen}
>
  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
  </svg>
  {buttonText}
</button>

<!-- Modal backdrop -->
{#if isVisible}
  <div 
    class="fixed inset-0 bg-black/50 flex justify-center items-center z-[9999]" 
    on:click={handleClose} 
    on:keydown 
    role="presentation"
  >
    <div class="bg-white rounded-lg w-[90%] max-w-4xl h-[80%] max-h-[600px] flex flex-col shadow-xl" on:click|stopPropagation on:keydown role="dialog" tabindex="-1">
      <!-- Modal header -->
      <div class="flex justify-between items-center p-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-800">{title}</h2>
        <button class="text-gray-500 hover:text-gray-800 text-2xl w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors" on:click={handleClose} aria-label="Sluit modal">
          ×
        </button>
      </div>

      <!-- Instructions -->
      <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
        <p class="text-sm text-gray-600">Navigeer naar de gewenste locatie en oriëntatie, klik vervolgens op "Huidige Weergave Opslaan" om de positie vast te leggen</p>
      </div>

      <!-- Cesium container -->
      <CesiumBaseMap 
        bind:this={cesiumBaseMap}
        {initialPosition}
        on:viewerReady={handleViewerReady}
      />

      <!-- Modal footer -->
      <div class="px-4 py-3 border-t border-gray-200 flex flex-col sm:flex-row sm:justify-between items-center gap-2">
        <button 
          class="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded text-sm font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors order-2 sm:order-1"
          on:click={handleSaveCurrentView}
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          Huidige Weergave Opslaan
        </button>
        <button 
          class="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded text-sm font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors order-1 sm:order-2"
          on:click={handleClose}
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
          Annuleren
        </button>
      </div>
    </div>
  </div>
{/if}
