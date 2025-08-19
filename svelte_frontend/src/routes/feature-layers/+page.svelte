<script lang="ts">
  import { onMount } from 'svelte';
  import LayerTable from '$lib/components/tables/LayerTable.svelte';
  import CreateLayerModal from '$lib/components/modals/CreateLayerModal.svelte';
  import { fetchLayers } from '$lib/api';
  import type { Layer } from '$lib/types/layer';

  interface Data {
    layers: Layer[];
    error: string | null;
  }

  let { data }: { data: Data } = $props();
  let isLoading = $state(true);
  let isBackgroundPage = false;
  let layers = $state([]);

  let createModal: CreateLayerModal;

  async function reloadLayers() {
    isLoading = true;
    try {
      layers = await fetchLayers();
      data.error = null;
    } catch (e) {
      data.error = 'Kon layers niet laden';
    } finally {
      isLoading = false;
    }
  }

  onMount(reloadLayers);
</script>

<svelte:head>
  <title>LEIA Beheeromgeving – Layers</title>
</svelte:head>

<CreateLayerModal
  bind:this={createModal}
  on:created={reloadLayers}
  isBackgroundPage={isBackgroundPage}
/>

<div class="flex justify-between items-center mb-6">
  <div>
    <h1 class="text-3xl font-bold">Feature Layers</h1>
    <p class="text-base-content/70 mt-2">Beheer en bekijk alle beschikbare feature layers</p>
  </div>
  <button
    class="btn btn-primary"
    onclick={() => createModal.showModal()}
  >
    <img src="/icons/plus.svg" alt="Nieuwe laag" class="mr-1 h-4 w-4" />
    Nieuwe Laag aanmaken
  </button>
</div>

{#if isLoading}
  <div class="flex items-center justify-center py-12">
    <span class="loading loading-spinner loading-lg"></span>
    <span class="ml-3">Laden...</span>
  </div>
{:else if data.error}
  <div class="alert alert-error">
    <span>{data.error}</span>
  </div>
{:else}
  <LayerTable
    isBackgroundPage={isBackgroundPage}
  />
{/if}