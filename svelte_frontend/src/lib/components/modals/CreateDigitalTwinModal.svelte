<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createDigitalTwin, bulkModifyToolAssociations, createViewer, fetchTools, fetchLayers, bulkUpdateDigitalTwinAssociations } from '$lib/api';
  import type { BulkToolOperation } from '$lib/types/digitalTwinAssociation';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type { Tool } from '$lib/types/tool';
  import type { LayerBulkOperation } from '$lib/types/digitalTwinAssociation';
  import type { Layer } from '$lib/types/layer';

  const dispatch = createEventDispatcher<{ created: DigitalTwin }>();

  let modalRef: HTMLDialogElement | null = null;

  // Form fields
  let name = '';
  let title = '';
  let subtitle = '';
  let owner = '';
  let isPrivate = false;

  // List of tool names to associate
  const defaultToolNames = [
    'layerlibrary',
    'layermanager',
    'featureinfo',
    'info',
    'help',
    'bookmarks',
    'cesium',
    'stories',
    'measure',
    'search',
    'geocoder',
    'projects'
  ];

  const defaultLayerTitles = [
    'BRT Achtergrondkaart (WMTS)',
    'Luchtfoto Actueel HR (WMTS)',
    '3D BAG'
  ];

  const defaultViewerContent = {
    logo: "",
    thumbnail: "",
    startPosition: {
      x: 3.62121,
      y: 51.45503,
      z: 3096.9614,
      heading: 360,
      pitch: -34.77193,
      duration: 1.5
    },
    colors: {
        "ui-background": "#ffffff",
        "interactive-01": "#214170",
        "interactive-02": "#171717",
        "interactive-03": "#0062ff",
        "interactive-04": "#0062ff",
        "ui-01": "#f3f3f3",
        "ui-02": "#ffffff",
        "ui-03": "#dcdcdc",
        "ui-04": "#8c8c8c",
        "ui-05": "#171717",
        "text-01": "#171717",
        "text-02": "#565656",
        "text-03": "#8c8c8c",
        "text-04": "#ffffff",
        "link-01": "#0062ff",
        "icon-01": "#171717",
        "icon-02": "#565656",
        "icon-03": "#ffffff",
        "field-01": "#f3f3f3",
        "field-02": "#ffffff",
        "inverse-01": "#ffffff",
        "inverse-02": "#3d3d3d",
        "support-01": "#da1e28",
        "support-02": "#24a148",
        "support-03": "#fdd13a",
        "support-04": "#054ada",
        "inverse-support-01": "#fb4b53",
        "inverse-support-02": "#3dbb61",
        "inverse-support-03": "#fdd13a",
        "inverse-support-04": "#408bfc",
        "overlay-01": "#171717CC",
        "interaction-tokens": "#0062ff",
        "hover-primary": "#376dbc",
        "hover-primary-text": "#054ada",
        "hover-secondary": "#4c4c4c",
        "hover-tertiary": "#4cabd8",
        "hover-ui": "#e5e5e5",
        "hover-selected-ui": "#cacaca",
        "hover-danger": "#ba1b23",
        "hover-row": "#e5e5e5",
        "active-primary": "#376dbc",
        "active-secondary": "#6f6f6f",
        "active-tertiary": "#0530ad",
        "active-ui": "#bebebe",
        "active-danger": "#750e13",
        "selected-ui": "#dcdcdc",
        "highlight": "#C9deff",
        "skeleton-01": "#e5e5e5",
        "skeleton-02": "#bebebe",
        "visited-link": "#0062ff",
        "disabled-01": "#f3f3f3",
        "disabled-02": "#bebebe",
        "disabled-03": "#8c8c8c"
      }
  };

  export function showModal() {
    resetForm();
    modalRef?.showModal();
  }

  function resetForm() {
    name = '';
    title = '';
    subtitle = '';
    owner = '';
    isPrivate = false;
  }

  async function handleSubmit() {
    try {
      const newTwin = await createDigitalTwin({
        name,
        title,
        subtitle,
        owner,
        private: isPrivate,
        last_updated: new Date().toISOString()
      });

      await createViewer(newTwin.id, defaultViewerContent);

      // --- Default Tools ---
      const allTools: Tool[] = await fetchTools();
      const toolIds = allTools
        .filter(tool => defaultToolNames.includes(tool.name))
        .map(tool => tool.id);

      if (toolIds.length > 0) {
        const operations: BulkToolOperation[] = toolIds.map(id => ({
          tool_id: id,
          action: 'create'
        }));
        await bulkModifyToolAssociations(newTwin.id, operations);
      }

      // --- Default Layers ---
      const allLayers: Layer[] = await fetchLayers();
      const defaultLayers = allLayers.filter(layer => defaultLayerTitles.includes(layer.title));
      const layerOperations: LayerBulkOperation[] = defaultLayers.map((layer, idx) => ({
        layer_id: layer.id,
        is_default: true,
        sort_order: idx,
        group_id: null,
        action: 'create'
      }));

      if (layerOperations.length > 0) {
        await bulkUpdateDigitalTwinAssociations(String(newTwin.id), {
          layer_payload: { operations: layerOperations },
          group_payload: { operations: [] }
        });
      }

      dispatch('created', newTwin);
      modalRef?.close();
    } catch (error) {
      console.error('Failed to create digital twin, viewer, tools, or layers', error);
    }
  }
</script>

<dialog bind:this={modalRef} class="modal">
  <form on:submit|preventDefault={handleSubmit} class="modal-box space-y-4">
    <h3 class="text-lg font-bold">Digital Twin Aanmaken</h3>

    <input class="input input-bordered w-full" placeholder="Naam" bind:value={name} required />
    <input class="input input-bordered w-full" placeholder="Titel" bind:value={title} required />
    <input class="input input-bordered w-full" placeholder="Subtitel" bind:value={subtitle} />
    <input class="input input-bordered w-full" placeholder="Eigenaar" bind:value={owner} required />

    <label class="flex items-center gap-2">
      <input type="checkbox" class="checkbox" bind:checked={isPrivate} />
      Privé
    </label>

    <div class="flex justify-end gap-2 pt-4">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef?.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>
