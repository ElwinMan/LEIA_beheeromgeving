<script lang="ts">
  import type { Layer } from '$lib/types/layer';
  import { updateLayer } from '$lib/api';
  import { createEventDispatcher } from 'svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';

  export let layer: Layer | null = null;
  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher();

  // Tab state
  let activeTab = 0;
  const typeOptions = [
    { value: 'wms', label: 'WMS' },
    { value: 'wmts', label: 'WMTS' },
    { value: '3DTiles', label: '3DTiles' },
    { value: 'geojson', label: 'GeoJSON' }
  ];

  // Main tab fields
  let title = '';
  let type = '';
  let mainUrl = '';
  let imageUrl = '';
  let legendUrl = '';
  let defaultAddToManager = false;
  let attribution = '';
  let metadata = '';
  let transparent = false;
  let opacity = 100;
  let cameraX: number = 0;
  let cameraY: number = 0;
  let cameraZ: number = 0;
  let cameraHeading: number = 0;
  let cameraPitch: number = 0;
  let cameraDuration: number = 1.5;
  $: cameraPosition = JSON.stringify({
    x: cameraX,
    y: cameraY,
    z: cameraZ,
    heading: cameraHeading,
    pitch: cameraPitch,
    duration: cameraDuration
  });
  let isBackground = false;

  // WMS tab fields
  let wmsFeatureName = '';
  let wmsContentType = '';

  // WMTS tab fields
  let wmtsFeatureName = '';
  let wmtsContentType = '';
  let wmtsRequestEncoding = '';
  let wmtsMatrixIds = '';
  let wmtsTileMatrixSetID = '';
  let wmtsTileWidth = '';
  let wmtsTileHeight = '';
  let wmtsMaximumLevel = '';

  // 3DTiles tab fields
  let tilesShadows = false;
  let tilesetHeight = '';
  let enableHeightControl = false;
  let defaultTheme = '';

  // GeoJSON tab fields
  let geojsonUrl = '';
  let geojsonStyle = {
    stroke: '#0000ff',
    strokeWidth: 1,
    fill: '#ff0000'
  };
  let geojsonClampToGround = true;
  let geojsonExtrude = {
    slider_min: 0,
    slider_max: 10,
    slider_step: 1,
    slider_default: 0,
    slider_label: 'Extrude Height'
  };

  export function showModal(l: Layer) {
    layer = l;
    title = layer.title || '';
    type = layer.type || '';
    mainUrl = layer.url || '';
    imageUrl = layer.content?.imageUrl || '';
    legendUrl = layer.content?.legendUrl || '';
    defaultAddToManager = layer.content?.defaultAddToManager || false;
    attribution = layer.content?.attribution || '';
    metadata = layer.content?.metadata || '';
    transparent = layer.content?.transparent || false;
    opacity = layer.content?.opacity ?? 100;
    isBackground = layer.isBackground || false;

    // Camera position
    if (layer.content?.cameraPosition) {
      try {
        const cam = typeof layer.content.cameraPosition === 'string' ? JSON.parse(layer.content.cameraPosition) : layer.content.cameraPosition;
        cameraX = cam.x ?? 0;
        cameraY = cam.y ?? 0;
        cameraZ = cam.z ?? 0;
        cameraHeading = cam.heading ?? 0;
        cameraPitch = cam.pitch ?? 0;
        cameraDuration = cam.duration ?? 1.5;
      } catch {}
    } else {
      cameraX = 0;
      cameraY = 0;
      cameraZ = 0;
      cameraHeading = 0;
      cameraPitch = 0;
      cameraDuration = 1.5;
    }

    // WMS
    wmsFeatureName = layer.content?.wms?.featureName || '';
    wmsContentType = layer.content?.wms?.contenttype || '';

    // WMTS
    wmtsFeatureName = layer.content?.wmts?.featureName || '';
    wmtsContentType = layer.content?.wmts?.contenttype || '';
    wmtsRequestEncoding = layer.content?.wmts?.requestencoding || '';
    wmtsMatrixIds = layer.content?.wmts?.matrixids || '';
    wmtsTileMatrixSetID = layer.content?.wmts?.tileMatrixSetID || '';
    wmtsTileWidth = layer.content?.wmts?.tileWidth || '';
    wmtsTileHeight = layer.content?.wmts?.tileHeight || '';
    wmtsMaximumLevel = layer.content?.wmts?.maximumLevel || '';

    // 3DTiles
    tilesShadows = layer.content?.tiles3d?.shadows || false;
    tilesetHeight = layer.content?.tiles3d?.tilesetHeight || '';
    enableHeightControl = layer.content?.tiles3d?.enableHeightControl || false;
    defaultTheme = layer.content?.tiles3d?.defaultTheme || '';

    // GeoJSON
    geojsonUrl = layer.content?.settings?.url || '';
    geojsonStyle = layer.content?.settings?.style || {
      stroke: '#0000ff',
      strokeWidth: 1,
      fill: '#ff0000'
    };
    geojsonClampToGround = layer.content?.settings?.clampToGround ?? true;
    geojsonExtrude = layer.content?.settings?.tools?.extrude || {
      slider_min: 0,
      slider_max: 10,
      slider_step: 1,
      slider_default: 0,
      slider_label: 'Extrude Height'
    };

    activeTab = 0;
    modalRef.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!layer) return;

    const tabContentMap: Record<string, any> = {
      wms: {
        wms: {
          featureName: wmsFeatureName,
          contenttype: wmsContentType
        }
      },
      wmts: {
        wmts: {
          featureName: wmtsFeatureName,
          contenttype: wmtsContentType,
          requestencoding: wmtsRequestEncoding,
          matrixids: wmtsMatrixIds,
          tileMatrixSetID: wmtsTileMatrixSetID,
          tileWidth: wmtsTileWidth,
          tileHeight: wmtsTileHeight,
          maximumLevel: wmtsMaximumLevel
        }
      },
      '3DTiles': {
        tiles3d: {
          shadows: tilesShadows,
          tilesetHeight,
          enableHeightControl,
          defaultTheme
        }
      },
      geojson: {
        settings: {
          url: geojsonUrl,
          style: geojsonStyle,
          clampToGround: geojsonClampToGround,
          tools: {
            extrude: geojsonExtrude
          }
        }
      }
    };

    const content: Record<string, any> = {
      imageUrl,
      legendUrl,
      defaultAddToManager,
      attribution,
      metadata,
      transparent,
      opacity,
      cameraPosition,
      ...(tabContentMap[type] || {})
    };

    // Set top-level featureName based on type
    let featureName = '';
    if (type === 'wms') featureName = wmsFeatureName;
    else if (type === 'wmts') featureName = wmtsFeatureName;

    try {
      const updated = await updateLayer(String(layer.id), {
        type,
        title,
        url: mainUrl,
        featureName,
        isBackground,
        content
      });
      dispatch('updated', updated);
      modalRef.close();
    } catch (error) {
      console.error('Update failed', error);
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form on:submit|preventDefault={handleSubmit} class="modal-box w-full max-w-4xl">
    <h3 class="mb-4 text-lg font-bold">Laag details bewerken</h3>
    <div class="tabs tabs-border mb-4" role="tablist">
      <button
        type="button"
        class="tab {activeTab === 0 ? 'tab-active' : ''}"
        role="tab"
        aria-selected={activeTab === 0}
        tabindex={activeTab === 0 ? 0 : -1}
        on:click={() => (activeTab = 0)}
      >Algemeen</button>
      {#if type === 'wms'}
        <button
          type="button"
          class="tab {activeTab === 1 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 1}
          tabindex={activeTab === 1 ? 0 : -1}
          on:click={() => (activeTab = 1)}
        >WMS</button>
      {/if}
      {#if type === 'wmts'}
        <button
          type="button"
          class="tab {activeTab === 2 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 2}
          tabindex={activeTab === 2 ? 0 : -1}
          on:click={() => (activeTab = 2)}
        >WMTS</button>
      {/if}
      {#if type === '3DTiles'}
        <button
          type="button"
          class="tab {activeTab === 3 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 3}
          tabindex={activeTab === 3 ? 0 : -1}
          on:click={() => (activeTab = 3)}
        >3DTiles</button>
      {/if}
      {#if type === 'geojson'}
        <button
          type="button"
          class="tab {activeTab === 4 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 4}
          tabindex={activeTab === 4 ? 0 : -1}
          on:click={() => (activeTab = 4)}
        >GeoJSON</button>
      {/if}
    </div>

    {#if activeTab === 0}
      <!-- Algemeen Tab -->
      <div class="grid grid-cols-4 gap-4 items-center">
        <label for="title" class="pr-4 text-right font-semibold">Title:</label>
        <input id="title" class="input input-bordered col-span-3 w-full" bind:value={title} required />

        <label for="type" class="pr-4 text-right font-semibold">Type:</label>
        <select id="type" class="select select-bordered col-span-3 w-full" bind:value={type} required>
          <option value="" disabled selected>Kies een type...</option>
          {#each typeOptions as opt}
            <option value={opt.value}>{opt.label}</option>
          {/each}
        </select>

        <label for="mainUrl" class="pr-4 text-right font-semibold">URL:</label>
        <input id="mainUrl" class="input input-bordered col-span-3 w-full" bind:value={mainUrl} required />

        <label for="imageUrl" class="pr-4 text-right font-semibold">Image URL:</label>
        <input id="imageUrl" class="input input-bordered col-span-3 w-full" bind:value={imageUrl} />

        <label for="legendUrl" class="pr-4 text-right font-semibold">Legend URL:</label>
        <input id="legendUrl" class="input input-bordered col-span-3 w-full" bind:value={legendUrl} />

        <label for="defaultAddToManager" class="pr-4 text-right font-semibold">Default Add To Manager:</label>
        <input id="defaultAddToManager" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={defaultAddToManager} />

        <label for="attribution" class="pr-4 text-right font-semibold">Attribution:</label>
        <input id="attribution" class="input input-bordered col-span-3 w-full" bind:value={attribution} />

        <label for="metadata" class="pr-4 text-right font-semibold">Metadata:</label>
        <input id="metadata" class="input input-bordered col-span-3 w-full" bind:value={metadata} />

        <label for="transparent" class="pr-4 text-right font-semibold">Transparent:</label>
        <input id="transparent" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={transparent} />

        <label for="opacity" class="pr-4 text-right font-semibold">Opacity:</label>
        <input
          id="opacity"
          type="number"
          min="0"
          max="100"
          step="1"
          class="input input-bordered col-span-3 w-full"
          bind:value={opacity}
          on:input={() => { if (opacity > 100) opacity = 100; if (opacity < 0) opacity = 0; }}
        />

        <!-- Camera Position row: label left, button right, then xyz row below -->
        <label for="cameraX" class="pr-4 text-right font-semibold">Camera Position:</label>
        <div class="col-span-3 mb-2">
          <PositionSelector
            title="Selecteer camera positie"
            buttonText="Selecteer camera positie op kaart"
            initialPosition={{
              x: cameraX,
              y: cameraY,
              z: cameraZ,
              heading: cameraHeading,
              pitch: cameraPitch,
              duration: cameraDuration
            }}
            on:coordinatesSelected={(e: CustomEvent<any>) => {
              cameraX = e.detail.x;
              cameraY = e.detail.y;
              cameraZ = e.detail.z;
              cameraHeading = e.detail.heading;
              cameraPitch = e.detail.pitch;
              cameraDuration = e.detail.duration;
            }}
          />
        </div>

        <!-- X/Y/Z row: empty left, fields right -->
        <div></div>
        <div class="col-span-3 grid grid-cols-3 gap-2 mb-2">
          <div>
            <label for="cameraX" class="block text-xs font-medium mb-1">X</label>
            <input id="cameraX" type="number" step="any" class="input input-bordered w-full" bind:value={cameraX} />
          </div>
          <div>
            <label for="cameraY" class="block text-xs font-medium mb-1">Y</label>
            <input id="cameraY" type="number" step="any" class="input input-bordered w-full" bind:value={cameraY} />
          </div>
          <div>
            <label for="cameraZ" class="block text-xs font-medium mb-1">Z</label>
            <input id="cameraZ" type="number" step="any" class="input input-bordered w-full" bind:value={cameraZ} />
          </div>
        </div>

        <!-- Heading/Pitch/Duration row: empty left, fields right -->
        <div></div>
        <div class="col-span-3 grid grid-cols-3 gap-2">
          <div>
            <label for="cameraHeading" class="block text-xs font-medium mb-1">Heading</label>
            <input id="cameraHeading" type="number" step="any" class="input input-bordered w-full" bind:value={cameraHeading} />
          </div>
          <div>
            <label for="cameraPitch" class="block text-xs font-medium mb-1">Pitch</label>
            <input id="cameraPitch" type="number" step="any" class="input input-bordered w-full" bind:value={cameraPitch} />
          </div>
          <div>
            <label for="cameraDuration" class="block text-xs font-medium mb-1">Duration</label>
            <input id="cameraDuration" type="number" step="any" class="input input-bordered w-full" bind:value={cameraDuration} />
          </div>
        </div>

        <label for="isBackground" class="text-right font-semibold">Is Background:</label>
        <input type="checkbox" class="checkbox col-span-3 checkbox-primary" bind:checked={isBackground} disabled />
      </div>
    {/if}

    {#if type === 'wms' && activeTab === 1}
      <!-- WMS Tab -->
      <div class="grid grid-cols-4 gap-4 items-center">
        <label for="wmsFeatureName" class="pr-4 text-right font-semibold">Feature Name:</label>
        <input id="wmsFeatureName" class="input input-bordered col-span-3 w-full" bind:value={wmsFeatureName} />

        <label for="wmsContentType" class="pr-4 text-right font-semibold">Content Type:</label>
        <input id="wmsContentType" class="input input-bordered col-span-3 w-full" bind:value={wmsContentType} />
      </div>
    {/if}

    {#if type === 'wmts' && activeTab === 2}
      <!-- WMTS Tab -->
      <div class="grid grid-cols-4 gap-4 items-center">
        <label for="wmtsFeatureName" class="pr-4 text-right font-semibold">Feature Name:</label>
        <input id="wmtsFeatureName" class="input input-bordered col-span-3 w-full" bind:value={wmtsFeatureName} />

        <label for="wmtsContentType" class="pr-4 text-right font-semibold">Content Type:</label>
        <input id="wmtsContentType" class="input input-bordered col-span-3 w-full" bind:value={wmtsContentType} />

        <label for="wmtsRequestEncoding" class="pr-4 text-right font-semibold">Request Encoding:</label>
        <input id="wmtsRequestEncoding" class="input input-bordered col-span-3 w-full" bind:value={wmtsRequestEncoding} />

        <label for="wmtsMatrixIds" class="pr-4 text-right font-semibold">Matrix IDs:</label>
        <input id="wmtsMatrixIds" class="input input-bordered col-span-3 w-full" bind:value={wmtsMatrixIds} />

        <label for="wmtsTileMatrixSetID" class="pr-4 text-right font-semibold">Tile Matrix Set ID:</label>
        <input id="wmtsTileMatrixSetID" class="input input-bordered col-span-3 w-full" bind:value={wmtsTileMatrixSetID} />

        <label for="wmtsTileWidth" class="pr-4 text-right font-semibold">Tile Width:</label>
        <input id="wmtsTileWidth" class="input input-bordered col-span-3 w-full" bind:value={wmtsTileWidth} />

        <label for="wmtsTileHeight" class="pr-4 text-right font-semibold">Tile Height:</label>
        <input id="wmtsTileHeight" class="input input-bordered col-span-3 w-full" bind:value={wmtsTileHeight} />

        <label for="wmtsMaximumLevel" class="pr-4 text-right font-semibold">Maximum Level:</label>
        <input id="wmtsMaximumLevel" class="input input-bordered col-span-3 w-full" bind:value={wmtsMaximumLevel} />
      </div>
    {/if}

    {#if type === '3DTiles' && activeTab === 3}
      <!-- 3DTiles Tab -->
      <div class="grid grid-cols-4 gap-4 items-center">
        <label for="tilesShadows" class="pr-4 text-right font-semibold">Shadows:</label>
        <input id="tilesShadows" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={tilesShadows} />

        <label for="tilesetHeight" class="pr-4 text-right font-semibold">Tileset Height:</label>
        <input id="tilesetHeight" class="input input-bordered col-span-3 w-full" bind:value={tilesetHeight} />

        <label for="enableHeightControl" class="pr-4 text-right font-semibold">Enable Height Control:</label>
        <input id="enableHeightControl" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={enableHeightControl} />

        <label for="defaultTheme" class="pr-4 text-right font-semibold">Default Theme:</label>
        <input id="defaultTheme" class="input input-bordered col-span-3 w-full" bind:value={defaultTheme} />
      </div>
    {/if}

    {#if type === 'geojson' && activeTab == 4}
      <!-- GeoJSON Tab -->
      <div class="grid grid-cols-4 gap-4 items-center">
        <label for="geojsonUrl" class="pr-4 text-right font-semibold">GeoJSON URL:</label>
        <input id="geojsonUrl" class="input input-bordered col-span-3 w-full" bind:value={geojsonUrl} required />

        <label for="geojsonClampToGround" class="pr-4 text-right font-semibold">Clamp To Ground:</label>
        <input id="geojsonClampToGround" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={geojsonClampToGround} />

        <label for="geojsonStyleGroup" class="pr-4 text-right font-semibold">Style:</label>
        <div class="col-span-3 grid grid-cols-2 gap-2">
          <div>
            <label for="geojsonStroke" class="block text-xs font-medium mb-1">Stroke</label>
            <input id="geojsonStroke" type="color" class="h-8 w-12 rounded border border-gray-300 p-0" bind:value={geojsonStyle.stroke} />
            <input id="geojsonStrokeText" type="text" class="input input-bordered mt-1 w-full" bind:value={geojsonStyle.stroke} />
          </div>
          <div>
            <label for="geojsonFill" class="block text-xs font-medium mb-1">Fill</label>
            <input id="geojsonFill" type="color" class="h-8 w-12 rounded border border-gray-300 p-0" bind:value={geojsonStyle.fill} />
            <input id="geojsonFillText" type="text" class="input input-bordered mt-1 w-full" bind:value={geojsonStyle.fill} />
          </div>
        </div>
        <div></div>
        <div class="col-span-3 grid grid-cols-2 gap-2 mt-2">
          <div>
            <label for="geojsonStrokeWidth" class="block text-xs font-medium mb-1">Stroke Width</label>
            <input id="geojsonStrokeWidth" type="number" min="1" class="input input-bordered w-full" bind:value={geojsonStyle.strokeWidth} />
          </div>
          <div></div>
        </div>

        <label for="geojsonExtrudeGroup" class="pr-4 text-right font-semibold">Extrude Tool:</label>
        <div class="col-span-3 grid grid-cols-5 gap-2">
          <div>
            <label for="geojsonExtrudeMin" class="block text-xs font-medium mb-1">Slider Min</label>
            <input id="geojsonExtrudeMin" type="number" class="input input-bordered w-full" bind:value={geojsonExtrude.slider_min} />
          </div>
          <div>
            <label for="geojsonExtrudeMax" class="block text-xs font-medium mb-1">Slider Max</label>
            <input id="geojsonExtrudeMax" type="number" class="input input-bordered w-full" bind:value={geojsonExtrude.slider_max} />
          </div>
          <div>
            <label for="geojsonExtrudeStep" class="block text-xs font-medium mb-1">Slider Step</label>
            <input id="geojsonExtrudeStep" type="number" class="input input-bordered w-full" bind:value={geojsonExtrude.slider_step} />
          </div>
          <div>
            <label for="geojsonExtrudeDefault" class="block text-xs font-medium mb-1">Slider Default</label>
            <input id="geojsonExtrudeDefault" type="number" class="input input-bordered w-full" bind:value={geojsonExtrude.slider_default} />
          </div>
          <div>
            <label for="geojsonExtrudeLabel" class="block text-xs font-medium mb-1">Slider Label</label>
            <input id="geojsonExtrudeLabel" type="text" class="input input-bordered w-full" bind:value={geojsonExtrude.slider_label} />
          </div>
        </div>
      </div>
    {/if}

    <div class="mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>
        Annuleren
      </button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>