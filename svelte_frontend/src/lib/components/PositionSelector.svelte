<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { Viewer, Cartesian3, Math as CesiumMath, Cartographic, Ellipsoid } from 'cesium';
  import 'cesium/Build/Cesium/Widgets/widgets.css';

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
  let cesiumContainer: HTMLDivElement;
  let viewer: Viewer | null = null;

  onMount(() => {
    if (cesiumContainer && isVisible) {
      initializeCesium();
    }
  });

  onDestroy(() => {
    if (viewer) {
      viewer.destroy();
      viewer = null;
    }
  });

  $: if (isVisible && cesiumContainer && !viewer) {
    initializeCesium();
  } else if (!isVisible && viewer) {
    viewer.destroy();
    viewer = null;
  }

  function initializeCesium() {
    if (!cesiumContainer) return;

    try {
      viewer = new Viewer(cesiumContainer, {
        terrainProvider: undefined, // Use ellipsoid terrain for now
        homeButton: false,
        sceneModePicker: false,
        baseLayerPicker: false,
        navigationHelpButton: false,
        animation: false,
        timeline: false,
        fullscreenButton: false,
        vrButton: false,
        geocoder: false,
        infoBox: false,
        selectionIndicator: false
      });

      // Set initial camera position - use provided position or default to Netherlands
      // If coordinates are all zero, treat as unset and use defaults
      const hasValidCoordinates = initialPosition && (
        (initialPosition.x !== 0 || initialPosition.y !== 0 || initialPosition.z !== 0)
      );
      
      const longitude = hasValidCoordinates ? initialPosition!.x! : 5.2913;
      const latitude = hasValidCoordinates ? initialPosition!.y! : 52.1326;
      const height = hasValidCoordinates ? initialPosition!.z! : 500000;
      const heading = hasValidCoordinates ? (initialPosition!.heading ?? 0.0) : 0.0;
      const pitch = hasValidCoordinates ? (initialPosition!.pitch ?? -90.0) : -90.0;
      const roll = hasValidCoordinates ? (initialPosition!.roll ?? 0.0) : 0.0;

      viewer.camera.setView({
        destination: Cartesian3.fromDegrees(longitude, latitude, height),
        orientation: {
          heading: CesiumMath.toRadians(heading),
          pitch: CesiumMath.toRadians(pitch),
          roll: CesiumMath.toRadians(roll)
        }
      });

      console.log('Cesium viewer initialized successfully');
    } catch (error) {
      console.error('Error initializing Cesium:', error);
    }
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
      
      // Convert camera position to longitude/latitude/height
      const cartographic = Cartographic.fromCartesian(position, Ellipsoid.WGS84);
      const longitude = CesiumMath.toDegrees(cartographic.longitude);
      const latitude = CesiumMath.toDegrees(cartographic.latitude);
      const height = cartographic.height;

      // Get camera orientation
      const heading = CesiumMath.toDegrees(camera.heading);
      const pitch = CesiumMath.toDegrees(camera.pitch);
      const roll = CesiumMath.toDegrees(camera.roll);

      // Preserve existing duration or use default of 2.0 if it's 0 or undefined
      const currentDuration = initialPosition?.duration ?? 0;
      const duration = currentDuration === 0 ? 2.0 : currentDuration;

      // Dispatch the coordinates event with all camera properties
      dispatch('coordinatesSelected', {
        longitude,
        latitude,
        height,
        heading,
        pitch,
        roll,
        // For backward compatibility with existing x/y/z usage
        x: longitude,
        y: latitude,
        z: height,
        duration
      });

      // Close the modal
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
      <div class="flex-1 w-full relative" bind:this={cesiumContainer}></div>

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
