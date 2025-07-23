<script lang="ts">
  import { onMount } from 'svelte';
  import TerrainProviderTable from '$lib/components/tables/TerrainProviderTable.svelte';
  import CreateTerrainProviderModal from '$lib/components/modals/CreateTerrainProviderModal.svelte';
  import { fetchTerrainProviders } from '$lib/api';
  import type { TerrainProvider } from '$lib/types/tool';

  interface Data {
    terrain_providers: TerrainProvider[];
    error: string | null;
  }

  let { data }: { data: Data } = $props();
  let isLoading = $state(true);
  let createModal: CreateTerrainProviderModal;

  async function reloadTerrainProviders() {
    isLoading = true;
    try {
      data.terrain_providers = await fetchTerrainProviders();
    } catch (e) {
      data.error = 'Kon terrain providers niet laden';
    } finally {
      isLoading = false;
    }
  }

  onMount(reloadTerrainProviders);
</script>

<svelte:head>
  <title>LEIA Beheeromgeving – TerrainProvider</title>
</svelte:head>

<div class="space-y-6">
  <div class="flex justify-between items-center mb-6">
    <div>
      <h1 class="text-3xl font-bold">TerrainProvider</h1>
      <p class="text-base-content/70 mt-2">Beheer en bekijk alle terrain providers</p>
    </div>
    <button class="btn btn-primary" onclick={() => createModal.showModal()}>
      Nieuwe TerrainProvider
    </button>
  </div>

  <CreateTerrainProviderModal bind:this={createModal} on:created={reloadTerrainProviders} />

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
    <TerrainProviderTable />
  {/if}
</div>