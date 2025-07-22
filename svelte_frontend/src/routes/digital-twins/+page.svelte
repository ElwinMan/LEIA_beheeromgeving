<script lang="ts">
  import { onMount } from 'svelte';
  import DigitalTwinTable from '$lib/components/tables/DigitalTwinTable.svelte';
  import CreateDigitalTwinModal from '$lib/components/modals/CreateDigitalTwinModal.svelte';
  import { fetchDigitalTwins } from '$lib/api';
  import type { DigitalTwin } from '$lib/types/digitalTwin';

  interface Data {
    digitalTwins: DigitalTwin[];
    error: string | null;
  }

  let { data }: { data: Data } = $props();
  let isLoading = $state(true);
  let digitalTwinModalRef: any;

  async function reloadDigitalTwins() {
    isLoading = true;
    try {
      data.digitalTwins = await fetchDigitalTwins();
      data.error = null;
    } catch (e) {
      data.error = 'Kon digital twins niet laden';
    } finally {
      isLoading = false;
    }
  }

  onMount(reloadDigitalTwins);
</script>

<svelte:head>
  <title>LEIA Beheeromgeving – Digital Twins</title>
</svelte:head>

<CreateDigitalTwinModal
  bind:this={digitalTwinModalRef}
  on:created={reloadDigitalTwins}
/>
<div class="flex justify-between items-center mb-6">
  <div>
    <h1 class="text-3xl font-bold">Digital Twins</h1>
    <p class="text-base-content/70 mt-2">Beheer en bekijk alle beschikbare digital twins</p>
  </div>
  <button
    class="btn btn-primary"
    onclick={() => digitalTwinModalRef.showModal()}
  >
    <img src="/icons/plus.svg" alt="Nieuwe twin" class="mr-1 h-4 w-4" />
    Digital Twin aanmaken
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
  <DigitalTwinTable digitalTwins={data.digitalTwins} />
{/if}