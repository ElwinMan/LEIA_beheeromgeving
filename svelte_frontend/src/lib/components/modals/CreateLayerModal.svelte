<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createLayer } from '$lib/api';
  import type { Layer } from '$lib/types/layer';
  import PositionSelector from '$lib/components/PositionSelector.svelte';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Layer }>();

  // Tab state
  let activeTab = 0;
  const typeOptions = [
    { value: 'wms', label: 'WMS' },
    { value: 'wmts', label: 'WMTS' },
    { value: '3DTiles', label: '3DTiles' },
    { value: 'geojson', label: 'GeoJSON' },
    { value: 'modelanimation', label: 'Model Animation' }
  ];

  let missingFields: string[] = [];

  // Main tab fields
  let title: string = '';
  let type: string = '';
  let mainUrl: string = '';
  let imageUrl: string = '';
  let legendUrl: string = '';
  let defaultAddToManager: boolean = false;
  let attribution: string = '';
  let metadata: string = '';
  let transparent: boolean = false;
  let opacity: number = 100;
  let enableCameraPosition: boolean = false;
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
  let isBackground: boolean = false;

  // WMS tab fields
  let wmsFeatureName: string = '';
  let wmsContentType: string = '';

  // WMTS tab fields
  let wmtsFeatureName: string = '';
  let wmtsContentType: string = '';
  let wmtsMatrixIds: string[] = [];
  let wmtsMatrixIdsText: string = '';
  let wmtsTileMatrixSetID: string = '';
  let wmtsTileWidth: number = 0;
  let wmtsTileHeight: number = 0;
  let wmtsMaximumLevel: number = 0;

  // 3DTiles tab fields
  let tilesShadows: boolean = false;
  let tilesetHeight: number = 0;
  let enableHeightControl: boolean = false;
  let defaultTheme: string = '';
  let style: Record<string, any> = {};
  let styleJson = JSON.stringify(style, null, 2);
  $: styleJson = JSON.stringify(style, null, 2);

  type ThemeCondition = [string, string];
  type ThemeLegendEntry = { color: string; label: string };
  type Theme = {
    title: string;
    conditions: ThemeCondition[];
    legend: ThemeLegendEntry[];
  };
  let themes: Theme[] = [];
  let filter = {
    filterAttribute: '',
    classMapping: {}
  };

  // GeoJSON tab fields
  let geojsonUrl: string = '';
  let geojsonStyle = {
    stroke: '#0000ff',
    strokeWidth: 1,
    fill: '#ff0000'
  };
  let geojsonClampToGround: boolean = true;
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
  let modelClampToTerrain: boolean = false;
  let timeKeyDate: string = '';
  let timeKeyTime: string = '';

  export let isBackgroundPage: boolean = false;

  function resetModal() {
    resetForm();
    missingFields = [];
  }

  export function showModal() {
    resetModal();
    modalRef?.showModal();
  }

  function resetForm() {
    title = '';
    type = '';
    mainUrl = '';
    imageUrl = '';
    legendUrl = '';
    defaultAddToManager = false;
    attribution = '';
    metadata = '';
    transparent = false;
    opacity = 100;
    enableCameraPosition = false;
    cameraX = 0;
    cameraY = 0;
    cameraZ = 0;
    cameraHeading = 0;
    cameraPitch = 0;
    cameraDuration = 1.5;
    isBackground = isBackgroundPage;

    wmsFeatureName = '';
    wmsContentType = '';

    wmtsFeatureName = '';
    wmtsContentType = '';
    wmtsMatrixIds = [];
    wmtsMatrixIdsText = '';
    wmtsTileMatrixSetID = '';
    wmtsTileWidth = 0;
    wmtsTileHeight = 0;
    wmtsMaximumLevel = 0;

    tilesShadows = false;
    tilesetHeight = 0;
    enableHeightControl = false;
    defaultTheme = '';
    style = {};
    themes = [];
    filter = {
      filterAttribute: '',
      classMapping: {}
    };

    geojsonUrl = '';
    geojsonStyle = {
      stroke: '#0000ff',
      strokeWidth: 1,
      fill: '#ff0000'
    };
    geojsonClampToGround = true;
    geojsonExtrude = {
      slider_min: 0,
      slider_max: 10,
      slider_step: 1,
      slider_default: 0,
      slider_label: 'Extrude Height'
    };

    modelUrl = '';
    timeKey = '';
    orientationKey = '';
    modelClampToTerrain = true;
    timeKeyDate = '';
    timeKeyTime = '';

    activeTab = 0;
  }
  
  async function handleSubmit(event: Event) {
    event.preventDefault();
    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) return;

    // Sanitize theme condition input: wrap variable in ${...} if not present
    if (type === '3DTiles' && themes.length > 0) {
      themes = themes.map(theme => ({
        ...theme,
        conditions: theme.conditions.map(([cond, result]) => {
          // If cond does not start with '${' and contain '}', wrap the variable part
          if (!cond.trim().startsWith('${')) {
            // Try to extract variable name before '===' or first space
            const match = cond.match(/^([a-zA-Z0-9_]+)(.*)$/);
            if (match) {
              const variable = match[1];
              const rest = match[2] || '';
              cond = `\${${variable}}${rest}`;
            } else {
              cond = `\${${cond}}`.replace('\u007f', '${').replace('\u007f', '}');
            }
          }
          return [cond, result];
        })
      }));
    }

    // Parse matrixids from textarea
    wmtsMatrixIds = wmtsMatrixIdsText
      .split(/\r?\n/)
      .map(s => s.trim())
      .filter(s => s.length > 0);

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
      '3DTiles': {
        tiles3d: {
          shadows: tilesShadows,
          tilesetHeight,
          enableHeightControl,
          defaultTheme,
          style,
          themes,
          filter
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
      attribution,
      metadata,
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

    try {
      // Set top-level featureName based on type
      let featureName = '';
      if (type === 'wms') featureName = wmsFeatureName;
      else if (type === 'wmts') featureName = wmtsFeatureName;

      // For geojson, use geojsonUrl as main url
      const url = type === 'geojson' ? geojsonUrl : mainUrl;

      const payload = {
        type,
        title,
        url,
        featureName,
        isBackground: isBackgroundPage,
        content,
        last_updated: new Date().toISOString()
      };
      const newLayer = await createLayer(payload);

      dispatch('created', newLayer);
      modalRef.close();
    } catch (error) {
      console.error('Layer creation failed', error);
    }
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
    if (type === 'geojson') {
      fields.push({ label: 'GeoJSON URL', value: geojsonUrl });
    }
    if (type === 'modelanimation') {
      fields.push(
        { label: 'Model URL', value: modelUrl },
        { label: 'Date', value: timeKeyDate },
        { label: 'Time', value: timeKeyTime }
      );
    }

    return fields.filter(f => !f.value || (typeof f.value === 'string' && !f.value.trim())).map(f => f.label);
  }

  // Helper to update timeKey from date and time inputs (used in ModelAnimation Tab)
  $: if (timeKeyDate && timeKeyTime) {
    // Compose ISO string: 'YYYY-MM-DDTHH:mm:ssZ'
    const dt = new Date(timeKeyDate + 'T' + timeKeyTime);
    if (!isNaN(dt.getTime())) {
      // Always output in UTC, with 'Z'
      timeKey = dt.toISOString().replace(/\.\d{3}Z$/, 'Z');
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form onsubmit={handleSubmit} class="modal-box w-full max-w-4xl">
    <div>
      <h3 class="mb-4 text-lg font-bold">Nieuwe Layer Aanmaken</h3>
      <MissingRequiredFields {missingFields} />
    </div>
    <!-- Only show tabs if a type is selected -->
    <div class="tabs tabs-border mb-4" role="tablist">
      <button
        type="button"
        class="tab {activeTab === 0 ? 'tab-active' : ''}"
        role="tab"
        aria-selected={activeTab === 0}
        tabindex={activeTab === 0 ? 0 : -1}
        onclick={() => (activeTab = 0)}
      >Algemeen</button>
      {#if type === 'wms'}
        <button
          type="button"
          class="tab {activeTab === 1 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 1}
          tabindex={activeTab === 1 ? 0 : -1}
          onclick={() => (activeTab = 1)}
        >WMS</button>
      {/if}
      {#if type === 'wmts'}
        <button
          type="button"
          class="tab {activeTab === 2 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 2}
          tabindex={activeTab === 2 ? 0 : -1}
          onclick={() => (activeTab = 2)}
        >WMTS</button>
      {/if}
      {#if type === '3DTiles'}
        <button
          type="button"
          class="tab {activeTab === 3 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 3}
          tabindex={activeTab === 3 ? 0 : -1}
          onclick={() => (activeTab = 3)}
        >3DTiles</button>
      {/if}
      {#if type === 'geojson'}
        <button
          type="button"
          class="tab {activeTab === 4 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 4}
          tabindex={activeTab === 4 ? 0 : -1}
          onclick={() => (activeTab = 4)}
        >GeoJSON</button>
      {/if}
      {#if type === 'modelanimation'}
        <button
          type="button"
          class="tab {activeTab === 5 ? 'tab-active' : ''}"
          role="tab"
          aria-selected={activeTab === 5}
          tabindex={activeTab === 5 ? 0 : -1}
          onclick={() => (activeTab = 5)}
        >Model Animation</button>
      {/if}
    </div>

    {#if activeTab === 0}
      <!-- Algemeen Tab -->
      <div class="grid grid-cols-4 gap-4 items-center">
        <label for="title" class="pr-4 text-right font-semibold">
          Title 
          <span class="text-error">*</span>:
          <HelpTooltip tip="De titel van de laag." />
        </label>
        <input id="title" class="input input-bordered col-span-3 w-full" bind:value={title} />

        <label for="type" class="pr-4 text-right font-semibold">
          Type 
          <span class="text-error">*</span>:
          <HelpTooltip tip="Het type van de laag. Let op! Het type voegt een tabblad toe met specifieke instellingen." />
        </label>
        <select id="type" class="select select-bordered col-span-3 w-full" bind:value={type} >
          <option value="" disabled selected>Kies een type...</option>
          {#each typeOptions as opt}
            <option value={opt.value}>{opt.label}</option>
          {/each}
        </select>

        <label for="mainUrl" class="pr-4 text-right font-semibold">
          URL 
          <span class="text-error">*</span>:
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
          oninput={() => { if (opacity > 100) opacity = 100; if (opacity < 0) opacity = 0; }}
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
            <label for="cameraX" class="block text-xs font-medium mb-1">X</label>
            <input id="cameraX" type="number" step="any" class="input input-bordered w-full" bind:value={cameraX} disabled={!enableCameraPosition} />
          </div>
          <div>
            <label for="cameraY" class="block text-xs font-medium mb-1">Y</label>
            <input id="cameraY" type="number" step="any" class="input input-bordered w-full" bind:value={cameraY} disabled={!enableCameraPosition} />
          </div>
          <div>
            <label for="cameraZ" class="block text-xs font-medium mb-1">Z</label>
            <input id="cameraZ" type="number" step="any" class="input input-bordered w-full" bind:value={cameraZ} disabled={!enableCameraPosition} />
          </div>
        </div>

        <!-- Heading/Pitch/Duration row: empty left, fields right -->
        <div></div>
        <div class="col-span-3 grid grid-cols-3 gap-2">
          <div>
            <label for="cameraHeading" class="block text-xs font-medium mb-1">Heading</label>
            <input id="cameraHeading" type="number" step="any" class="input input-bordered w-full" bind:value={cameraHeading} disabled={!enableCameraPosition} />
          </div>
          <div>
            <label for="cameraPitch" class="block text-xs font-medium mb-1">Pitch</label>
            <input id="cameraPitch" type="number" step="any" class="input input-bordered w-full" bind:value={cameraPitch} disabled={!enableCameraPosition} />
          </div>
          <div>
            <label for="cameraDuration" class="block text-xs font-medium mb-1">Duration</label>
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
        <textarea
          id="wmtsMatrixIds"
          class="textarea textarea-bordered col-span-3 w-full"
          bind:value={wmtsMatrixIdsText}
          rows="5"
          placeholder="One matrix ID per line"
        ></textarea>

        <label for="wmtsTileMatrixSetID" class="pr-4 text-right font-semibold">Tile Matrix Set ID:</label>
        <input id="wmtsTileMatrixSetID" class="input input-bordered col-span-3 w-full" bind:value={wmtsTileMatrixSetID} />

        <label for="wmtsTileWidth" class="pr-4 text-right font-semibold">Tile Width:</label>
        <input id="wmtsTileWidth" type="number" class="input input-bordered col-span-3 w-full" bind:value={wmtsTileWidth} />

        <label for="wmtsTileHeight" class="pr-4 text-right font-semibold">Tile Height:</label>
        <input id="wmtsTileHeight" type="number" class="input input-bordered col-span-3 w-full" bind:value={wmtsTileHeight} />

        <label for="wmtsMaximumLevel" class="pr-4 text-right font-semibold">Maximum Level:</label>
        <input id="wmtsMaximumLevel" type="number" class="input input-bordered col-span-3 w-full" bind:value={wmtsMaximumLevel} />
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

        <label for="style" class="pr-4 text-right font-semibold">Style (JSON):</label>
        <textarea
          id="style"
          class="textarea textarea-bordered col-span-3 w-full"
          rows="6"
          bind:value={styleJson}
          oninput={(e) => {
            const target = e.target as HTMLTextAreaElement | null;
            if (target) {
              try {
                style = JSON.parse(target.value);
              } catch (err) {
              }
            }
          }}
        ></textarea>

        <!-- Themes UI -->
        <div class="col-span-4 mt-4">
          <div class="flex justify-between items-center mb-2">
            <span class="font-semibold">Themes</span>
            <button type="button" class="btn btn-sm btn-primary" onclick={() => themes = [...themes, { title: '', conditions: [], legend: [] }]}>+ Add Theme</button>
          </div>
          {#if themes.length === 0}
            <div class="text-sm text-gray-500">No themes added yet.</div>
          {/if}
          {#each themes as theme, i}
            <div class="border rounded p-3 mb-3 bg-gray-50">
              <div class="flex justify-between items-center mb-2">
                <span class="font-semibold">Theme {i + 1}</span>
                <button type="button" class="btn btn-xs btn-error" onclick={() => themes = themes.filter((_, idx) => idx !== i)}>Remove</button>
              </div>
              <div class="mb-2">
                <label for={`theme-title-${i}`} class="block text-xs font-medium mb-1">Title (unique):</label>
                <input id={`theme-title-${i}`} class="input input-bordered w-full" bind:value={theme.title} placeholder="Theme title" />
              </div>
              <div class="mb-2">
                <label for={`theme-cond-${i}`} class="block text-xs font-medium mb-1">Conditions</label>
                {#each theme.conditions as cond, j}
                  <div class="flex gap-2 mb-1">
                    <input id={`theme-cond-${i}-${j}-0`} class="input input-bordered w-1/2" bind:value={cond[0]} placeholder='e.g. value === "A"' />
                    <input id={`theme-cond-${i}-${j}-1`} class="input input-bordered w-1/2" bind:value={cond[1]} placeholder='e.g. color("#009037")' />
                    <button type="button" class="btn btn-xs btn-error" onclick={() => theme.conditions = theme.conditions.filter((_, idx) => idx !== j)}>Remove</button>
                  </div>
                {/each}
                <button type="button" class="btn btn-xs btn-primary mt-1" onclick={() => theme.conditions = [...theme.conditions, ['', '']]}>+ Add Condition</button>
              </div>
              <div>
                <label for={`theme-legend-${i}`} class="block text-xs font-medium mb-1">Legend</label>
                {#each theme.legend as entry, k}
                  <div class="flex gap-2 mb-1">
                    <input id={`theme-legend-${i}-${k}-color`} class="input input-bordered w-1/2" bind:value={entry.color} placeholder='e.g. #009037' />
                    <input id={`theme-legend-${i}-${k}-label`} class="input input-bordered w-1/2" bind:value={entry.label} placeholder='e.g. A' />
                    <button type="button" class="btn btn-xs btn-error" onclick={() => theme.legend = theme.legend.filter((_, idx) => idx !== k)}>Remove</button>
                  </div>
                {/each}
                <button type="button" class="btn btn-xs btn-primary mt-1" onclick={() => theme.legend = [...theme.legend, { color: '', label: '' }]}>+ Add Legend Entry</button>
              </div>
            </div>
          {/each}
        </div>
        <div>
          <label for="filter-attribute" class="block text-xs font-medium mb-1">Filter Attribute:</label>
          <input id="filter-attribute" class="input input-bordered w-full" bind:value={filter.filterAttribute} placeholder="e.g. Classification" />
        </div>
        <div class="mt-2">
          <label for="filter-classmapping-0" class="block text-xs font-medium mb-1">Class Mapping</label>
          {#each Object.entries(filter.classMapping) as [key, value], idx}
            <div class="flex gap-2 mb-1">
              <input id={`filter-classmapping-${idx}-key`} class="input input-bordered w-1/3" value={key} placeholder='Class value (e.g. 0)'
                oninput={(e) => {
                  const target = e.target as HTMLInputElement | null;
                  if (!target) return;
                  const newKey = target.value;
                  if (newKey !== key) {
                    // Copy mapping, update key
                    const mapping: Record<string, string> = { ...filter.classMapping };
                    mapping[newKey] = mapping[key];
                    delete mapping[key];
                    filter.classMapping = mapping;
                  }
                }} />
              <input id={`filter-classmapping-${idx}-value`} class="input input-bordered w-2/3" value={value}
                placeholder='Class label (e.g. Class 0)'
                oninput={(e) => {
                  const target = e.target as HTMLInputElement | null;
                  if (!target) return;
                  const mapping: Record<string, string> = { ...filter.classMapping };
                  mapping[key] = target.value;
                  filter.classMapping = mapping;
                }} />
              <button type="button" class="btn btn-xs btn-error" onclick={() => {
                const mapping: Record<string, string> = { ...filter.classMapping };
                delete mapping[key];
                filter.classMapping = mapping;
              }}>Remove</button>
            </div>
          {/each}
          <button type="button" class="btn btn-xs btn-primary mt-1" onclick={() => {
            let nextKey = '0';
            const keys = Object.keys(filter.classMapping).map(Number).filter(n => !isNaN(n));
            if (keys.length) {
              nextKey = String(Math.max(...keys) + 1);
            }
            filter.classMapping = { ...filter.classMapping, [nextKey]: '' };
          }}>+ Add Class Mapping</button>
        </div>
      </div>
    {/if}

    {#if type === 'geojson' && activeTab == 4}
      <!-- GeoJSON Tab -->
      <div class="grid grid-cols-4 gap-4 items-center">
        <label for="geojsonUrl" class="pr-4 text-right font-semibold">GeoJSON URL <span class="text-error">*</span>:</label>
        <input id="geojsonUrl" class="input input-bordered col-span-3 w-full" bind:value={geojsonUrl} />

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
        <label for="modelUrl" class="pr-4 text-right font-semibold">Model URL <span class="text-error">*</span>:</label>
        <input id="modelUrl" class="input input-bordered col-span-3 w-full" bind:value={modelUrl} />

        <label for="orientationKey" class="pr-4 text-right font-semibold">Orientation Key:</label>
        <input id="orientationKey" class="input input-bordered col-span-3 w-full" bind:value={orientationKey} />

        <label for="clampToTerrain" class="pr-4 text-right font-semibold">Clamp To Terrain:</label>
        <input id="clampToTerrain" type="checkbox" class="checkbox checkbox-primary col-span-3" bind:checked={modelClampToTerrain} />

        <label for="timeKeyDate" class="pr-4 text-right font-semibold">Time Key:</label>
        <div class="col-span-3 grid grid-cols-2 gap-2">
          <div>
            <label for="timeKeyDate" class="block text-xs font-medium mb-1">Date <span class="text-error">*</span></label>
            <input id="timeKeyDate" type="date" class="input input-bordered w-full" bind:value={timeKeyDate} />
          </div>
          <div>
            <label for="timeKeyTime" class="block text-xs font-medium mb-1">Time <span class="text-error">*</span></label>
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
  <button type="button" class="btn btn-ghost" onclick={() => { modalRef.close(); resetModal(); }}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>