<script lang="ts">
  import type { Layer } from '$lib/types/layer';
  import { updateLayer } from '$lib/api';
  import { createEventDispatcher } from 'svelte';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';
  let missingFields: string[] = [];

  export let layer: Layer | null = null;
  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher();

  // Tab state
  let activeTab = 0;
  const typeOptions = [
    { value: 'wms', label: 'WMS' },
    { value: 'wmts', label: 'WMTS' },
    { value: '3dtiles', label: '3DTiles' },
    { value: 'geojson', label: 'GeoJSON' },
    { value: 'modelanimation', label: 'Model Animation' }
  ];

  // Main tab fields
  let title = '';
  let type = '';
  let mainUrl = '';
  let imageUrl = '';
  let legendUrl = '';
  let defaultAddToManager = false;
  let description = '';
  let attribution = '';
  let metadata = '';
  let disablePopup = false;
  let transparent = false;
  let opacity = 100;
  let enableCameraPosition = false;
  let cameraX: number = 0;
  let cameraY: number = 0;
  let cameraZ: number = 0;
  let cameraHeading: number = 0;
  let cameraPitch: number = 0;
  let cameraDuration: number = 1.5;
  $: cameraPosition = {
    x: cameraX,
    y: cameraY,
    z: cameraZ,
    heading: cameraHeading,
    pitch: cameraPitch,
    duration: cameraDuration
  };
  let isBackground = false;

  // WMS tab fields
  let wmsFeatureName = '';
  let wmsContentType = '';

  // WMTS tab fields
  let wmtsFeatureName = '';
  let wmtsContentType = '';
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

  // ModelAnimation tab fields
  let modelUrl: string = '';
  let timeKey: string = '';
  let orientationKey: string = '';
  let modelClampToTerrain: boolean = true;
  let timeKeyDate: string = '';
  let timeKeyTime: string = '';

  // Helper to update timeKey from date and time inputs
  $: if (timeKeyDate && timeKeyTime) {
    const dt = new Date(timeKeyDate + 'T' + timeKeyTime);
    if (!isNaN(dt.getTime())) {
      timeKey = dt.toISOString().replace(/\.\d{3}Z$/, 'Z');
    }
  }

  function resetModal() {
    missingFields = [];
  }

  export function showModal(l: Layer) {
    layer = l;
    title = layer.title || '';
    type = layer.type || '';
    mainUrl = layer.url || '';
    imageUrl = layer.content?.imageUrl || '';
    legendUrl = layer.content?.legendUrl || '';
    defaultAddToManager = layer.content?.defaultAddToManager || false;
    description = layer.content?.description || '';
    attribution = layer.content?.attribution || '';
    metadata = layer.content?.metadata || '';
    disablePopup = layer.content?.disablePopup || false;
    transparent = layer.content?.transparent || false;
    opacity = layer.content?.opacity ?? 100;
    isBackground = layer.isBackground || false;

    // Camera position
    enableCameraPosition = !!layer.content?.cameraPosition;
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
    wmsFeatureName = layer.featureName || '';
    wmsContentType = layer.content?.wms?.contentType || '';

    // WMTS
    wmtsFeatureName = layer.featureName || '';
    wmtsContentType = layer.content?.wmts?.contentType || '';
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
    geojsonStyle = layer.content?.geojson?.style || {
      stroke: '#0000ff',
      strokeWidth: 1,
      fill: '#ff0000'
    };
    geojsonClampToGround = layer.content?.geojson?.clampToGround ?? true;
    geojsonExtrude = layer.content?.geojson?.tools?.extrude || {
      slider_min: 0,
      slider_max: 10,
      slider_step: 1,
      slider_default: 0,
      slider_label: 'Extrude Height'
    };

    // Model Animation
    modelUrl = layer.content?.modelanimation?.modelUrl || '';
    timeKey = layer.content?.modelanimation?.timeKey || '';
    orientationKey = layer.content?.modelanimation?.orientationKey || '';
    modelClampToTerrain = layer.content?.modelanimation?.clampToTerrain ?? true;
    // Parse timeKey into date and time fields if present
    if (timeKey) {
      const d = new Date(timeKey);
      if (!isNaN(d.getTime())) {
        timeKeyDate = d.toISOString().slice(0, 10);
        timeKeyTime = d.toISOString().slice(11, 19);
      } else {
        timeKeyDate = '';
        timeKeyTime = '';
      }
    } else {
      timeKeyDate = '';
      timeKeyTime = '';
    }

    activeTab = 0;
    resetModal();
    modalRef.showModal();
  }

  function getMissingRequiredFields(): string[] {
    const fields: { label: string; value: any }[] = [];

    // Always check Algemeen tab required fields
    fields.push(
      { label: 'Title', value: title },
      { label: 'Type', value: type },
      { label: 'URL', value: mainUrl }
    );

    // Type-specific required fields
    if (type === 'modelanimation') {
      fields.push(
        { label: 'Model URL', value: modelUrl },
        { label: 'Date', value: timeKeyDate },
        { label: 'Time', value: timeKeyTime }
      );
    }

    return fields.filter(f => !f.value || (typeof f.value === 'string' && !f.value.trim())).map(f => f.label);
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    if (!layer) return;
    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) return;

    const tabContentMap: Record<string, any> = {
      wms: {
        wms: {
          contentType: wmsContentType
        }
      },
      wmts: {
        wmts: {
          contentType: wmtsContentType,
          matrixids: wmtsMatrixIds,
          tileMatrixSetID: wmtsTileMatrixSetID,
          tileWidth: wmtsTileWidth,
          tileHeight: wmtsTileHeight,
          maximumLevel: wmtsMaximumLevel
        }
      },
      '3dtiles': {
        tiles3d: {
          shadows: tilesShadows,
          tilesetHeight,
          enableHeightControl,
          defaultTheme
        }
      },
      geojson: {
        geojson: {
          style: geojsonStyle,
          clampToGround: geojsonClampToGround,
          tools: {
            extrude: geojsonExtrude
          }
        }
      },
      modelanimation: {
        modelanimation: {
          modelUrl,
          timeKey,
          orientationKey,
          clampToGround: modelClampToTerrain
        }
      }
    };

    const content: Record<string, any> = {
      imageUrl,
      legendUrl,
      defaultAddToManager,
      description,
      attribution,
      metadata,
      disablePopup,
      ...(tabContentMap[type] || {})
    };

    // Only add transparent and opacity if transparent is true
    if (transparent) {
      content.transparent = true;
      content.opacity = opacity;
    }

    // Only add cameraPosition if enabled
    if (enableCameraPosition) {
      content.cameraPosition = cameraPosition;
    }

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
  <MissingRequiredFields {missingFields} />
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
      {#if type === '3dtiles'}
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
      {#if type === 'modelanimation'}
        <button
          type="button"
          class="tab {activeTab === 5 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 5}
          tabindex={activeTab === 5 ? 0 : -1}
          on:click={() => (activeTab = 5)}
        >Model Animation</button>
      {/if}
    </div>

    {#if activeTab === 0}
      <!-- Algemeen Tab -->
      <div class="grid grid-cols-4 gap-4 items-center">
        <label for="title" class="pr-4 text-right font-semibold">
          Title:<span class="text-error">*</span>
          <HelpTooltip tip="De titel van de laag." />
        </label>
        <input id="title" class="input input-bordered col-span-3 w-full" bind:value={title} />

        <label for="type" class="pr-4 text-right font-semibold">
          Type:<span class="text-error">*</span>
          <HelpTooltip tip="Het type van de laag. Let op! Het type voegt een tabblad toe met specifieke instellingen." />
        </label>
        <select id="type" class="select select-bordered col-span-3 w-full" bind:value={type} >
          <option value="" disabled selected>Kies een type...</option>
          {#each typeOptions as opt}
            <option value={opt.value}>{opt.label}</option>
          {/each}
        </select>

        <label for="mainUrl" class="pr-4 text-right font-semibold">
          URL:<span class="text-error">*</span>
          <HelpTooltip tip="De hoofd-URL van de laag." />
        </label>
        <input id="mainUrl" class="input input-bordered col-span-3 w-full" bind:value={mainUrl} />

        <label for="imageUrl" class="pr-4 text-right font-semibold">
          Image URL:
          <HelpTooltip tip="De URL van een voorbeeldafbeelding van de laag, wordt weergegeven in de lagenbibliotheek." />
        </label>
        <input id="imageUrl" class="input input-bordered col-span-3 w-full" bind:value={imageUrl} />

        <label for="legendUrl" class="pr-4 text-right font-semibold">
          Legend URL:
          <HelpTooltip tip="De URL van de legenda voor de laag." />
        </label>
        <input id="legendUrl" class="input input-bordered col-span-3 w-full" bind:value={legendUrl} />

        <label for="defaultAddToManager" class="pr-4 text-right font-semibold">
          Default Add To Manager:
          <HelpTooltip tip="Standaard toevoegen aan manager." />
        </label>
        <input id="defaultAddToManager" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={defaultAddToManager} />

        <label for="description" class="pr-4 text-right font-semibold">
          Description:
          <HelpTooltip tip="Een tekst veld die de laag beschrijft bij het open klappen van het laag." />
        </label>
        <textarea
          id="description"
          class="textarea textarea-bordered col-span-3 w-full resize-y min-h-[6rem]"
          rows="4"
          bind:value={description}
          placeholder="Beschrijf deze laag..."
        ></textarea>

        <label for="attribution" class="pr-4 text-right font-semibold">
          Attribution:
          <HelpTooltip tip="De attributie voor de laag." />
        </label>
        <input id="attribution" class="input input-bordered col-span-3 w-full" bind:value={attribution} />

        <label for="metadata" class="pr-4 text-right font-semibold">
          Metadata:
          <HelpTooltip tip="De metadata voor de laag." />
        </label>
        <input id="metadata" class="input input-bordered col-span-3 w-full" bind:value={metadata} />

        <label for="disablePopup" class="pr-4 text-right font-semibold">
          Disable Popup:
          <HelpTooltip tip="Schakel de feature info popup voor deze laag uit." />
        </label>
        <input id="disablePopup" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={disablePopup} />

        <label for="transparent" class="pr-4 text-right font-semibold">
          Transparent:
          <HelpTooltip tip="Maak de laag doorzichtig." />
        </label>
        <input id="transparent" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={transparent} />

        <label for="opacity" class="pr-4 text-right font-semibold">
          Opacity:
          <HelpTooltip tip="De doorzichtigheid van de laag (0-100)." />
        </label>
        <input
          id="opacity"
          type="number"
          min="0"
          max="100"
          step="1"
          class="input input-bordered col-span-3 w-full"
          bind:value={opacity}
          on:input={() => { if (opacity > 100) opacity = 100; if (opacity < 0) opacity = 0; }}
          disabled={!transparent}
        />

        <label for="enableCameraPosition" class="pr-4 text-right font-semibold">
          Enable Camera Position:
          <HelpTooltip tip="Schakel camerastandpunt in. Wanneer ingeschakeld, wordt er een zoom-naar-icoon weergegeven voor de laag in de lagenbeheerder." />
        </label>
        <input id="enableCameraPosition" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={enableCameraPosition} />

        <!-- Camera Position row: label left, button right, then xyz row below -->
        <label for="cameraX" class="pr-4 text-right font-semibold">
          Camera Position:
          <HelpTooltip tip="Gebruik de positie-selector om de camera positie in te stellen of voer het handmatig in, duration wordt niet door de position-selector gegenereerd." />
        </label>
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
            disabled={!enableCameraPosition}
          />
        </div>

        <!-- X/Y/Z row: empty left, fields right -->
        <div></div>
        <div class="col-span-3 grid grid-cols-3 gap-2 mb-2">
          <div>
            <label for="cameraX" class="block text-xs font-medium mb-1">
              X
              <HelpTooltip tip="X-coördinaat van de camera positie." />
            </label>
            <input id="cameraX" type="number" step="any" class="input input-bordered w-full" bind:value={cameraX} disabled={!enableCameraPosition} />
          </div>
          <div>
            <label for="cameraY" class="block text-xs font-medium mb-1">
              Y
              <HelpTooltip tip="Y-coördinaat van de camera positie." />
            </label>
            <input id="cameraY" type="number" step="any" class="input input-bordered w-full" bind:value={cameraY} disabled={!enableCameraPosition} />
          </div>
          <div>
            <label for="cameraZ" class="block text-xs font-medium mb-1">
              Z
              <HelpTooltip tip="Z-coördinaat (hoogte) van de camera positie." />
            </label>
            <input id="cameraZ" type="number" step="any" class="input input-bordered w-full" bind:value={cameraZ} disabled={!enableCameraPosition} />
          </div>
        </div>

        <!-- Heading/Pitch/Duration row: empty left, fields right -->
        <div></div>
        <div class="col-span-3 grid grid-cols-3 gap-2">
          <div>
            <label for="cameraHeading" class="block text-xs font-medium mb-1">
              Heading
              <HelpTooltip tip="De richting waarin de camera kijkt (in graden)." />
            </label>
            <input id="cameraHeading" type="number" step="any" class="input input-bordered w-full" bind:value={cameraHeading} disabled={!enableCameraPosition} />
          </div>
          <div>
            <label for="cameraPitch" class="block text-xs font-medium mb-1">
              Pitch
              <HelpTooltip tip="De kantelhoek van de camera (omhoog/omlaag in graden)." />
            </label>
            <input id="cameraPitch" type="number" step="any" class="input input-bordered w-full" bind:value={cameraPitch} disabled={!enableCameraPosition} />
          </div>
          <div>
            <label for="cameraDuration" class="block text-xs font-medium mb-1">
              Duration
              <HelpTooltip tip="De duur van de camera animatie in seconden." />
            </label>
            <input id="cameraDuration" type="number" step="any" class="input input-bordered w-full" bind:value={cameraDuration} disabled={!enableCameraPosition} />
          </div>
        </div>

        <label for="isBackground" class="text-right font-semibold">Is Background:
          <HelpTooltip tip="Ondergrond laag, dit waarde wordt bepaalt door de locatie waarop dit formulier wordt geopend." />
        </label>
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

    {#if type === '3dtiles' && activeTab === 3}
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

    {#if type === 'modelanimation' && activeTab == 5}
      <!-- Model Animation Tab -->
      <div class="grid grid-cols-4 gap-4 items-center">
        <label for="modelUrl" class="pr-4 text-right font-semibold">Model URL:<span class="text-error">*</span></label>
        <input id="modelUrl" class="input input-bordered col-span-3 w-full" bind:value={modelUrl} />

        <label for="orientationKey" class="pr-4 text-right font-semibold">Orientation Key:</label>
        <input id="orientationKey" class="input input-bordered col-span-3 w-full" bind:value={orientationKey} />

        <label for="clampToTerrain" class="pr-4 text-right font-semibold">Clamp To Terrain:</label>
        <input id="clampToTerrain" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={modelClampToTerrain} />

        <label for="timeKeyDate" class="pr-4 text-right font-semibold">Time Key:</label>
        <div class="col-span-3 grid grid-cols-2 gap-2">
          <div>
            <label for="timeKeyDate" class="block text-xs font-medium mb-1">Date<span class="text-error">*</span></label>
            <input id="timeKeyDate" type="date" class="input input-bordered w-full" bind:value={timeKeyDate} />
          </div>
          <div>
            <label for="timeKeyTime" class="block text-xs font-medium mb-1">Time<span class="text-error">*</span></label>
            <input id="timeKeyTime" type="time" step="1" class="input input-bordered w-full" bind:value={timeKeyTime} />
          </div>
        </div>
        <div></div>
        <div class="col-span-3">
          <span class="text-s text-gray-500">Time Key: <code>{timeKey}</code></span>
        </div>
      </div>
    {/if}

    <div class="mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => { modalRef.close(); resetModal(); }}>
        Annuleren
      </button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>