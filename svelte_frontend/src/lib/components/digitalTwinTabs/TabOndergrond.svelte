<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchLayers, fetchDigitalTwin, bulkUpdateDigitalTwinAssociations } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';
  import type { Layer } from '$lib/types/layer';
  import type { BulkAssociationsPayload, LayerBulkOperation } from '$lib/types/digitalTwinAssociation';

  interface Props {
    digitalTwin: DigitalTwin | null;
    digitalTwinId: string;
  }

  let { digitalTwin, digitalTwinId }: Props = $props();

  let backgroundLayers = $state<Layer[]>([]);
  let selectedLayerIds = $state<Set<number>>(new Set());
  let defaultLayerId = $state<number | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let isSaving = $state(false);
  let saveSuccess = $state(false);
  let associatedLayerIds = $state<Set<number>>(new Set());

  onMount(async () => {
    try {
      const [layers, twin] = await Promise.all([
        fetchLayers(),
        fetchDigitalTwin(digitalTwinId)
      ]);

      // Build associatedLayerIds from the digital twin's layer_associations
      associatedLayerIds = new Set<number>(
        (twin.layer_associations ?? []).map((a: { layer_id: number }) => a.layer_id)
      );

      backgroundLayers = layers.filter((layer: Layer) => layer.isBackground);
      selectedLayerIds = new Set<number>(
        (twin.layer_associations ?? [])
          .filter((a: { group_id: number | null }) => a.group_id === null)
          .map((a: { layer_id: number }) => a.layer_id)
      );
      defaultLayerId =
        (twin.layer_associations ?? []).find((a: { is_default: boolean; group_id: number | null }) =>
          a.is_default && a.group_id === null
        )?.layer_id ?? null;
    } catch (err) {
      error = 'Fout bij laden van ondergrondlagen.';
      console.error(err);
    } finally {
      loading = false;
    }
  });

  function toggleLayer(layerId: number) {
    if (selectedLayerIds.has(layerId)) {
      selectedLayerIds.delete(layerId);
      if (defaultLayerId === layerId) {
        defaultLayerId = null;
      }
    } else {
      selectedLayerIds.add(layerId);
    }
  }

  function setDefaultLayer(layerId: number) {
    defaultLayerId = layerId;
    selectedLayerIds.add(layerId);
  }

  async function saveBackgroundLayers() {
    isSaving = true;
    saveSuccess = false;
    error = null;
    try {
      // Compose bulk payload for background layers
      const layerOperations: LayerBulkOperation[] = backgroundLayers
        .filter(layer => selectedLayerIds.has(layer.id))
        .map(layer => ({
          action: associatedLayerIds.has(layer.id) ? 'update' : 'create',
          layer_id: layer.id,
          is_default: layer.id === defaultLayerId,
          sort_order: 0,
          group_id: null,
          isBackground: true
        }));

      const payload: BulkAssociationsPayload = {
        layer_payload: { operations: layerOperations },
        group_payload: { operations: [] }
      };

      await bulkUpdateDigitalTwinAssociations(digitalTwinId, payload);
      saveSuccess = true;
    } catch (err) {
      error = 'Fout bij opslaan van ondergrondlagen.';
      console.error(err);
    } finally {
      isSaving = false;
      setTimeout(() => (saveSuccess = false), 2000);
    }
  }
</script>

<div class="space-y-6">
  <h2 class="text-2xl font-bold">Ondergrond</h2>
  <p class="text-base-content/70">Beheer Ondergrond voor deze digital twin.</p>

  {#if loading}
    <p>Aan het laden...</p>
  {:else if error}
    <p class="text-error">{error}</p>
  {:else}
    <div class="card bg-base-100 border-base-300 border">
      <div class="card-body space-y-4">
        {#each backgroundLayers as layer}
          <div class="flex items-center justify-between border-b pb-2">
            <div class="flex items-center gap-3">
              <input
                type="checkbox"
                checked={selectedLayerIds.has(layer.id)}
                onchange={() => toggleLayer(layer.id)}
                class="checkbox checkbox-primary"
              />
              <span>{layer.title}</span>
            </div>

            <div>
              <label class="label cursor-pointer flex items-center gap-2">
                <input
                  type="radio"
                  name="default-layer"
                  value={layer.id}
                  checked={defaultLayerId === layer.id}
                  onchange={() => setDefaultLayer(layer.id)}
                  class="radio radio-secondary"
                />
                <span class="text-sm">Standaard</span>
              </label>
            </div>
          </div>
        {/each}
        <div class="flex gap-2 mt-4">
          <button class="btn btn-primary" onclick={saveBackgroundLayers} disabled={isSaving}>
            {#if isSaving}
              <span class="loading loading-spinner loading-xs"></span>
            {:else}
              Opslaan
            {/if}
          </button>
          {#if saveSuccess}
            <span class="text-success">Opgeslagen!</span>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>