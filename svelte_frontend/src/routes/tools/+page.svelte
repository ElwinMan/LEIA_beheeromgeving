<script lang="ts">
  import { onMount } from 'svelte';
  import ToolTable from '$lib/components/tables/ToolTable.svelte';

  let { data } = $props();
  let isLoading = $state(true);

  onMount(() => {
    setTimeout(() => {
      isLoading = false;
    }, 100);
  });
</script>

<svelte:head>
  <title>LEIA Beheeromgeving – Tools</title>
</svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-3xl font-bold">Tools</h1>
    <p class="text-base-content/70 mt-2">Beheer en bekijk alle beschikbare tools</p>
  </div>

  {#if isLoading}
    <div class="flex items-center justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
      <span class="ml-3">Laden...</span>
    </div>
  {:else if data.error}
    <div class="alert alert-error">
      <svg class="h-6 w-6 shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span>{data.error}</span>
    </div>
  {:else}
    <ToolTable tools={data.tools} />
  {/if}
</div>
