<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createLayer } from '$lib/api';
  import type { Layer } from '$lib/types/layer';
  import PositionSelector from '$lib/components/PositionSelector.svelte';

  import { onMount } from 'svelte';
  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Layer }>();

  // Tab state
  let activeTab = 0;
  const typeOptions = [
    { value: 'wms', label: 'WMS' },
    { value: 'wmts', label: 'WMTS' },
    { value: '3DTiles', label: '3DTiles' }
  ];
  const tabLabels = ['Algemeen'];

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

  export let isBackgroundPage: boolean = false;

  export function showModal() {
    resetForm();
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
    opacity = 1;
    cameraPosition = '';
    isBackground = isBackgroundPage;

    wmsFeatureName = '';
    wmsContentType = '';

    wmtsFeatureName = '';
    wmtsContentType = '';
    wmtsRequestEncoding = '';
    wmtsMatrixIds = '';
    wmtsTileMatrixSetID = '';
    wmtsTileWidth = '';
    wmtsTileHeight = '';
    wmtsMaximumLevel = '';

    tilesShadows = false;
    tilesetHeight = '';
    enableHeightControl = false;
    defaultTheme = '';

    activeTab = 0;
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

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

    try {
      // Set top-level featureName based on type
      let featureName = '';
      if (type === 'wms') featureName = wmsFeatureName;
      else if (type === 'wmts') featureName = wmtsFeatureName;
      // For 3DTiles, leave as empty or set as needed

      const payload = {
        type,
        title,
        url: mainUrl,
        featureName,
        isBackground: isBackgroundPage,
        content
      };
      const newLayer = await createLayer(payload);

      dispatch('created', newLayer);
      modalRef.close();
    } catch (error) {
      console.error('Layer creation failed', error);
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form on:submit|preventDefault={handleSubmit} class="modal-box w-full max-w-4xl">
    <h3 class="mb-4 text-lg font-bold">Nieuwe Layer Aanmaken</h3>
    <!-- Only show tabs if a type is selected -->
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

    <div class="mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>