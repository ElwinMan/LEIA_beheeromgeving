<script lang="ts">
  import { onMount } from 'svelte';
  import CesiumTable from '$lib/components/tables/CesiumTable.svelte';
  import type { Cesium } from '$lib/types/tool';

  interface Data {
    cesiums: Cesium[];
    error: string | null;
  }

  let { data }: { data: Data } = $props();
  let isLoading = $state(true);

  onMount(() => {
    setTimeout(() => {
      isLoading = false;
    }, 100);
  });
</script>

<svelte:head>
  <title>LEIA Beheeromgeving – Cesium</title>
</svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-3xl font-bold">Cesium</h1>
    <p class="text-base-content/70 mt-2">Beheer en bekijk alle Cesiums</p>
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
    <CesiumTable cesiums={data.cesiums} />
  {/if}
</div>