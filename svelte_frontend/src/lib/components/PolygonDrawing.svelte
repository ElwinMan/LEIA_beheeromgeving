<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { 
    Viewer,
    Cartesian3, 
    Math as CesiumMath, 
    Cartographic, 
    Ellipsoid,
    Entity,
    Color,
    ScreenSpaceEventHandler,
    ScreenSpaceEventType,
    HeightReference,
    Ion,
    defined
  } from 'cesium';
  import CesiumBaseMap from './CesiumBaseMap.svelte';

  export let title = 'Polygon Tekenen';
  export let buttonText = 'Teken polygon op kaart';
  export let initialPosition: {
    x?: number;
    y?: number;
    z?: number;
    heading?: number;
    pitch?: number;
    roll?: number;
    duration?: number;
  } | null = null;
  export let initialPolygon: number[][] | null = null;

  const dispatch = createEventDispatcher();

  let isVisible = false;
  let viewer: Viewer | null = null;
  let cesiumBaseMap: CesiumBaseMap;
  let handler: ScreenSpaceEventHandler | null = null;
  let isDrawing = false;
  let polygonPoints: Cartesian3[] = [];
  let activePolyline: Entity | null = null;
  let activePolygon: Entity | null = null;
  let pointEntities: Entity[] = [];

  function handleViewerReady(event: CustomEvent) {
    viewer = event.detail.viewer;
    
    // Load initial polygon if provided
    if (initialPolygon && initialPolygon.length > 0) {
      loadInitialPolygon();
    }
    
    setupPolygonDrawing();
  }

  function loadInitialPolygon() {
    if (!viewer || !initialPolygon) return;

    try {
      // Convert polygon coordinates to Cartesian3 points
      polygonPoints = initialPolygon.map(coord => 
        Cartesian3.fromDegrees(coord[0], coord[1])
      );

      // Create polygon entity
      if (polygonPoints.length >= 3) {
        activePolygon = viewer.entities.add({
          polygon: {
            hierarchy: polygonPoints,
            material: Color.BLUE.withAlpha(0.3),
            outline: true,
            outlineColor: Color.BLUE
          }
        });
      }

      // Create point entities
      polygonPoints.forEach((point, index) => {
        const pointEntity = viewer!.entities.add({
          position: point,
          point: {
            pixelSize: 8,
            color: Color.YELLOW,
            outlineColor: Color.BLACK,
            outlineWidth: 2,
            heightReference: HeightReference.CLAMP_TO_GROUND
          }
        });
        pointEntities.push(pointEntity);
      });
    } catch (error) {
      console.error('Error loading initial polygon:', error);
    }
  }

  function setupPolygonDrawing() {
    if (!viewer) return;

    handler = new ScreenSpaceEventHandler(viewer.scene.canvas);
    
    // Left click to add points
    handler.setInputAction((click: any) => {
      if (!viewer) return;

      const pickedPosition = viewer.camera.pickEllipsoid(click.position, viewer.scene.globe.ellipsoid);
      if (!defined(pickedPosition)) return;

      if (!isDrawing) {
        startDrawing();
      }

      addPoint(pickedPosition);
    }, ScreenSpaceEventType.LEFT_CLICK);

    // Right click to finish polygon
    handler.setInputAction(() => {
      if (isDrawing && polygonPoints.length >= 3) {
        finishPolygon();
      }
    }, ScreenSpaceEventType.RIGHT_CLICK);

    // Disable default right-click context menu
    viewer.cesiumWidget.screenSpaceEventHandler.removeInputAction(ScreenSpaceEventType.RIGHT_CLICK);
  }

  function startDrawing() {
    if (!viewer) return;
    
    isDrawing = true;
    clearExistingDrawing();
    polygonPoints = [];
    pointEntities = [];
  }

  function addPoint(position: Cartesian3) {
    if (!viewer) return;

    // Use Svelte reactivity pattern - reassign array to trigger updates
    polygonPoints = [...polygonPoints, position];

    // Add point entity
    const pointEntity = viewer.entities.add({
      position: position,
      point: {
        pixelSize: 8,
        color: Color.YELLOW,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        heightReference: HeightReference.CLAMP_TO_GROUND
      }
    });
    pointEntities.push(pointEntity);

    // Update polyline
    if (polygonPoints.length > 1) {
      if (activePolyline) {
        viewer.entities.remove(activePolyline);
      }
      
      activePolyline = viewer.entities.add({
        polyline: {
          positions: polygonPoints,
          width: 2,
          material: Color.BLUE,
          clampToGround: true
        }
      });
    }
  }

  function finishPolygon() {
    if (!viewer || polygonPoints.length < 3) return;

    // Remove the temporary polyline
    if (activePolyline) {
      viewer.entities.remove(activePolyline);
      activePolyline = null;
    }

    // Create the final polygon
    activePolygon = viewer.entities.add({
      polygon: {
        hierarchy: polygonPoints,
        material: Color.BLUE.withAlpha(0.3),
        outline: true,
        outlineColor: Color.BLUE
      }
    });

    isDrawing = false;
  }

  function clearExistingDrawing() {
    if (!viewer) return;

    // Remove existing entities
    if (activePolyline) {
      viewer.entities.remove(activePolyline);
      activePolyline = null;
    }
    
    if (activePolygon) {
      viewer.entities.remove(activePolygon);
      activePolygon = null;
    }

    pointEntities.forEach(entity => {
      viewer!.entities.remove(entity);
    });
    pointEntities = [];
  }

  function clearPolygon() {
    clearExistingDrawing();
    polygonPoints = [];
    isDrawing = false;
  }

  function handleClose() {
    if (handler) {
      handler.destroy();
      handler = null;
    }
    
    // Clear any drawing state when closing the modal
    clearPolygon();
    
    isVisible = false;
    dispatch('close');
  }

  function handleOpen() {
    isVisible = true;
  }

  function handleSavePolygonAndPosition() {
    if (!viewer) {
      console.error('No viewer available');
      return;
    }

    // Check if we have enough points first
    if (polygonPoints.length < 3) {
      alert('Je moet minimaal 3 punten tekenen om een polygon op te slaan.');
      return;
    }

    // If user is still drawing (didn't right-click to finish), finish the polygon now
    if (isDrawing) {
      finishPolygon();
    }

    try {
      let result: any = {};

      // Save polygon coordinates
      const polygonCoords = polygonPoints.map(point => {
        const cartographic = Cartographic.fromCartesian(point, Ellipsoid.WGS84);
        return [
          CesiumMath.toDegrees(cartographic.longitude),
          CesiumMath.toDegrees(cartographic.latitude)
        ];
      });
      result.polygon = polygonCoords;

      // Only dispatch polygon data
      dispatch('coordinatesSelected', result);
      isVisible = false;
    } catch (error) {
      console.error('Error capturing polygon:', error);
    }
  }
