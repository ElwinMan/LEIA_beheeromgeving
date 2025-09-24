<script lang="ts">
  import { createEventDispatcher, tick } from 'svelte';
  import { 
    Viewer,
    Cartographic, 
    Ellipsoid,
    Math as CesiumMath
  } from 'cesium';
  import CesiumBaseMap from './CesiumBaseMap.svelte';

  export let title = 'Selecteer Positie';
  export let buttonText = 'Selecteer positie op kaart';
  export let disabled = false;
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
  let dialogEl: HTMLDialogElement | null = null;

  function handleViewerReady(event: CustomEvent) {
    viewer = event.detail.viewer;
  }

  function handleClose() {
    // Close native dialog if open
    dialogEl?.open && dialogEl.close();
    isVisible = false;
    // restore body scroll when closing
    document.body.style.overflow = '';
    dispatch('close');
  }

  async function handleOpen() {
    isVisible = true;
    // prevent background scroll and keep overlay fixed to viewport
    document.body.style.overflow = 'hidden';
    // ensure the dialog is in the DOM before opening as a modal (top layer)
    await tick();
    await new Promise((resolve) => requestAnimationFrame(() => resolve(null)));
    dialogEl?.showModal?.();
  }

  function handleSaveCurrentView() {
    if (!viewer) return;

    try {
      // Get current camera position
      const camera = viewer.camera;
      const position = camera.position;
      
      const cartographic = Cartographic.fromCartesian(position, Ellipsoid.WGS84);
      const x = Number.parseFloat(CesiumMath.toDegrees(cartographic.longitude).toFixed(5));
      const y = Number.parseFloat(CesiumMath.toDegrees(cartographic.latitude).toFixed(5));
      const z = Number.parseFloat(cartographic.height.toFixed(5));

      const heading = Number.parseFloat(CesiumMath.toDegrees(camera.heading).toFixed(5));
      const pitch = Number.parseFloat(CesiumMath.toDegrees(camera.pitch).toFixed(5));
      const currentDuration = initialPosition?.duration ?? 0;
      const duration = currentDuration === 0 ? 2.0 : currentDuration;

      const result = {
        x,
        y,
        z,
        heading,
        pitch,
        duration
      };

      dispatch('coordinatesSelected', result);
      isVisible = false;
    } catch (error) {
      console.error('Error capturing current view:', error);
    }
  }
</script>

<style>
  /* Style the native dialog backdrop */
  :global(dialog.position-selector)::backdrop {
    background-color: rgba(0, 0, 0, 0.5);
  }
  /* Reset UA defaults for a clean card look */
  :global(dialog.position-selector) {
    padding: 0;
    border: none;
    /* Center in viewport */
    inset: 0;
    margin: auto;
  }
</style>

<!-- Button to open position selector -->
<button 
  type="button"
  class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-sm font-medium transition-colors shadow-sm disabled:bg-gray-400 disabled:cursor-not-allowed disabled:hover:bg-gray-400"
  on:click={handleOpen}
  {disabled}
>
  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
  </svg>
  {buttonText}
</button>

<!-- Modal dialog in top layer (above other dialogs) -->
{#if isVisible}
  <dialog
    bind:this={dialogEl}
    class="position-selector w-[90vw] max-w-4xl h-[80vh] max-h-[600px] rounded-lg shadow-xl bg-white flex flex-col"
    aria-modal="true"
    on:cancel|preventDefault={handleClose}
    on:close={handleClose}
    on:click={(e) => {
      // Close when backdrop is clicked (event target is the dialog itself)
      if (e.target === dialogEl) handleClose();
    }}
  >
    <div class="flex flex-col h-full" tabindex="-1">
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
      <div class="flex-1 min-h-0">
        <CesiumBaseMap 
          bind:this={cesiumBaseMap}
          {initialPosition}
          on:viewerReady={handleViewerReady}
        />
      </div>

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
  </dialog>
{/if}
