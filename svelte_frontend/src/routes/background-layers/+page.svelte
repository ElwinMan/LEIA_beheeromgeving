<script lang="ts">
  import { onMount } from 'svelte';
  import LayerTable from '$lib/components/tables/LayerTable.svelte';
  import CreateLayerModal from '$lib/components/modals/CreateLayerModal.svelte';
  import type { Layer } from '$lib/types/layer';

  let { data } = $props();
  let isBackgroundPage = true;
  let isLoading = $state(true);
  let layers = $state(data.layers);

  let createModal: CreateLayerModal;

  onMount(() => {
    setTimeout(() => {
      isLoading = false;
    }, 100);
  });

  function handleLayerCreated(event: CustomEvent<Layer>) {
    const newLayer = event.detail;
    if (newLayer.isBackground === isBackgroundPage) {
      layers = [...layers, newLayer];
    }
  }
</script>

<svelte:head>
  <title>LEIA Beheeromgeving – Layers</title>
</svelte:head>

<CreateLayerModal
  bind:this={createModal}
  on:created={handleLayerCreated}
  isBackgroundPage={isBackgroundPage}
/>

<div class="flex justify-between items-center mb-6">
  <div>
    <h1 class="text-3xl font-bold">Layers</h1>
    <p class="text-base-content/70 mt-2">Beheer en bekijk alle beschikbare layers</p>
  </div>
  <button class="btn btn-primary" onclick={() => createModal.showModal()}>
    + Nieuwe Layer
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