</script>

<!-- Button to open polygon drawing -->
<button 
  type="button"
  class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-sm font-medium transition-colors shadow-sm"
  on:click={handleOpen}
>
  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m-6 3l6-3"></path>
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
    <div class="bg-white rounded-lg w-[95%] max-w-6xl h-[85%] max-h-[90vh] flex flex-col shadow-xl" on:click|stopPropagation on:keydown role="dialog" tabindex="-1">
      <!-- Modal header -->
      <div class="flex justify-between items-center p-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-800">{title}</h2>
        <button class="text-gray-500 hover:text-gray-800 text-2xl w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors" on:click={handleClose} aria-label="Sluit modal">
          ×
        </button>
      </div>

      <!-- Instructions -->
      <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
        <p class="text-sm text-gray-600 mb-2">
          <strong>Polygon tekenen:</strong> Klik met de linkermuisknop om punten toe te voegen. Klik met de rechtermuisknop om de vorm af te maken (minimaal 3 punten vereist).
        </p>
      </div>

      <!-- Drawing controls -->
      <div class="px-4 py-2 bg-blue-50 border-b border-blue-200 flex items-center gap-2">
        <button 
          type="button"
          class="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600 transition-colors"
          on:click={clearPolygon}
        >
          Wis Polygon
        </button>
        <span class="text-sm text-blue-700">
          {#if isDrawing}
            Aan het tekenen... ({polygonPoints.length} punten) - Rechtermuisknop om af te maken
          {:else if polygonPoints.length > 0}
            Polygon getekend ({polygonPoints.length} punten)
          {:else}
            Klik op de kaart om te beginnen met tekenen
          {/if}
        </span>
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
          type="button"
          class="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 rounded text-sm font-medium focus:outline-none focus:ring-2 transition-colors order-2 sm:order-1"
          class:bg-green-600={polygonPoints.length >= 3}
          class:text-white={polygonPoints.length >= 3}
          class:hover:bg-green-700={polygonPoints.length >= 3}
          class:focus:ring-green-500={polygonPoints.length >= 3}
          class:bg-gray-300={polygonPoints.length < 3}
          class:text-gray-500={polygonPoints.length < 3}
          class:cursor-not-allowed={polygonPoints.length < 3}
          on:click={handleSavePolygonAndPosition}
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          Opslaan Polygon {polygonPoints.length < 3 ? `(${polygonPoints.length}/3 punten)` : ''}
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
