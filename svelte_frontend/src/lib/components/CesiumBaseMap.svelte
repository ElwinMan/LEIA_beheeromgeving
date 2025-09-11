<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { 
    Viewer, 
    Cartesian3, 
    Math as CesiumMath
  } from 'cesium';
  import 'cesium/Build/Cesium/Widgets/widgets.css';

  export let initialPosition: {
    x?: number;
    y?: number;
    z?: number;
    heading?: number;
    pitch?: number;
    roll?: number;
  } | null = null;

  const dispatch = createEventDispatcher();

  let cesiumContainer: HTMLDivElement;
  let viewer: Viewer | null = null;

  onMount(() => {
    if (cesiumContainer) {
      initializeCesium();
    }
  });

  onDestroy(() => {
    cleanup();
  });

  function cleanup() {
    if (viewer) {
      viewer.destroy();
      viewer = null;
    }
  }

  function initializeCesium() {
    if (!cesiumContainer) return;

    try {
      // Set a proper Ion access token or use a different imagery provider
      // For now, we'll use the default but handle the warning differently
      
      viewer = new Viewer(cesiumContainer, {
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

      // Set initial camera position
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

      // Hide the Ion access token warning and other overlays
      setTimeout(() => {
        const ionWarning = viewer?.cesiumWidget.creditContainer?.querySelector('.cesium-widget-credits') as HTMLElement;
        if (ionWarning) {
          ionWarning.style.display = 'none';
        }
        
        // Hide any other overlays
        const overlays = viewer?.cesiumWidget.container?.querySelectorAll('.cesium-widget-errorPanel');
        overlays?.forEach((overlay) => {
          (overlay as HTMLElement).style.display = 'none';
        });
      }, 100);

      // Dispatch viewer ready event
      dispatch('viewerReady', { viewer });

    } catch (error) {
      console.error('Error initializing Cesium:', error);
      dispatch('error', { error });
    }
  }

  // Expose viewer getter for parent components
  export function getViewer(): Viewer | null {
    return viewer;
  }
</script>

<div class="flex-1 w-full relative cesium-container" bind:this={cesiumContainer}></div>